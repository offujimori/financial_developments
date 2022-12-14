input int MagicNumber_Buy = 100;
input int MagicNumber_Sell = 200;
input double Target = 100;
input double Overral_Target = 10;
input double LotSize = 0.01;

input int MA_Long_Period = 50;
input int MA_Short_Period = 20;

input double Balance_Start = 10000;

double Balance_Buy = Balance_Start;
double Balance_Sell = Balance_Start;

double Account_Balance = AccountBalance();

double Equity_Buy = Balance_Buy;
double Equity_Sell = Balance_Sell;

int Buy_Positions = 0;
int Sell_Positions = 0;

void Position_Status(int MagicNumber, string Side)
   {
      //Orders Data -> Range/Trend [Range/Trend] + "|" + PnL + "|" + RootOrder + "|" + Flips
      double Side_PnL = 0;
      
      for (int O = OrdersTotal() - 1; O>= 0; O--)
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
                  
                  Side_PnL += StringToDouble(O_Second_Add);            
               }
         }
         
      if (Side == "BUY")
         Equity_Buy = Balance_Buy + Side_PnL;
      if (Side == "SELL")
         Equity_Sell = Balance_Sell + Side_PnL;        
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
   
void Close1_1 (int MagicNumber)
   {
            for (int O = OrdersTotal() - 1; O>=0; O--)
               {
               if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
                  {
                     if (OrderMagicNumber () == MagicNumber)
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
                        break;
                        }
                  }  
               }
   }
 
  
void OnTick()
   {  
      double Equity = iCustom(Symbol(), PERIOD_CURRENT, "Equity_v7",True,"","","",False,False,False,True,False,False,False,0,25,True,D'2009.08.17 00:00',False,D'2001.01.01 00:00');
      
      static datetime bar_time=0;
   
      double MA_Long_Current = iMA(NULL, 0, MA_Long_Period, 0, 0, 0, 1);
      double MA_Short_Current = iMA(NULL, 0, MA_Short_Period, 0, 0, 0, 1);
      double MA_Long_Previous = iMA(NULL, 0, MA_Long_Period, 0, 0, 0, 2);
      double MA_Short_Previous = iMA(NULL, 0, MA_Short_Period, 0, 0, 0, 2);
      
      Position_Status(MagicNumber_Buy, "BUY");
      Position_Status(MagicNumber_Sell, "SELL");
      
  //    if (Equity_Buy > Balance_Buy + Target)
  //       {
  //          CloseAll(MagicNumber_Buy);
  //          Balance_Buy = Equity_Buy;
  //          Buy_Positions = 0;
  //       }
      
  //    if (Equity_Sell > Balance_Sell + Target)
  //       {
  //          CloseAll(MagicNumber_Sell);
  //          Balance_Sell = Equity_Sell;
  //          Sell_Positions = 0;
  //       }
         
      if (AccountEquity() > Account_Balance + Overral_Target)
         {       
             CloseAll(MagicNumber_Buy);             ///DEFINICAO DE ALVO EM EQUITY
             CloseAll(MagicNumber_Sell);           ///DEFINICAO DE ALVO EM EQUITY
             Account_Balance = AccountBalance();   ///DEFINICAO DE ALVO EM EQUITY
             Buy_Positions = 0;
             Sell_Positions = 0;
          }
      
      if(bar_time!=Time[0])
         {
                      if (MA_Short_Current > MA_Long_Current && MA_Short_Previous <= MA_Long_Previous)
                        {
                           if (Equity_Buy > Balance_Buy + Target)// && Previous_Close < Pre_Previous_Close)
                              {
                                Close1_1(MagicNumber_Buy);
                                Balance_Buy = Equity_Buy;
                                 
                               //  Close1_1(MagicNumber_Sell);
                               //  Balance_Sell = Equity_Sell;
                               //  OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                                 
                                // OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                                 Buy_Positions = 0;
                              }
                       //     if (Equity_Sell > Balance_Sell + Target)// && Previous_Close > Pre_Previous_Close)
                       //       {
                             // Close1_1(MagicNumber_Sell);
                             // Balance_Sell = Equity_Sell;
                              
                       //       Close1_1(MagicNumber_Buy);
                       //       Balance_Buy = Equity_Buy;
                       //       OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                              
                             // OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                       //       Sell_Positions = 0;
                       //       }
                              
                              
                            Buy_Positions += 1;
                            OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                            //OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);  // NoStop

                        }
            
                     else if (MA_Short_Current < MA_Long_Current && MA_Short_Previous >= MA_Long_Previous)
                        {
                           if (Equity_Sell > Balance_Sell + Target)// && Previous_Close > Pre_Previous_Close)
                              {
                              Close1_1(MagicNumber_Sell);
                              Balance_Sell = Equity_Sell;
                              
                             // Close1_1(MagicNumber_Buy);
                             // Balance_Buy = Equity_Buy;
                             // OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                              
                             // OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                         //     Sell_Positions = 0;
                              }
                            //  if (Equity_Buy > Balance_Buy + Target)// && Previous_Close < Pre_Previous_Close)
                            //  {
                              //  Close1_1(MagicNumber_Buy);
                              //  Balance_Buy = Equity_Buy;
                                 
                              //   Close1_1(MagicNumber_Sell);
                              //   Balance_Sell = Equity_Sell;
                             //    OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                                 
                                // OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                            //     Buy_Positions = 0;
                            //  }


                             Sell_Positions += 1;
                             OrderSend(NULL, OP_BUY, LotSize, Ask, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                             //OrderSend(NULL, OP_SELL, LotSize, Bid, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);   // NoStop
                        }      
                  }      
            bar_time=Time[0];
         }                    
   