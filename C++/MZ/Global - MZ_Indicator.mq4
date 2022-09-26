//+------------------------------------------------------------------+
//|                                                 MZ_Indicator.mq4 |
//|                        Copyright 2019, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2019, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
input double Lots = 0.01;
input  int Magic_Number = 500;
input string File = "Alfa.csv";

static datetime Bar_Time = 0;

double Bars_Measure(int Shift)
   {
      double Bar_Range;
      int Bar;
      
      for (int B = 1; B<=Shift; B++)
         {
            double Bar_High = iHigh(Symbol(), PERIOD_CURRENT, B);
            double Bar_Low = iLow(Symbol(), PERIOD_CURRENT, B);
            double Range = Bar_High - Bar_Low;
            
            Bar += 1;
            Bar_Range += Range;
         }
      
      double Bar_Average_Range = NormalizeDouble(Bar_Range/Bar, Digits);
      
      return(Bar_Average_Range);
   }

int TextIndex;
int Comment_UP;
int Comment_DOWN;
string Signal = "";
datetime Signal_Datetime;
int Previous_UP;     //NUMERO ORDENS COMPRADAS ANTERIORMENTE
int Previous_DOWN;   //NUMERO DE ORDENS VENDIDAS ANTERIORMENTE
datetime Previous_Signal_Time = TimeCurrent(); // TEMPO SINAL ANTERIOR
int Time_Buy; // NUMERO DE BARRAS EM DOMINANCIA COMPRADORA
int Time_Sell; //NUMERO DE BARRAS EM DOMINANCIA VENDEDORA
void Orders_Status()
   {
      int UP;
      int DOWN;
      int Handle;
      string Commentary;
      
      int Bars_Count;
   
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) && OrderMagicNumber() == Magic_Number)
               {
                  if (OrderType() == OP_BUY)
                     {UP += 1;}
                  if (OrderType() == OP_SELL)
                     {DOWN += 1;}  
               }
         }
      
      if (UP > DOWN && Bar_Time!=Time[0])
         {
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex), IntegerToString(UP-DOWN), 12);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, clrAqua);  
            
            Time_Buy ++;
            
            TextIndex++;          
         }
         
      if (UP < DOWN && Bar_Time!=Time[0])
         {
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex), IntegerToString(DOWN-UP), 12);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, clrOrange);  
            
            Time_Sell ++;
            
            TextIndex++;          
         }         
         
      
      
      if ((Previous_UP <= Previous_DOWN && UP > DOWN && Signal == "DOWN") || (Previous_UP <= Previous_DOWN && UP > DOWN && Signal == ""))
         {
            Bars_Count = Bars(Symbol(), PERIOD_CURRENT, Previous_Signal_Time, TimeCurrent()); // CONTAGEM BARRAS DESDE ULTIMO SINAL
            Previous_Signal_Time = TimeCurrent();
            
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex),"UP - "+IntegerToString(Bars_Count), 20);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, White);
            TextIndex++;
            Comment_UP++;
            Signal = "UP";   
            
            Handle = FileOpen(File, FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, "|");
            FileSeek(Handle, 0, SEEK_END);
            FileWrite(Handle, Signal, TimeToString(Time[0], TIME_DATE | TIME_MINUTES), DoubleToString(Close[0], MarketInfo(Symbol(), MODE_DIGITS)));
            FileClose(Handle);           
         }
      
      if ((Previous_UP >= Previous_DOWN && UP < DOWN && Signal == "UP") || (Previous_UP >= Previous_DOWN && UP < DOWN && Signal == ""))
         {
            Bars_Count = Bars(Symbol(), PERIOD_CURRENT, Previous_Signal_Time, TimeCurrent()); // CONTAGEM BARRAS DESDE ULTIMO SINAL
            Previous_Signal_Time = TimeCurrent();         
         
            ObjectCreate(IntegerToString(TextIndex), OBJ_TEXT, 0, Time[0], Close[0]);
            ObjectSetText(IntegerToString(TextIndex),"DOWN - "+IntegerToString(Bars_Count), 20);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_TIME1,Time[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_PRICE1, Close[0]);
            ObjectSet(IntegerToString(TextIndex),OBJPROP_COLOR, Yellow);
            TextIndex++;
            Comment_DOWN++;
            Signal = "DOWN";
            
            Handle = FileOpen(File, FILE_WRITE | FILE_READ | FILE_CSV | FILE_COMMON | FILE_SHARE_READ | FILE_SHARE_WRITE, "|");
            FileSeek(Handle, 0, SEEK_END);
            FileWrite(Handle, Signal, TimeToString(Time[0], TIME_DATE | TIME_MINUTES), DoubleToString(Close[0], MarketInfo(Symbol(), MODE_DIGITS)));
            FileClose(Handle);            
         }    
      Previous_UP = UP;
      Previous_DOWN = DOWN; 

      Commentary = "UP Pos: " + UP                                + "\n";
      Commentary = Commentary + "DOWN Pos: "       + DOWN         + "\n"; 
      Commentary = Commentary + "\n";
      Commentary = Commentary + "Bar_UP: "         + Bar_UP       + "\n";
      Commentary = Commentary + "Bar_DOWN: "       + Bar_DOWN     + "\n";
      Commentary = Commentary + "\n";
      Commentary = Commentary + "Comment_UP: "     + Comment_UP   + "\n";
      Commentary = Commentary + "Comment_DOWN: "   + Comment_DOWN + "\n";
      Commentary = Commentary + "\n";
      Commentary = Commentary + "BUY DOMINANCE: "  + Time_Buy     + "\n";
      Commentary = Commentary + "SELL DOMINANCE: " + Time_Sell    + "\n";
      
      
      Comment(Commentary);    
   } 
   
void Orders_Delete_Peding()
   {
      for (int O = OrdersTotal() - 1; O>=0; O--)
         {
            if (OrderSelect(O, SELECT_BY_POS, MODE_TRADES) == True && OrderMagicNumber () == Magic_Number)
               {
                  if (OrderType() == OP_BUYSTOP)
                     {OrderDelete (OrderTicket(), clrNONE);}
                  if (OrderType() == OP_SELLSTOP)
                     {OrderDelete (OrderTicket(), clrNONE);}  
               }    
         }
   }
   
   
      
     

int OnInit()
  {
   FileDelete(File, FILE_COMMON);
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  { 
  }


int Bar_UP;                            //NUMERO DE BARRAS COMPRADORAS
int Bar_DOWN;                          //NUMERO DE BARRAS VENDEDORAS
void OnTick()
  {
   double Equity = iCustom(Symbol(), PERIOD_CURRENT, "Equity_v7",True,"","","",False,False,False,True,False,False,False,0,25,True,D'2009.08.17 00:00',False,D'2001.01.01 00:00');
   
   //static datetime Bar_Time = 0;
   
   double Pre_Previous_Close = iClose(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_Open = iOpen(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_High = iHigh(Symbol(), PERIOD_CURRENT, 2);
   double Pre_Previous_Low = iLow(Symbol(), PERIOD_CURRENT, 2);
   
   double Previous_Close = iClose(Symbol(), PERIOD_CURRENT, 1);
   double Previous_Open = iOpen(Symbol(), PERIOD_CURRENT, 1);
   double Previous_High = iHigh(Symbol(), PERIOD_CURRENT, 1);
   double Previous_Low = iLow(Symbol(), PERIOD_CURRENT, 1);
   
   //double Spread = MarketInfo(Symbol(),MODE_SPREAD)*Point;
   double Spread = Ask - Bid;
   
   Orders_Status();
   if (Bar_Time!=Time[0])
      {
         double Stop = Bars_Measure(24) + 20*Point;
      
         if (Previous_Close > Previous_Open)
            Bar_UP =+ 1;
         if (Previous_Close < Previous_Open)
            Bar_DOWN =+ 1;
         
         Orders_Delete_Peding();
         OrderSend(Symbol(), OP_BUYSTOP, Lots, NormalizeDouble(Previous_High + Spread, Digits), 5, Previous_High - Stop, 0, "", Magic_Number);
         OrderSend(Symbol(), OP_SELLSTOP, Lots, NormalizeDouble(Previous_Low - Spread, Digits), 5, Previous_Low + Stop, 0, "", Magic_Number);
         
         ObjectsDeleteAll(WindowOnDropped(), OBJ_ARROW);
         Bar_Time = Time[0];
      }
   Sleep(3000);   
      
  }
//+------------------------------------------------------------------+
