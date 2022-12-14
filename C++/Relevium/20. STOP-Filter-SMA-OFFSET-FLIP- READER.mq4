input int StopLoss = 300;
input int Balance_Target = 15;
input int Magic_Number = 100;

input int MA_Long_Period = 50;
input int MA_Short_Period = 20;
extern double LotSize = 0.01;
input int Entrance = 100;

int Trend_Tickets_Data[];     //ID Tickets vigentes
int Trend_Positions = 1;      //ID posições já abertas
int Trend_OrdersTotal;        //Count posições atuais.

int Flips;

double Previous_Balance = 0;

void Orders_Close_MagicNumbers (int MagicNumber)
   {
      int Orders_Total = OrdersTotal();
      
      for (int O = Orders_Total - 1; O>=0; O--)
         {
            OrderSelect(O, SELECT_BY_POS, MODE_TRADES);
               if (OrderMagicNumber() == MagicNumber)
                  {
                     if (OrderType() == OP_BUY)
                        OrderClose(OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 3);
                     if (OrderType() == OP_SELL)
                        OrderClose(OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 3);
                  }
         }
   }

void Orders_Position_Comment (int MagicNumber)
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
               }
         }  
      Comment(Orders_Comment);
   }
   
void Trend_Orders_Flip(int MagicNumber, int ArrayData[])
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
                           
                        
                        if (OrderType() == OP_BUY)
                          // NewTicket = OrderSend(NULL, OP_BUYSTOP, LotSize, OpenPrice, 5, OpenPrice - StopLoss*Point, 0, Comment_Send, MagicNumber);
                           NewTicket = OrderSend(NULL, OP_SELL, LotSize, Bid,5, Bid + StopLoss*Point, 0, Comment_Send, MagicNumber);
                        else if (OrderType() == OP_SELL)                                                                               
                         //  NewTicket = OrderSend(NULL, OP_SELLSTOP, LotSize, OpenPrice, 5, OpenPrice + StopLoss*Point, 0, Comment_Send, MagicNumber); 
                           NewTicket = OrderSend(NULL, OP_BUY, LotSize, Ask,5, Bid - StopLoss*Point, 0, Comment_Send, MagicNumber);
                           
                        ArrayData[T] = NewTicket;
                     }
               }
         }  
   }
   
   
int Orders_Total_Update(int MagicNumber)
   {
      int Orders_Total;
      for (int O = OrdersTotal() - 1; O>=0; O--)
         if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
            {
               if (OrderMagicNumber() == MagicNumber)
                  Orders_Total += 1;
            }
      return (Orders_Total);
   }
   
void CloseAll(int MagicNumber)
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
   
void ClosePending(int MagicNumber)
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
   
   Orders_Position_Comment(Magic_Number);
   Trend_Orders_Flip(Magic_Number, Trend_Tickets_Data); // FLIPPER FUNCTION
   string File_Array[];
   
   int Handle = FileOpen("STOPS.csv", FILE_READ | FILE_WRITE | FILE_CSV, "|");
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
   Print(N);  
   
   string Order_Read = File_Array[0];
   int Order_iFirst  = StringFind(Order_Read, "|");
   int Order_iSecond = StringFind(Order_Read, "|", Order_iFirst + 1);
                        
   int Order_First  = StringSubstr(Order_Read, 0, Order_iFirst);
   string Order_Second = StringSubstr(Order_Read, Order_iFirst + 1, Order_iSecond - Order_iFirst - 1);
   double Order_Third  = StringSubstr(Order_Read, Order_iSecond + 1);

   
   if (TimeToString(TimeCurrent(), TIME_DATE|TIME_MINUTES) == Order_Second)
      {
         string Text;       
         if (Order_First == 0)
            {
               
               Trend_Positions ++;
               OrderSend(Symbol(), OP_SELL, LotSize, Bid, 5, Bid + StopLoss*Point, 0, "TREND" + "|" + "0" + "|" + Trend_Positions + "|" + "0", Magic_Number);
               FileDelete("STOPS.csv");
               Handle = FileOpen("STOPS.csv", FILE_READ | FILE_WRITE | FILE_CSV, "|");
               for (int A = 1; A <= ArraySize(File_Array) - 1; A++)
                  {
                     FileSeek(Handle, 0, SEEK_END);
                     Text = File_Array[A];
                     FileWrite(Handle, Text);
                     FileFlush(Handle);
                  }  
               FileClose(Handle);
            }
         if (Order_First == 1)
            {
               Trend_Positions ++; 
               OrderSend(Symbol(), OP_BUY, LotSize, Ask, 5, Bid - StopLoss*Point, 0, "TREND" + "|" + "0" + "|" + Trend_Positions + "|" + "0", Magic_Number); 
               FileDelete("STOPS.csv");
               Handle = FileOpen("STOPS.csv", FILE_READ | FILE_WRITE | FILE_TXT, "|");
               for (int B = 1; B <= ArraySize(File_Array) - 1; B++)
                  {
                     FileSeek(Handle, 0, SEEK_END);
                     Text = File_Array[B];
                     FileWrite(Handle, Text);
                     FileFlush(Handle);
                  }  
               FileClose(Handle);
            }
         Trend_OrdersTotal = Orders_Total_Update(Magic_Number);
         if (ArrayResize(Trend_Tickets_Data, Trend_OrdersTotal) == Trend_OrdersTotal)
                  {
                     for (int i = Trend_OrdersTotal - 1; i>=0; i--)
                        {
                           if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
                              {
                              Trend_Tickets_Data[i] = OrderTicket();
                              }
                           else 
                              Trend_Tickets_Data[i] = EMPTY;     
                       }
                  }
      }
   
   Orders_Position_Comment(Magic_Number);
   if (AccountEquity() >= Previous_Balance+Balance_Target)  ///DEFINICAO DE ALVO EM EQUITY
      {       
          CloseAll(Magic_Number);                ///DEFINICAO DE ALVO EM EQUITY
          ArrayFree(Trend_Tickets_Data);         ///DEFINICAO DE ALVO EM EQUITY
          Previous_Balance = AccountBalance();   ///DEFINICAO DE ALVO EM EQUITY
     }
  }