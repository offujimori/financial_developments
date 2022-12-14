input int StopLoss = 100;
input double LotSize = 0.01;

input int SMA_Long = 50;
input int SMA_Short = 20;

input int MagicNumber_Buy = 100;
input int MagicNumber_Sell = 200;
input int MagicNumber_Global = 1;

input double Balance_Start = 10000;
input double Target = 100;
input double Overral_Target = 10;

double Account_Balance = AccountBalance();

double Balance_Buy = Balance_Start;
double Balance_Sell = Balance_Start;

double Equity_Buy = Balance_Buy;
double Equity_Sell = Balance_Sell;

int Positions = 0;
int Tickets_Data[];

void Position_Status (int MagicNumber)
   {
      string Orders_Comment = "BALANCE: " + DoubleToString(AccountBalance(), 2) + " --- " + "EQUITY: " + DoubleToString(AccountEquity(), 2);
      double Buy_PnL = 0;
      double Sell_PnL = 0;
      
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            OrderSelect(O, SELECT_BY_POS, MODE_TRADES);
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
                  
                  string O_Second_Add = DoubleToString(StringToDouble(O_Second)+OrderProfit(), 2);
                  
                  Orders_Comment += "\n" + "STRATEGY: " + O_First + " --- " + "PnL: " + O_Second_Add + " --- " + "ROOT ORDER: " + O_Third + " --- " + "FLIPS: " + O_Fourth;
                  
                  if (OrderType() == OP_BUY)
                     Buy_PnL += StringToDouble(O_Second_Add);
                  if (OrderType() == OP_SELL)
                     Sell_PnL += StringToDouble(O_Second_Add);

               }
            Equity_Buy = Balance_Buy + Buy_PnL;
            Equity_Sell = Balance_Sell + Sell_PnL;                         
               
         }
      Comment(Orders_Comment);
   }
   
void Orders_Flip(int MagicNumber, int ArrayData[])
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
                        
                        string Comment_Send = O_First + "|" + O_Second_Add + "|" + O_Third + "|" + O_Fourth_Add;
                                        
                        if (OrderType() == OP_BUY)
                           NewTicket = OrderSend(NULL, OP_SELL, LotSize, Bid, 5, Bid + StopLoss*Point, 0, Comment_Send, MagicNumber); 
                        else if (OrderType() == OP_SELL)                                                                               
                           NewTicket = OrderSend(NULL, OP_BUY, LotSize, Ask, 5, Bid - StopLoss*Point, 0, Comment_Send, MagicNumber); 
                           
                        ArrayData[T] = NewTicket;
                     }
               }
         }  
   }

void CloseAll(int MagicNumber, string Side)
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
            {
               if (OrderMagicNumber() == MagicNumber)
                  {
                     if (Side == "BUY")
                        {
                           if (OrderType() == OP_BUY)
                              OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, Red );
                           if (OrderType()== OP_BUYSTOP) 
                              OrderDelete( OrderTicket() );
                           if (OrderType()== OP_BUYLIMIT)
                           OrderDelete( OrderTicket() );
                        }
                     if (Side == "SELL")
                        {
                           if (OrderType() == OP_SELL)
                              OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_ASK), 15, Red );
                           if (OrderType()== OP_SELLSTOP)
                              OrderDelete( OrderTicket() );
                           if (OrderType()== OP_SELLLIMIT)
                              OrderDelete( OrderTicket() );
                        }
                  }
            }
                  
   }   

   

void OnTick()
   {
      double Equity = iCustom(Symbol(), PERIOD_CURRENT, "Equity_v7",True,"","","",False,False,False,True,False,False,False,0,25,True,D'2009.08.17 00:00',False,D'2001.01.01 00:00');
      
      static datetime bar_time=0;
      
      double MA_Long_Current = iMA(NULL, 0, SMA_Long, 0, 0, 0, 1);
      double MA_Short_Current = iMA(NULL, 0, SMA_Short, 0, 0, 0, 1);
      double MA_Long_Previous = iMA(NULL, 0, SMA_Long, 0, 0, 0, 2);
      double MA_Short_Previous = iMA(NULL, 0, SMA_Short, 0, 0, 0, 2);
      
      Position_Status(MagicNumber_Global);     
         
      if (AccountEquity() > Account_Balance + Overral_Target)
         {       
             CloseAll(MagicNumber_Global, "BUY");
             CloseAll(MagicNumber_Global, "SELL");              ///DEFINICAO DE ALVO EM EQUITY
             Account_Balance = AccountBalance();   ///DEFINICAO DE ALVO EM EQUITY
             Positions = 0;
             ArrayFree(Tickets_Data);
          }
      
      if(bar_time!=Time[0])
         {
             if (MA_Short_Current > MA_Long_Current && MA_Short_Previous <= MA_Long_Previous)
               {                               
                Positions += 1;
                OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", MagicNumber_Global);  
               }
   
            else if (MA_Short_Current < MA_Long_Current && MA_Short_Previous >= MA_Long_Previous)
               {
                Positions += 1;
                OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Positions + "|" + "0", MagicNumber_Global);  
               }
                
            if (ArrayResize(Tickets_Data, OrdersTotal()) == OrdersTotal())
               {
                  for (int O = OrdersTotal() - 1; O>=0; O--)
                     {
                        if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
                           {
                           Tickets_Data[O] = OrderTicket();
                           }
                        else 
                           Tickets_Data[O] = EMPTY;
                     }
               }  
                    
            bar_time=Time[0];                   
         }      
   }
