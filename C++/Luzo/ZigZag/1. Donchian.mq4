input int ChannelPeriod = 20;
input double LotSize = 0.01;
input int StopLoss = 100;
input int TakeProfit = 100;
input double Target = 100;
input double Overral_Target = 10;

int MagicNumber_Buy = 100;
int MagicNumber_Sell = 200;
double Balance_Start = 10000;

double Balance_Buy = Balance_Start;
double Balance_Sell = Balance_Start;

double Account_Balance = AccountBalance();

double Equity_Buy = Balance_Buy;
double Equity_Sell = Balance_Sell;

int Buy_Positions = 0;
int Sell_Positions = 0;

bool Sell_Close = True;
bool Buy_Close = True;

  
void Orders_Pending_Delete()
{
   for(int i=0;i<OrdersTotal();i++){
     OrderSelect(i,SELECT_BY_POS,MODE_TRADES);
     if(OrderSymbol()==Symbol() && ((OrderType()==OP_BUYSTOP) || (OrderType()==OP_SELLSTOP) || (OrderType()==OP_BUYLIMIT) || (OrderType()==OP_SELLLIMIT)))
     {
       OrderDelete(OrderTicket());
     }   
   }
}

   double Donchian_Current_HIGH = NULL;
   double Donchian_Current_MID = NULL;
   double Donchian_Current_LOW = NULL;
   
   
   double Donchian_Previous_HIGH = NULL;
   double Donchian_Previous_MID = NULL;
   double Donchian_Previous_LOW = NULL;
   
   string Signal = NULL;
   static datetime bar_time=0;
   
   
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
      bool Cycle = True;
      while (Cycle == True)
         {
            for (int O = OrdersTotal() - 1; O>=0; O--)
               {
               if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES))
                  {
                     if (OrderMagicNumber () == MagicNumber && OrderType() == OP_BUY || OrderType() == OP_SELL)
                        {
                        if (OrderType() == OP_BUY)
                           OrderClose( OrderTicket(), OrderLots(), MarketInfo(OrderSymbol(), MODE_BID), 15, Red );
                        if (OrderType() == OP_SELL)
                        Cycle = False;
                        break;
                        }
                  }
               }
         }
   }   
   

void OnTick()
  {
   double Equity = iCustom(Symbol(), PERIOD_CURRENT, "Equity_v7",True,"","","",False,False,False,True,False,False,False,0,25,True,D'2009.08.17 00:00',False,D'2001.01.01 00:00');
   string Orders_Comment = "BALANCE: " + DoubleToString(AccountBalance(), 2) + " --- " + "EQUITY: " + DoubleToString(AccountEquity(), 2);
   Comment(Orders_Comment);
  
   double Donchian_HIGH = iCustom(Symbol(), PERIOD_CURRENT, "DonchianChannels", ChannelPeriod, 0,0);  
   double Donchian_MID = iCustom(Symbol(), PERIOD_CURRENT, "DonchianChannels", ChannelPeriod, 1,0); 
   double Donchian_LOW = iCustom(Symbol(), PERIOD_CURRENT, "DonchianChannels", ChannelPeriod, 2,0);
   
   double SAR = iSAR(Symbol(), PERIOD_CURRENT, 0.02, 0.2, 0);

   
   double Previous_Close = iClose(Symbol(), 0, 1);
   double Pre_Previous_Close = iClose(Symbol(), 0, 2);
   
   //ORDERS - START  
   
   Position_Status(MagicNumber_Buy, "BUY");
   Position_Status(MagicNumber_Sell, "SELL");
   
//   if (Equity_Buy > Balance_Buy + Target && Buy_Close == True)
//   {
//      CloseAll(MagicNumber_Buy);
//      Balance_Buy = Equity_Buy;
      //CloseAll(MagicNumber_Sell);
     // Balance_Sell = Equity_Sell;
//      Buy_Positions = 0;
//      Buy_Close = False;
//      Sell_Close = True;
//   }

//   if (Equity_Sell > Balance_Sell + Target && Sell_Close == True)
//      {
//         CloseAll(MagicNumber_Sell);
//         Balance_Sell = Equity_Sell;
        // CloseAll(MagicNumber_Buy);
       //  Balance_Buy = Equity_Buy;
//         Sell_Positions = 0;
//         Sell_Close = False;
//         Buy_Close = True;
//      }
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
            bar_time=Time[0];
            
            if (Equity_Buy > Balance_Buy + Target && Previous_Close > Pre_Previous_Close)
               {
                  Close1_1(MagicNumber_Buy);
                  Balance_Buy = Equity_Buy;
                  //CloseAll(MagicNumber_Sell);
                 // Balance_Sell = Equity_Sell;
                  Buy_Positions = 0;

               }
            
            if (Equity_Sell > Balance_Sell + Target && Previous_Close < Pre_Previous_Close)
               {
                  Close1_1(MagicNumber_Sell);
                  Balance_Sell = Equity_Sell;
                 // CloseAll(MagicNumber_Buy);
                //  Balance_Buy = Equity_Buy;
                  Sell_Positions = 0;

               }
            
            if (Donchian_HIGH != Donchian_Current_HIGH)
               {
                  Donchian_Previous_HIGH = Donchian_Current_HIGH;
                  Donchian_Current_HIGH = Donchian_HIGH;
               }
   
            if (Donchian_LOW != Donchian_Current_LOW)
               {
                  Donchian_Previous_LOW = Donchian_Current_LOW;
                  Donchian_Current_LOW = Donchian_LOW;
               }
            if (Donchian_MID != Donchian_Current_MID)
               {
                  Donchian_Previous_MID = Donchian_Current_MID;
                  Donchian_Current_MID = Donchian_MID;
                  if (Donchian_Current_MID > Donchian_Previous_MID)
                     Signal = "BUY";
                  else if (Donchian_Current_MID < Donchian_Previous_MID)
                     Signal = "SELL";
          
                 // Orders_Pending_Delete();
                  if (Signal == "BUY" )    //&& Close_Previous > Donchian_Current_MID)  
                     {               
                         Buy_Positions += 1;
                         OrderSend(NULL, OP_BUYSTOP, LotSize, Donchian_Current_HIGH, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                         OrderSend(NULL, OP_SELLSTOP, LotSize, Donchian_Current_LOW, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell); 
                         
                         
                       //  OrderSend(NULL, OP_BUYLIMIT, LotSize, Donchian_Current_MID, 5,0 ,0 , "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                       // OrderSend(NULL, OP_SELLLIMIT, LotSize, Donchian_Current_HIGH, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                     }
   
                  if (Signal == "SELL" )  //&& Close_Previous < Donchian_Current_MID)]
                     {              
                        Sell_Positions += 1;
                        OrderSend(NULL, OP_BUYSTOP, LotSize, Donchian_Current_HIGH, 5, 0, 0, "TREND" + "|" + "0" + "|" + Buy_Positions + "|" + "0", MagicNumber_Buy);
                        OrderSend(NULL, OP_SELLSTOP, LotSize, Donchian_Current_LOW, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell); 
                        
                      //  OrderSend(NULL, OP_SELLLIMIT, LotSize, Donchian_Current_MID, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell);
                       /// OrderSend(NULL,OP_BUYLIMIT, LotSize, Donchian_Current_LOW, 5, 0, 0, "TREND" + "|" + "0" + "|" + Sell_Positions + "|" + "0", MagicNumber_Sell); 
                     }    
               } 
         }
   }
