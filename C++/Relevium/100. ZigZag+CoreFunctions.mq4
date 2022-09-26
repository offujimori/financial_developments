input double LotSize = 0.01;
input int Magic_Number = 100;

extern int ExtDepth=12;
extern int ExtDeviation=5;
extern int ExtBackstep=3;

double P0,P1,P2,P3,P4,P5, Previous_P4, Previous_P2;
string Signal;

void ZZ_SubPrintDetails()
   {
   string sComment   = "";
   string sp         = "----------------------------------------\n";
   string NL         = "\n";


       
   sComment = "ZigZag practise           Copyright © 2012, Tjipke" + NL;
   sComment = sComment + NL;
   sComment = sComment + "P0 " + DoubleToStr(P0,Digits) + NL;
   sComment = sComment + "P1 " + DoubleToStr(P1,Digits) + NL;
   sComment = sComment + "P2 " + DoubleToStr(P2,Digits) + NL;
   sComment = sComment + "P3 " + DoubleToStr(P3,Digits) + NL;
   sComment = sComment + "P4 " + DoubleToStr(P4,Digits) + NL;
   sComment = sComment + "P5 " + DoubleToStr(P5,Digits) + NL;            
   sComment = sComment + "Buffervalue 0  ZigZag " + NL;


   Comment(sComment);
   }
   
void ZZ_Call ()
   {
   //This function calls the custom indicator zigzag and returns it´s values. THE INDICATOR ZIGZAG MUST BE IN THE FOLDER C:\...\MetaTrader 4\experts\indicators AND MUST BE NAMED "zigzag"!!!!
      int n, i = 0;
      while(n<6)
      {
         if(P0>0) 
            {P5=P4; P4=P3; P3=P2; P2=P1; P1=P0; }
         P0=iCustom(Symbol(),0,"ZigZag",ExtDepth,ExtDeviation,ExtBackstep,0,i);
         if(P0>0)
            n+=1;
         i++;
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
    

   
  }

