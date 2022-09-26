import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import time

print("*** LUZO HEDGE ***")
Codename = input(" EA -- CODENAME: ")
Account_Type = input("Account Type [LIVE / PRACTICE]: ")
Instrument = input("INSTRUMENT [XXX_YYY]: ")
Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
Granularity = input("PIVOT LINES TIMEFRAME [Sx, Mx, Hx, D, W, M]: ")
Units_Size = int(input("BASE UNITS SIZE: "))
CandleCount = input("BARS COUNT: ")
LONG_SMA_Index = int(input("**LONG** S-MA Index [int+]: "))
SHORT_SMA_Index = int(input("**SHORT** S-MA Index [int+]: "))



def AccID():
    if Account_Type == "LIVE":
        ID = "001-011-3186926-003"
        return ID
    elif Account_Type == "PRACTICE":
        ID = "101-011-12347680-016"
        return ID
    else:
        print("***ACCOUNT TYPE ERROR***")
        time.sleep(10)
        quit()
def AccTOKEN():
    if Account_Type == "LIVE":
        Token = "9e9f8572bb706a0eeb30f8b0d51c32aa-2b9cd8c20331edecb8ded48031f994d1"
        return Token
    elif Account_Type == "PRACTICE":
        Token = "d52df53ba7439a8e5e5d98e9aef0b10a-ee7136f4c65cc2b4faac66932bf28735"
        return Token
    else:
        print("***ACCOUNT TYPE ERROR***")
        time.sleep(10)
        quit()
def AccEnvironment():
    if Account_Type == "LIVE":
        Environment = "live"
        return Environment
    elif Account_Type == "PRACTICE":
        Environment = "practice"
        return Environment
    else:
        print("***ACCOUNT TYPE ERROR***")
        time.sleep(10)
        quit()

AccountID = AccID()
Client = oandapyV20.API(access_token=AccTOKEN(), environment=AccEnvironment())



Bars_List = []
LONG_SMA_Present_Value = None
LONG_SMA_Previous_Value = None


SHORT_SMA_Present_Value = None
SHORT_SMA_Previous_Value = None

Signal = None
Signal_Price = None
Previous_Signal = None
Previous_Signal_Price = None

Trade = False

TrendBuy = True
TrendSell = True
RangeBuy = True
RangeSell = True

Trend_Buy_ID = Codename + "_Trend_Buy"
Trend_Buy_ID_Order = Codename + "_Trend_Buy_Order"

Trend_Sell_ID = Codename + "_Trend_Sell"
Trend_Sell_ID_Order = Codename +"_Trend_Sell_Order"

Range_Buy_ID = Codename + "_Range_Buy"
Range_Buy_ID_Order = Codename + "_Range_Buy_Order"

Range_Sell_ID = Codename + "_Range_Sell"
Range_Sell_ID_Order = Codename +"_Range_Sell_Order"

def COUNT_Bars():
    global Bars_List
    Bars_List = []
    params = {"price": "B", "granularity": Granularity, "count": str(CandleCount), "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    request = Client.request(r)
    List = request["candles"]
    for Candle in List:
        if Candle == List[-1]:
            continue
        BarStatus = str(Candle["complete"])
        BarDateTime = Candle["time"]
        BarOpen = Candle["bid"]["o"]
        BarHigh = Candle["bid"]["h"]
        BarLow = Candle["bid"]["l"]
        BarClose = Candle["bid"]["c"]
        BarDay = (BarDateTime[8:10])
        BarMonth = (BarDateTime[5:7])
        BarYear = (BarDateTime[0:4])
        BarTime = (BarDateTime[11:19])
        BarData =   {
                "STATUS": BarStatus, "DAY": BarDay, "MONTH": BarMonth, "YEAR": BarYear,
                "TIME": BarTime, "DateTime": BarDateTime,
                "HIGH": BarHigh, "LOW": BarLow, "OPEN": BarOpen, "CLOSE": BarClose
                    }
        Bars_List.append(BarData)

def SMA_UPDATE():
    print("\n<... INITIALIZING SMA UPDATE ...>\n")

    Data_L = []
    for Candle in Bars_List[-1:-LONG_SMA_Index - 1:-1]:
        Data_L.append(float(Candle["CLOSE"]))
    L_SMA = round(float(sum(Data_L) / LONG_SMA_Index), Price_Decimal)

    global LONG_SMA_Present_Value, LONG_SMA_Previous_Value
    if L_SMA != LONG_SMA_Present_Value:
        LONG_SMA_Previous_Value = LONG_SMA_Present_Value
        LONG_SMA_Present_Value = L_SMA
        print("<... LONG SMA - UPDATED - ", L_SMA," ...>\n")

    elif L_SMA == LONG_SMA_Present_Value:
        print("<... LONG SMA - CHECK ...>\n")

    ######  ######  ######  ######  ######  ######  ######  ######  ######  ######

    Data_S = []
    for Candle in Bars_List[-1:-SHORT_SMA_Index - 1:-1]:
        Data_S.append(float(Candle["CLOSE"]))
    S_SMA = round(float(sum(Data_S) / SHORT_SMA_Index), Price_Decimal)

    global SHORT_SMA_Present_Value, SHORT_SMA_Previous_Value
    if S_SMA != SHORT_SMA_Present_Value:
        SHORT_SMA_Previous_Value = SHORT_SMA_Present_Value
        SHORT_SMA_Present_Value = S_SMA
        print("<... SHORT SMA - UPDATED - ", S_SMA," ...>\n")

    elif S_SMA == SHORT_SMA_Present_Value:
        print ("<... SHORT SMA - CHECK ...>\n")

def Trend_Signal():
    ##BUY##
    global Signal, Previous_Signal, Signal_Price, Previous_Signal_Price, Trade
    if SHORT_SMA_Previous_Value != None and LONG_SMA_Previous_Value != None:
        if SHORT_SMA_Previous_Value <= LONG_SMA_Previous_Value and SHORT_SMA_Present_Value > LONG_SMA_Present_Value:
            if Signal != "BUY":
                Previous_Signal = Signal
                Previous_Signal_Price = Signal_Price
                Signal = "BUY"
                Signal_Price = float(Bars_List[-1]["CLOSE"])
                Trade = True
                print("<... SIGNAL -> ", Signal, " ...>")
                print("<... SIGNAL PRICE-> ", Signal_Price, " ...>")
                print("<... PREVIOUS SIGNAL -> ", Previous_Signal, " ...>")
                print("<... PREVIOUS SIGNAL PRICE -> ", Previous_Signal_Price, " ...>")
        elif SHORT_SMA_Previous_Value >= LONG_SMA_Previous_Value and SHORT_SMA_Present_Value < LONG_SMA_Present_Value:
            if Signal != "SELL":
                Previous_Signal = Signal
                Previous_Signal_Price = Signal_Price
                Signal = "SELL"
                Signal_Price = float(Bars_List[-1]['CLOSE'])
                Trade = True
                print("<... SIGNAL -> ", Signal, " ...>")
                print("<... SIGNAL PRICE-> ", Signal_Price, " ...>")
                print("<... PREVIOUS SIGNAL -> ", Previous_Signal, " ...>")
                print("<... PREVIOUS SIGNAL PRICE -> ", Previous_Signal_Price, " ...>")
        else:
            print("<... SIGNALS - CHECK ...>\n")

def Order_MKT(Units):#, OrderExt, TradeExt):  # , TradeClientExtension):
    data = {
        "order": {
            "type": "MARKET",
            "instrument": Instrument,
            "units": str(Units),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT"
            #"clientExtensions": {"id": str(OrderExt)},
            #"tradeClientExtensions": {"id": str(TradeExt)}
        }
    }
    Order_Create = orders.OrderCreate(AccountID, data=data)
    Client.request(Order_Create)
    print("Order Market Opened")



def Trade_Close(ID):
    Trade_Data = {"units": "ALL"}
    Trade_Request = trades.TradeClose(accountID= AccountID, tradeID= "@" + ID, data= Trade_Data)
    Client.request(Trade_Request)
    print("<...", ID, " CLOSED ...>")



while True:
    try:
        print("\n***CYCLE RESTART***")
        COUNT_Bars()
        SMA_UPDATE()
        Trend_Signal()
        if Trade == True:
            if Previous_Signal != None:
                ### EXITS ###
                if Previous_Signal == "BUY" and Signal == "SELL" and Previous_Signal_Price < Signal_Price:
                    try:
                        Order_MKT(-Units_Size)
                        TrendBuy = True
                    except Exception as Error:
                        print(Error)
                        print("<... TREND BUY TRADE ALREADY CLOSED ...>")

                elif Previous_Signal == "SELL" and Signal == "BUY" and Previous_Signal_Price > Signal_Price:
                    try:
                        Order_MKT(Units_Size)
                        TrendSell = True
                    except Exception as Error:
                        print(Error)
                        print("<... TREND SELL TRADE ALREADY CLOSED ...>")

                elif Previous_Signal == "BUY" and Signal == "SELL" and Previous_Signal_Price > Signal_Price:
                    try:
                        Order_MKT(Units_Size)
                        RangeSell = True
                    except Exception as Error:
                        print(Error)
                        print("<... RANGE SELL TRADE ALREADY CLOSED ...>")

                elif Previous_Signal == "SELL" and Signal == "BUY" and Previous_Signal_Price < Signal_Price:
                    try:
                        Order_MKT(-Units_Size)
                        RangeBuy = True
                    except Exception as Error:
                        print(Error)
                        print("<... RANGE BUY TRADE ALREADY CLOSED ...>")

            ### ENTRIES ###
            if Signal == "BUY":
                if TrendBuy == True:
                    try:
                        Order_MKT(Units_Size)
                        TrendBuy = False
                    except Exception as Error:
                        print(Error)
                        print("<... BUY TREND ALREADY IN ...>")

                if RangeSell == True:
                    try:
                        Order_MKT(-Units_Size)
                        RangeSell = False
                    except Exception as Error:
                        print(Error)
                        print("<... SELL RANGE ALREADY IN ...>")

            elif Signal == "SELL":
                if TrendSell == True:
                    try:
                        Order_MKT(-Units_Size)
                        TrendSell = False
                    except Exception as Error:
                        print(Error)
                        print("<... SELL TREND ALREADY IN ..>")
                if RangeBuy == True:
                    try:
                        Order_MKT(Units_Size)
                        RangeBuy = False
                    except Exception as Error:
                        print(Error)
                        print("<... BUY RANGE ALREADY IN ...>")

            ###

            Trade = False

        print("\n\n<... SIGNAL -> ", Signal, " ...>")
        print("<... SIGNAL PRICE-> ", Signal_Price, " ...>")
        print("<... PREVIOUS SIGNAL -> ", Previous_Signal, " ...>")
        print("<... PREVIOUS SIGNAL PRICE -> ", Previous_Signal_Price, " ...>\n")
        print("LONG PRESENT VALUE: ",LONG_SMA_Present_Value)
        print("LONG PREVIOUS VALUE: ", LONG_SMA_Previous_Value)
        print("SHORT PRESENT VALUE: ",SHORT_SMA_Present_Value)
        print("SHORT PREVIOUS VALUE: ", SHORT_SMA_Previous_Value)


        time.sleep(60)
    except Exception as Error:
        print("MAIN LOOP ERROR")
        print(Error)
        time.sleep(10)
