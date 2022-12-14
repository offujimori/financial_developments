input int Magic_Number_Trend = 100;
input int Magic_Number_Range = 200;
input double Lots = 0.01;

int Bar_UP;          //NUMERO DE BARRAS COMPRADORAS
int Bar_DOWN;        //NUMERO DE BARRAS VENDEDORAS

int Previous_UP;     //NUMERO ORDENS COMPRADAS ANTERIORMENTE
int Previous_DOWN;   //NUMERO DE ORDENS VENDIDAS ANTERIORMENTE

int TextIndex;
int Comment_UP;
int Comment_DOWN;
string Signal = "";



void Order_Close (int MagicNumber, int OP_Side)
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) == True && OrderMagicNumber() == MagicNumber && OrderType() == OP_Side) 
               {
                  if (OP_Side == OP_BUY)
                     {
                        OrderClose(OrderTicket(), OrderLots(), Bid, 15, clrNONE );
                        break;
                     }
                  if (OP_Side == OP_SELL)
                     {
                        OrderClose(OrderTicket(), OrderLots(), Ask, 15, clrNONE );  
                        break;  
                     }
               }
         }
   }
 
void Order_Breakeven()
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) == True)
               {
                  if (OrderProfit() > 0)
                     {
                        if (OrderType() == OP_BUY)
                           {OrderModify(OrderTicket(),OrderOpenPrice(),OrderOpenPrice()+0.00001,OrderTakeProfit(),0, clrNONE);}
                        if (OrderType() == OP_SELL)
                           {OrderModify(OrderTicket(),OrderOpenPrice(),OrderOpenPrice()-0.00001,OrderTakeProfit(),0, clrNONE);}     
                     }   
                 // if (OrderType() == OP_BUY)
                 //    {UP += 1;}
                 // if (OrderType() == OP_SELL)
                 //    {DOWN += 1;}      
                    
               }
         }    
   }   
   
void Order_Status_ALL()
   {
      string Commentary;
      int UP;              //NUMERO ORDENS COMPRADAS ANTERIORMENTE
      int DOWN;            //NUMETO ORDENS VENDIDAS ANTERIORMENTE
      int Handle;
      
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) == True)
               {
                  if (OrderType() == OP_BUY)
                     {UP += 1;}
                  if (OrderType() == OP_SELL)
                     {DOWN += 1;}                
               }
         }
      
      if (Previous_UP >= Previous_DOWN && UP > DOWN+2 && Signal == "DOWN"|| Previous_UP <= Previous_DOWN && UP > DOWN && Signal == "")
         {
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex),"UP",20);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, White);
            TextIndex++;
            Comment_UP++;
            Signal = "UP";   
            
            Handle = FileOpen("STOPS.csv", FILE_WRITE | FILE_READ | FILE_CSV, "|");
            FileSeek(Handle, 0, SEEK_END);
            FileWrite(Handle, Signal, TimeToString(Time[0], TIME_DATE | TIME_MINUTES), DoubleToString(Close[0], MarketInfo(Symbol(), MODE_DIGITS)));
            FileClose(Handle);       
         }
      if (Previous_UP <= Previous_DOWN && UP+2 < DOWN && Signal == "UP"|| Previous_UP >= Previous_DOWN && UP < DOWN && Signal == "")
         {
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex),"DOWN",20);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, Yellow);
            TextIndex++;
            Comment_DOWN++;
            Signal = "DOWN";
            
            Handle = FileOpen("STOPS.csv", FILE_WRITE | FILE_READ | FILE_CSV, "|");
            FileSeek(Handle, 0, SEEK_END);
            FileWrite(Handle, Signal, TimeToString(Time[0], TIME_DATE | TIME_MINUTES), DoubleToString(Close[0], MarketInfo(Symbol(), MODE_DIGITS)));
            FileClose(Handle);            
         }  
      
      Previous_UP = UP;
      Previous_DOWN = DOWN;    
      
      
      Commentary = "UP Pos: " + UP                       + "\n";
      Commentary = Commentary + "DOWN Pos: " + DOWN      + "\n"; 
      Commentary = Commentary + "\n";
      Commentary = Commentary + "Bar_UP: "   + Bar_UP    + "\n";
      Commentary = Commentary + "Bar_DOWN: " + Bar_DOWN  + "\n";
      Commentary = Commentary + "\n";
      Commentary = Commentary + "Comment_UP: " + Comment_UP + "\n";
      Commentary = Commentary + "Comment_DOWN: " + Comment_DOWN + "\n";
      
      
      Comment(Commentary); 
             
   }


int OnInit()
  {
   FileDelete("STOPS.csv");
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
   
   Order_Status_ALL();
   
   if (Bar_Time != Time[0])
      {
         Order_Breakeven();
         if (Pre_Previous_Close > Pre_Previous_Open)
            {
               if (Previous_Close > Previous_Open) //BOTH CANDLE TREND UP
                  {
                     //Order_Close(Magic_Number_Range, OP_SELL);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Trend,0, clrNONE);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Range,0, clrNONE);
                  }
               if (Previous_Close < Previous_Open)
                  {
                     Order_Close(Magic_Number_Trend, OP_BUY);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Trend,0, clrNONE);
                   //  OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Range,0, clrNONE);
                  } 
            }         
         if (Pre_Previous_Close < Pre_Previous_Open)
            {
               if (Previous_Close < Previous_Open) // BOTH CANDLE TREND DOWN
                  {
                     //Order_Close(Magic_Number_Range, OP_BUY);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Trend,0, clrNONE);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Range,0, clrNONE);
                  }
               if (Previous_Close > Previous_Open)
                  {
                     Order_Close(Magic_Number_Trend, OP_SELL);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Trend);
                    // OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Range);
                  }    
            }
         if (Previous_Close > Previous_Open)
            Bar_UP += 1;
         if (Previous_Close < Previous_Open)
            Bar_DOWN += 1;
         
         Bar_Time = Time[0];   
                                                
      }
  }

