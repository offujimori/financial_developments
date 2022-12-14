input int Magic_Number_Trend = 100;
input int Magic_Number_Range = 200;
input int StopLoss = 300;
input int Entrance = 300;
input double Lots = 0.01;

// NOTES: ORDER FLIP STOP LOSSES ON/OFF ; ORDER SEND STOP LOSS ON/OFF ; ORDER CLOSE ONLY UNPROFITABLE ON/OFF

int Positions;
int Tickets_Data[];

double Previous_Balance = AccountBalance();
double Previous_Drawdown = 0;

void Order_Send()
   {
      string File_Array[];
      int Handle = FileOpen("STOPS.csv", FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, "|");
      
      if (Handle != INVALID_HANDLE)
         {
         int X = 0;
         FileSeek(Handle, 0, SEEK_SET);
         while (!FileIsEnding(Handle))
            {
             string  String1 = FileReadString(Handle);
             string  String2 = FileReadString(Handle);
             string  String3 = FileReadString(Handle);
             string String4 = String1 + "|" + String2 + "|" +  String3;
             
             ArrayResize(File_Array, X+1);
             File_Array[X] = String4;
             X++;
            }
         FileClose(Handle);  
         }
 
      int N = ArraySize(File_Array);
      
      string Order_Read = File_Array[0];
      int Order_iFirst  = StringFind(Order_Read, "|");
      int Order_iSecond = StringFind(Order_Read, "|", Order_iFirst + 1);
                           
      string Order_First  = StringSubstr(Order_Read, 0, Order_iFirst);
      string Order_Second = StringSubstr(Order_Read, Order_iFirst + 1, Order_iSecond - Order_iFirst - 1);
      double Order_Third  = StringSubstr(Order_Read, Order_iSecond + 1);        
      
      if (TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES) == Order_Second)
         {
            string Text;
            if (Order_First == "DOWN")
            {
               Order_Close_Pending(Magic_Number_Trend);
               Positions ++;
               //OrderSend(Symbol(), OP_SELLSTOP, Lots, (Bid - Entrance*Point) , 5, (Bid - Entrance*Point) + StopLoss*Point , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend);
               //OrderSend(Symbol(), OP_SELL, Lots, Bid , 5, Bid + StopLoss*Point , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend); // NO OFFSET
               OrderSend(Symbol(), OP_SELL, Lots, Bid , 5, 0 , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend); // NO OFFSET NO SL
               FileDelete("STOPS.csv", FILE_COMMON);
               Handle = FileOpen("STOPS.csv", FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, "|");
               for (int A = 1; A <= ArraySize(File_Array) - 1; A++)
                  {
                     FileSeek(Handle, 0, SEEK_END);
                     Text = File_Array[A];
                     FileWrite(Handle, Text);
                     FileFlush(Handle);
                  }  
               FileClose(Handle);
               Array_Resize();
               Order_Close(Magic_Number_Trend, OP_BUY);
            }
         if (Order_First == "UP")
            {
               Order_Close_Pending(Magic_Number_Trend);
               Positions ++; 
               //OrderSend(Symbol(), OP_BUYSTOP, Lots, (Bid + Entrance*Point), 5, (Bid + Entrance*Point) - StopLoss*Point , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend); 
               //OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, Bid - StopLoss*Point , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend); // NO OFFSET
               OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0 , 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", Magic_Number_Trend); // NO OFFSET NO SL
               FileDelete("STOPS.csv", FILE_COMMON);
               Handle = FileOpen("STOPS.csv", FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, "|");
               for (int B = 1; B <= ArraySize(File_Array) - 1; B++)
                  {
                     FileSeek(Handle, 0, SEEK_END);
                     Text = File_Array[B];
                     FileWrite(Handle, Text);
                     FileFlush(Handle);
                  }  
               FileClose(Handle);
               Array_Resize();
               Order_Close(Magic_Number_Trend, OP_SELL);
            }  
         }
      }

void Order_Flip(int MagicNumber, int ArrayData[])
   {
      for (int T = ArraySize(ArrayData) - 1; T>= 0; T--)
         {
            int Ticket = ArrayData[T];
            if (Ticket > 0 && OrderSelect (Ticket, SELECT_BY_TICKET, MODE_HISTORY)== True)
               {
                  if (OrderMagicNumber() == MagicNumber && OrderCloseTime() > 0)
                     {
                        int NewTicket;
                        string O_Comment = OrderComment();
                  
                        int O_iFirst  = StringFind(O_Comment, "|");
                        int O_iSecond = StringFind(O_Comment, "|", O_iFirst + 1);
                        int O_iThird = StringFind(O_Comment, "|", O_iSecond + 1);
                        
                        string O_First  = StringSubstr(O_Comment, 0, O_iFirst);
                        string O_Second = StringSubstr(O_Comment, O_iFirst + 1, O_iSecond - O_iFirst - 1);
                        string O_Third  = StringSubstr(O_Comment, O_iSecond + 1, O_iThird - O_iSecond -1);
                        string O_Fourth = StringSubstr(O_Comment, O_iThird +1);
                        
                        string O_Second_Add = DoubleToString(StringToDouble(O_Second)+OrderProfit(), 2);    //Cumulated PnL added
                        string O_Fourth_Add = IntegerToString(StringToInteger(O_Fourth)+1);                 //Flip Quantity Added
                        
                        double OpenPrice = OrderOpenPrice();
                        double ClosePrice = OrderClosePrice();
                        
                        string Comment_Send = O_First + "|" + O_Second_Add + "|" + O_Third + "|" + O_Fourth_Add; 
                           
                        if (OrderType() == OP_BUY)                                                                                        //OPTIONAL
                           //NewTicket = OrderSend(NULL, OP_SELL, Lots, Bid, 5, Bid + StopLoss*Point, 0, Comment_Send, MagicNumber);        //
                           NewTicket = OrderSend(NULL, OP_SELL, Lots, Bid, 5, 0, 0, Comment_Send, MagicNumber);                           //
                        else if (OrderType() == OP_SELL)                                                                                  //
                           //NewTicket = OrderSend(NULL, OP_BUY, Lots, Ask, 5,  Bid - StopLoss*Point, 0, Comment_Send, MagicNumber);        //
                           NewTicket = OrderSend(NULL, OP_BUY, Lots, Ask, 5,  0, 0, Comment_Send, MagicNumber);                           //
                           
                        ArrayData[T] = NewTicket;
                     }
               }
         }  
   }

void Order_Position_Comment (int MagicNumber)
   {
      //Orders Data -> Range/Trend [Range/Trend] + "|" + PnL + "|" + RootOrder + "|" + Flips
      int    Orders_Total = OrdersTotal();
      string Orders_Comment = "BALANCE: " + DoubleToString(AccountBalance(), 2) + " --- " + "EQUITY: " + DoubleToString(AccountEquity(), 2);
      
      
      for (int O = Orders_Total - 1; O>=0; O--)
         {
            OrderSelect (O, SELECT_BY_POS, MODE_TRADES);
            if (OrderMagicNumber() == MagicNumber)
               {
                  string O_Comment = OrderComment();
                  
                  int O_iFirst  = StringFind(O_Comment, "|");
                  int O_iSecond = StringFind(O_Comment, "|", O_iFirst + 1);
                  int O_iThird = StringFind(O_Comment, "|", O_iSecond + 1);
                  
                  string O_First  = StringSubstr(O_Comment, 0, O_iFirst);
                  string O_Second = StringSubstr(O_Comment, O_iFirst + 1, O_iSecond - O_iFirst - 1);
                  string O_Third  = StringSubstr(O_Comment, O_iSecond + 1, O_iThird - O_iSecond -1);
                  string O_Fourth = StringSubstr(O_Comment, O_iThird +1);
                  
                  string O_Second_Add = DoubleToString(StringToDouble(O_Second)+OrderProfit(), 2);      //PnL cumulated ADDED
                  
                  Orders_Comment += "\n" + "STRATEGY: " + O_First + " --- " + "PnL: " + O_Second_Add + " --- " + "ROOT ORDER: " + O_Third + " --- " + "FLIPS: " + O_Fourth;
                  
                //  if (OrderProfit() > 5)
                //     {
                //        if (OrderType() == OP_BUY)
                //           {
                //           OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, Red );
                //           Array_Resize();
                //           }
                //        if (OrderType() == OP_SELL)
                //           {
                //           OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 15, Red );
                //          Array_Resize();
                //           }          
                //     }
               }
         }  
      Comment(Orders_Comment);
   }

void Array_Resize()  
   {
      if (ArrayResize(Tickets_Data, OrdersTotal()) == OrdersTotal())
         {
            for (int i = OrdersTotal() - 1; i>=0; i--)
               {
                  if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
                     {
                     Tickets_Data[i] = OrderTicket();
                     }
                  else 
                     Tickets_Data[i] = EMPTY;     
              }
         }
   }
   

void Order_Close (int MagicNumber, int OP_Side)
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) == True && OrderMagicNumber() == MagicNumber && OrderType() == OP_Side) // && OrderProfit() < 0) //CLOSE ONLY UNPROFITABLE OPTION
               {
                  if (OP_Side == OP_BUY)
                     {
                        OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, clrNONE );
                        //break; // TO CLOSE 1
                     }
                  if (OP_Side == OP_SELL)
                     {
                        OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 15, clrNONE );  
                        //break;  // TO CLOSE 1
                     }
               }
         }
   }
   
void Order_Close_All(int MagicNumber)
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
            {
               if (OrderMagicNumber() == MagicNumber)
                  {
                     if (OrderType() == OP_BUY)
                        OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, Red );
                     if (OrderType() == OP_SELL)
                        OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 15, Red );
                     if (OrderType()== OP_BUYSTOP) 
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_SELLSTOP)
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_BUYLIMIT)
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_SELLLIMIT)
                        OrderDelete( OrderTicket() );
                  }
            }
                  
   }
   
void Order_Close_Pending(int MagicNumber)
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
            {
               if (OrderMagicNumber() == MagicNumber)
                  {
                     if (OrderType()== OP_BUYSTOP) 
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_SELLSTOP)
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_BUYLIMIT)
                        OrderDelete( OrderTicket() );
                     if (OrderType()== OP_SELLLIMIT)
                        OrderDelete( OrderTicket() );
                  }
            }
   }
   
   
int OnInit()
  {
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  { 
  }

void OnTick()
  {
   double Equity = iCustom(Symbol(), PERIOD_CURRENT, "Equity_v7",True,"","","",False,False,False,True,False,False,False,0,25,True,D'2009.08.17 00:00',False,D'2001.01.01 00:00');
   
   static datetime Bar_Time = 0;
   
   double Pre_Previous_Close = iClose(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_Open = iOpen(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_High = iHigh(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_Low = iLow(Symbol(), PERIOD_CURRENT, 2);
   
   double Previous_Close = iClose(Symbol(), PERIOD_CURRENT, 1);
   double Previous_Open = iOpen(Symbol(), PERIOD_CURRENT, 1);
   double Previous_High = iHigh(Symbol(), PERIOD_CURRENT, 1);
   double Previous_Low = iLow(Symbol(), PERIOD_CURRENT, 1);
   
   //Order_Send(); // PARA DATA EM TICKS
   //Order_Flip(Magic_Number_Trend, Tickets_Data); // PARA DATA EM TICKS
   Order_Position_Comment(Magic_Number_Trend);
   
   if (Bar_Time != Time[0])
      {        
         Order_Send(); // PARA DATA EM OPENS
         Order_Flip(Magic_Number_Trend, Tickets_Data); // PARA DATA EM OPENS
         Bar_Time = Time[0];   
                                                
      }
      
  // if (AccountEquity() < Previous_Balance)
  //    {
  //       double Drawdown = MathAbs(Previous_Balance - AccountEquity());
  //       if (Drawdown > Previous_Drawdown) 
  //          {
  //            Previous_Drawdown = Drawdown;
  //          }    
  //    }
      
  // if (AccountEquity() >= Previous_Balance+Previous_Drawdown)  ///DEFINICAO DE ALVO EM EQUITY
  //    {       
  //     Order_Close_All(Magic_Number_Trend);                ///DEFINICAO DE ALVO EM EQUITY
  //     ArrayFree(Tickets_Data);         ///DEFINICAO DE ALVO EM EQUITY
  //     Previous_Balance = AccountBalance();   ///DEFINICAO DE ALVO EM EQUITY
  //     Previous_Drawdown = 0;
  //    }   
   
   Sleep(7000);
  }

