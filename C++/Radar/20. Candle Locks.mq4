input int Magic_Number_Trend = 100;
input int Magic_Number_Range = 200;
input double Lots = 0.01;

void Order_Close (int MagicNumber, int OP_Side, int Index)
   {
      //for (int O = OrdersTotal() - 1; O>=0; O--)
      //   {
            if (OrderSelect(Index, SELECT_BY_POS, MODE_TRADES) == True && OrderMagicNumber() == MagicNumber && OrderType() == OP_Side) 
               {
                  if (OP_Side == OP_BUY)
                     OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, Red );
                  if (OP_Side == OP_SELL)
                     OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 15, Red );    
               }
      //   }
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
   
   double Previous_Close = iClose(Symbol(), PERIOD_CURRENT, 1);
   double Previous_Open = iOpen(Symbol(), PERIOD_CURRENT, 1);
   
   if (Bar_Time != Time[0])
      {
         if (Pre_Previous_Close > Pre_Previous_Open)
            {
               if (Previous_Close > Previous_Open) //BOTH CANDLE TREND UP
                  {
                     Order_Close(Magic_Number_Range, OP_SELL, 0);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Trend);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Range);
                  }
               if (Previous_Close < Previous_Open)
                  {
                     Order_Close(Magic_Number_Trend, OP_BUY, 0);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Trend);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Range);
                  } 
            }         
         if (Pre_Previous_Close < Pre_Previous_Open)
            {
               if (Previous_Close < Previous_Open) // BOTH CANDLE TREND DOWN
                  {
                     Order_Close(Magic_Number_Range, OP_BUY, 0);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Trend);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Range);
                  }
               if (Previous_Close > Previous_Open)
                  {
                     Order_Close(Magic_Number_Trend, OP_SELL, 0);
                     OrderSend(Symbol(), OP_BUY, Lots, Ask, 5, 0, 0, "", Magic_Number_Trend);
                     OrderSend(Symbol(), OP_SELL, Lots, Bid, 5, 0, 0, "", Magic_Number_Range);
                  }    
            }                 
      }
   

   
  }

