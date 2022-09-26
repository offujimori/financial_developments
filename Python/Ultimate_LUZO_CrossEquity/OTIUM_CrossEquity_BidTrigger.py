import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.trades as trades
import pandas as pd
import numpy as np
import time


print("*** SMA CROSS || DONCHIAN EQUITY ***\n")

Strategy_Codename = input("STRATEGY CODENAME [string]: ")
Account_Demo_ID = input("Demo Account ID [string]: ")
Account_Live_ID = input("Live Account ID [string]: ")

Instrument = input("\nINSTRUMENT [XXX_YYY][string]: ")
Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M][string]: ")
Price_Decimal = int(input("PRICE DECIMAL [int]: "))
Unit_Size = int(input("BASE UNITS SIZE [int]: "))
StopLoss = float(input("STOP-LOSS [float] [0.xxxxx]: "))
TakeProfit = float(input("TAKE-PROFIT [float] [0.xxxxx]: "))

SMA_COUNT = int(input("\nSMA CANDLE COUNT [int]: "))
SMA_Short_INPUT = int(input("SMA Short [int]: "))
SMA_Long_INPUT = int(input("SMA Long [int]: "))
Donchian_INPUT = int(input("DONCHIAN [int]: "))

Database_PATH = input("\nBT DB Path [string]: ")
Database_SHEET = input("DB Excel Sheet [string]: ")
Database_DATAFRAME = pd.read_excel(Database_PATH, Database_SHEET, convert_float=False)

## ORIGINAL Account_Live_TOKEN = "9e9f8572bb706a0eeb30f8b0d51c32aa-2b9cd8c20331edecb8ded48031f994d1"
Account_Live_TOKEN = "d52df53ba7439a8e5e5d98e9aef0b10a-ee7136f4c65cc2b4faac66932bf28735"
Account_Demo_TOKEN = "d52df53ba7439a8e5e5d98e9aef0b10a-ee7136f4c65cc2b4faac66932bf28735"

## ORIGINAL Account_Live_ENVIRONMENT = "live"
Account_Live_ENVIRONMENT = "practice"
Account_Demo_ENVIRONMENT = "practice"


Account_Live_CLIENT = oandapyV20.API(access_token=Account_Live_TOKEN, environment= Account_Live_ENVIRONMENT)
Account_Demo_CLIENT = oandapyV20.API(access_token=Account_Demo_TOKEN, environment= Account_Demo_ENVIRONMENT)



############################################
#Floating Variables - START
############################################
CurrentCandle_DATA = None
PreviousCandle_DATA = None
PrePreviousCandle_DATA = None
CurrentCandle_DATETIME = None

Bars_List = []

Signal = None
Signal_Price = None
Previous_Signal = None
Previous_Signal_Price = None

SMA_Long_CURRENT = None
SMA_Long_PREVIOUS = None
SMA_Short_CURRENT = None
SMA_Short_PREVIOUS = None

Donchian_DATAFRAME = Database_DATAFRAME["BALANCE"].tolist()
Donchian_LIST = Donchian_DATAFRAME[-Donchian_INPUT::1]
Donchian_OUTPUT = None

print(Donchian_LIST)

Balance_CURRENT = None
Balance_PREVIOUS = None
Balance_CALL = True

TradeID = None
############################################
#Floating Variables - END
############################################



############################################
#Live Data - START
############################################
def Instrument_CANDLES_Current():
    params = {"price": "B", "count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    rv = Account_Live_CLIENT.request(r)
    result = rv["candles"]
    CurrentBar_CANDLE = result[1]
    CurrentBar_STATUS = str(CurrentBar_CANDLE["complete"])
    CurrentBar_OPEN = round(float(CurrentBar_CANDLE["bid"]["o"]), Price_Decimal)
    CurrentBar_HIGH = round(float(CurrentBar_CANDLE["bid"]["h"]), Price_Decimal)
    CurrentBar_LOW = round(float(CurrentBar_CANDLE["bid"]["l"]), Price_Decimal)
    CurrentBar_CLOSE = round(float(CurrentBar_CANDLE["bid"]["c"]), Price_Decimal)
    CurrentBar_DATETIME = CurrentBar_CANDLE["time"]
    CurrentBar_DAY = (CurrentBar_DATETIME[8:10])
    CurrentBar_MONTH = (CurrentBar_DATETIME[5:7])
    CurrentBar_YEAR = (CurrentBar_DATETIME[0:4])
    CurrentBar_TIME = (CurrentBar_DATETIME[11:19])
    global CurrentCandle_DATA
    CurrentCandle_DATA = {"STATUS": CurrentBar_STATUS, "DAY": CurrentBar_DAY, "MONTH": CurrentBar_MONTH,
                          "YEAR": CurrentBar_YEAR,
                          "TIME": CurrentBar_TIME, "DATETIME": CurrentBar_DATETIME,
                          "HIGH": CurrentBar_HIGH, "LOW": CurrentBar_LOW, "OPEN": CurrentBar_OPEN,
                          "CLOSE": CurrentBar_CLOSE
                          }
    return print("\n**CURRENT BAR DATA UPDATE**")

def Instrument_CANDLES_Previous():
    params = {"price": "B", "count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    rv = Account_Live_CLIENT.request(r)
    result = rv["candles"]
    PreviousBar_CANDLE = result[0]
    PreviousBar_STATUS = str(PreviousBar_CANDLE["complete"])
    PreviousBar_OPEN = round(float(PreviousBar_CANDLE["bid"]["o"]), Price_Decimal)
    PreviousBar_HIGH = round(float(PreviousBar_CANDLE["bid"]["h"]), Price_Decimal)
    PreviousBar_LOW = round(float(PreviousBar_CANDLE["bid"]["l"]), Price_Decimal)
    PreviousBar_CLOSE = round(float(PreviousBar_CANDLE["bid"]["c"]), Price_Decimal)
    PreviousBar_DATETIME = PreviousBar_CANDLE["time"]
    PreviousBar_DAY = (PreviousBar_DATETIME[8:10])
    PreviousBar_MONTH = (PreviousBar_DATETIME[5:7])
    PreviousBar_YEAR = (PreviousBar_DATETIME[0:4])
    PreviousBar_TIME = (PreviousBar_DATETIME[11:19])
    global PreviousCandle_DATA
    PreviousCandle_DATA = {"STATUS": PreviousBar_STATUS, "DAY": PreviousBar_DAY, "MONTH": PreviousBar_MONTH,
                           "YEAR": PreviousBar_YEAR,
                           "TIME": PreviousBar_TIME, "DATETIME": PreviousBar_DATETIME,
                           "HIGH": PreviousBar_HIGH, "LOW": PreviousBar_LOW, "OPEN": PreviousBar_OPEN,
                           "CLOSE": PreviousBar_CLOSE
                           }
    return print("**PREVIOUS BAR DATA UPDATE**")

def Instrument_CANDLES_Pre_Previous():
    params = {"price": "B", "count": 3, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    rv = Account_Live_CLIENT.request(r)
    result = rv["candles"]
    PreviousBar_CANDLE = result[0]
    PreviousBar_STATUS = str(PreviousBar_CANDLE["complete"])
    PreviousBar_OPEN = round(float(PreviousBar_CANDLE["bid"]["o"]), Price_Decimal)
    PreviousBar_HIGH = round(float(PreviousBar_CANDLE["bid"]["h"]), Price_Decimal)
    PreviousBar_LOW = round(float(PreviousBar_CANDLE["bid"]["l"]), Price_Decimal)
    PreviousBar_CLOSE = round(float(PreviousBar_CANDLE["bid"]["c"]), Price_Decimal)
    PreviousBar_DATETIME = PreviousBar_CANDLE["time"]
    PreviousBar_DAY = (PreviousBar_DATETIME[8:10])
    PreviousBar_MONTH = (PreviousBar_DATETIME[5:7])
    PreviousBar_YEAR = (PreviousBar_DATETIME[0:4])
    PreviousBar_TIME = (PreviousBar_DATETIME[11:19])
    global PrePreviousCandle_DATA
    PrePreviousCandle_DATA = {"STATUS": PreviousBar_STATUS, "DAY": PreviousBar_DAY, "MONTH": PreviousBar_MONTH,
                              "YEAR": PreviousBar_YEAR,
                              "TIME": PreviousBar_TIME, "DATETIME": PreviousBar_DATETIME,
                              "HIGH": PreviousBar_HIGH, "LOW": PreviousBar_LOW, "OPEN": PreviousBar_OPEN,
                              "CLOSE": PreviousBar_CLOSE
                              }
    return print("**PRE PREVIOUS BAR DATA UPDATE**")

def COUNT_Bars():
    global Bars_List
    Bars_List = []
    params = {"price": "B", "granularity": Granularity, "count": str(SMA_COUNT), "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    request = Account_Live_CLIENT.request(r)
    List = request["candles"]
    #print(List)
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
    for Candle in Bars_List[-SMA_Long_INPUT::1]:
        Data_L.append(float(Candle["CLOSE"]))
    #print("DATA_L:", Data_L)
    L_SMA = round(float(sum(Data_L) / SMA_Long_INPUT), Price_Decimal)

    global SMA_Long_CURRENT, SMA_Long_PREVIOUS
    if L_SMA != SMA_Long_CURRENT:
        SMA_Long_PREVIOUS = SMA_Long_CURRENT
        SMA_Long_CURRENT = L_SMA
        print("<... LONG SMA - UPDATED - ", L_SMA," ...>\n")

    elif L_SMA == SMA_Long_CURRENT:
        print("<... LONG SMA - CHECK ...>\n")

    ######  ######  ######  ######  ######  ######  ######  ######  ######  ######

    Data_S = []
    for Candle in Bars_List[-SMA_Short_INPUT::1]:
        Data_S.append(float(Candle["CLOSE"]))
    #print("DATA_S:", Data_S)
    S_SMA = round(float(sum(Data_S) / SMA_Short_INPUT), Price_Decimal)

    global SMA_Short_CURRENT, SMA_Short_PREVIOUS
    if S_SMA != SMA_Short_CURRENT:
        SMA_Short_PREVIOUS = SMA_Short_CURRENT
        SMA_Short_CURRENT = S_SMA
        print("<... SHORT SMA - UPDATED - ", S_SMA," ...>\n")

    elif S_SMA == SMA_Short_CURRENT:
        print ("<... SHORT SMA - CHECK ...>\n")

def Trend_Signal():
    ##BUY##
    global Signal, Previous_Signal, Signal_Price, Previous_Signal_Price, Trade
    if SMA_Short_PREVIOUS != None and SMA_Long_PREVIOUS != None:
        if SMA_Short_PREVIOUS <= SMA_Long_PREVIOUS and SMA_Short_CURRENT > SMA_Long_CURRENT:
            if Signal != "BUY":
                Previous_Signal = Signal
                Previous_Signal_Price = Signal_Price
                Signal = "BUY"
                Signal_Price = round(float(Bars_List[-1]["CLOSE"]), Price_Decimal)
                print("<... SIGNAL -> ", Signal, " ...>")
                print("<... SIGNAL PRICE-> ", Signal_Price, " ...>")
                print("<... PREVIOUS SIGNAL -> ", Previous_Signal, " ...>")
                print("<... PREVIOUS SIGNAL PRICE -> ", Previous_Signal_Price, " ...>")
        elif SMA_Short_PREVIOUS >= SMA_Long_PREVIOUS and SMA_Short_CURRENT < SMA_Long_CURRENT:
            if Signal != "SELL":
                Previous_Signal = Signal
                Previous_Signal_Price = Signal_Price
                Signal = "SELL"
                Signal_Price = round(float(Bars_List[-1]['CLOSE']), Price_Decimal)
                print("<... SIGNAL -> ", Signal, " ...>")
                print("<... SIGNAL PRICE-> ", Signal_Price, " ...>")
                print("<... PREVIOUS SIGNAL -> ", Previous_Signal, " ...>")
                print("<... PREVIOUS SIGNAL PRICE -> ", Previous_Signal_Price, " ...>")
        else:
            print("<... SIGNALS - CHECK ...>\n")#
############################################
#Live Data - END
############################################



############################################
#Excel Data - START
############################################
def Donchian_UPDATE_FLOAT():
    global Donchian_OUTPUT
    Minimum = min(Donchian_LIST)
    Maximum = max(Donchian_LIST)
    Donchian_OUTPUT = round(float((Maximum + Minimum)/2), 2)
    print("***DONCHIAN UPDATED***")

############################################
#Excel Data - END
############################################



############################################
#Demo Data - START
############################################
def Balance_UPDATE_FLOAT():
    global Balance_CURRENT, Balance_PREVIOUS, Balance_CALL
    Balance_Request = accounts.AccountSummary(Account_Demo_ID)
    Request = Account_Demo_CLIENT.request(Balance_Request)
    Balance = round(float(Request["account"]["balance"]), Price_Decimal)

    if Balance_CURRENT != Balance_PREVIOUS:
        Balance_PREVIOUS = Balance_CURRENT
        Balance_CURRENT = Balance
        del Donchian_LIST[0]
        Donchian_LIST.append(Balance_CURRENT)
        Balance_CALL = False
        print("***BALANCE UPDATED***")
    elif Balance_CURRENT == None and Balance_PREVIOUS == None:
        Balance_CURRENT = Balance
        del Donchian_LIST[0]
        Donchian_LIST.append(Balance_CURRENT)
        Balance_CALL = False
        print("***BALANCE UPDATED***")

    elif Balance_CURRENT == Balance_PREVIOUS:
        Balance_PREVIOUS = Balance_CURRENT
        Balance_CURRENT = Balance
        del Donchian_LIST[0]
        Donchian_LIST.append(Balance_CURRENT)
        Balance_CALL = False
        print("***BALANCE UPDATED***")

def Position_Instrument_UNITS_NET_STR():
    Pos_Request = positions.PositionDetails(accountID= Account_Demo_ID, instrument= Instrument)
    Request = Account_Demo_CLIENT.request(Pos_Request)
    Pos_Long = int(Request["position"]["long"]["units"])
    Pos_Short = int(Request["position"]["short"]["units"])
    if Pos_Long == 0 and Pos_Short == 0:
        return "0"
    else:
        return str(Pos_Long+Pos_Short)
############################################
#Demo Data - END
############################################



############################################
#TRADE - START
############################################
def Market_Trade_SLTP (AccID, CLIENT, Units):
    global TradeID
    data = {
              "order":
                {
                "units": str(Units),
                "instrument": Instrument,
                "timeInForce": "FOK",
                "type": "MARKET",
                "positionFill": "DEFAULT"
                }
            }

    Request_Trade = orders.OrderCreate(AccID, data=data)
    Request = CLIENT.request(Request_Trade)
    Price = float(Request["orderFillTransaction"]["price"])
    ID = Request["orderFillTransaction"]["tradeOpened"]["tradeID"]
    TradeID = ID
    print("-----TRADE ACTIVATED-----\nUNITS: ", Units, "\nPRICE: ", Price)

    if int(Units) > 0:
        BuyTP = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": Instrument,
                "units": str(-Units),
                "price": str(round(Price + TakeProfit, Price_Decimal)),
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "triggerCondition": "BID",
                "clientExtensions": {"id": "TP_ORDER"},
                #"stopLossOnFill": {"distance": str(StopLossDistance)}
                "tradeClientExtensions": {"id": "TP_TRADE"}
                    }
                }
        Request_BuyTP = orders.OrderCreate(accountID=AccID, data=BuyTP)
        CLIENT.request(Request_BuyTP)
        print("\n\nTAKEPROFIT: ", round(Price + TakeProfit, Price_Decimal), "\nUNITS: ", -Units)

        BuySL = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": Instrument,
                "units": str(-Units),
                "price": str(round(Price - StopLoss, Price_Decimal)),
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "triggerCondition": "BID",
                "clientExtensions": {"id": "SL_ORDER"},
                #"stopLossOnFill": {"distance": str(StopLossDistance)}
                "tradeClientExtensions": {"id": "SL_TRADE"}
                    }
                }
        Request_BuySL = orders.OrderCreate(accountID=AccID, data=BuySL)
        CLIENT.request(Request_BuySL)
        print("\n\nSTOPLOSS: ", round(Price - StopLoss, Price_Decimal), "\nUNITS: ", -Units)



    elif int(Units) < 0:
        SellTP = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": Instrument,
                "units": str(-Units),
                "price": str(round(Price - TakeProfit, Price_Decimal)),
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "triggerCondition": "BID",
                "clientExtensions": {"id": "TP_ORDER"},
                #"stopLossOnFill": {"distance": str(StopLossDistance)}
                "tradeClientExtensions": {"id": "TP_TRADE"}
                    }
                }
        Request_SellTP = orders.OrderCreate(accountID=AccID, data=SellTP)
        CLIENT.request(Request_SellTP)
        print("\n\nTAKEPROFIT: ", round(Price - TakeProfit, Price_Decimal), "\nUNITS: ", -Units)

        SellSL = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": Instrument,
                "units": str(-Units),
                "price": str(round(Price + TakeProfit, Price_Decimal)),
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "triggerCondition": "BID",
                "clientExtensions": {"id": "SL_ORDER"},
                #"stopLossOnFill": {"distance": str(StopLossDistance)}
                "tradeClientExtensions": {"id": "SL_TRADE"}
                    }
                }
        Request_SellSL = orders.OrderCreate(accountID=AccID, data=SellSL)
        CLIENT.request(Request_SellSL)
        print("\n\nSTOPLOSS: ", round(Price + TakeProfit, Price_Decimal), "\nUNITS: ", -Units)

def Targets_Update():
    try:
        Data = trades.TradeDetails(accountID= Account_Demo_ID, tradeID=TradeID)
        Request = Account_Demo_CLIENT.request(Data)
        if Request["trade"]["state"] == "CLOSED":
            try:
                TP_Demo_Data = orders.OrderCancel(accountID= Account_Demo_ID, orderID= "@"+"TP_ORDER")
                Account_Demo_CLIENT.request(TP_Demo_Data)
            except:
                pass

            try:
                TP_Live_Data = orders.OrderCancel(accountID= Account_Live_ID, orderID= "@"+"TP_ORDER")
                Account_Live_CLIENT.request(TP_Live_Data)
            except:
                pass

            try:
                SL_Demo_Data = orders.OrderCancel(accountID= Account_Demo_ID, orderID= "@"+"SL_ORDER")
                Account_Demo_CLIENT.request(SL_Demo_Data)
            except:
                pass

            try:
                SL_Live_Data = orders.OrderCancel(accountID= Account_Live_ID, orderID="@"+"SL_ORDER")
                Account_Live_CLIENT.request(SL_Live_Data)
            except:
                pass

    except Exception as Expt:
        print("Targets Update ----> ", Expt)



############################################
#TRADE - END
############################################

while True:
    try:
        print("\n***CYCLE RESTART***")
        #Instrument_CANDLES_Current()
        #Instrument_CANDLES_Previous()
        COUNT_Bars()
        SMA_UPDATE()
        Targets_Update()
        if CurrentCandle_DATA["DATETIME"] != CurrentCandle_DATETIME:
            if SMA_Long_PREVIOUS != None and SMA_Short_PREVIOUS != None:
               if (SMA_Short_PREVIOUS <= SMA_Long_PREVIOUS and SMA_Short_CURRENT > SMA_Long_CURRENT) or (SMA_Short_PREVIOUS >= SMA_Long_PREVIOUS and SMA_Short_CURRENT < SMA_Long_CURRENT):
                    if Position_Instrument_UNITS_NET_STR() == "0":
                        if Balance_CALL == True:
                            Balance_UPDATE_FLOAT()
                            Donchian_UPDATE_FLOAT()

                        if Balance_CURRENT >= Donchian_OUTPUT:
                            if SMA_Short_PREVIOUS <= SMA_Long_PREVIOUS and SMA_Short_CURRENT > SMA_Long_CURRENT:
                                Market_Trade_SLTP(Account_Demo_ID, Account_Demo_CLIENT, Unit_Size)
                                Market_Trade_SLTP(Account_Live_ID, Account_Live_CLIENT, Unit_Size)

                            elif SMA_Short_PREVIOUS >= SMA_Long_PREVIOUS and SMA_Short_CURRENT < SMA_Long_CURRENT:
                                Market_Trade_SLTP(Account_Demo_ID, Account_Demo_CLIENT, -Unit_Size)
                                Market_Trade_SLTP(Account_Live_ID, Account_Live_CLIENT, -Unit_Size)

                        elif Balance_CURRENT < Donchian_OUTPUT:
                            if SMA_Short_PREVIOUS <= SMA_Long_PREVIOUS and SMA_Short_CURRENT > SMA_Long_CURRENT:
                                Market_Trade_SLTP(Account_Demo_ID, Account_Demo_CLIENT, Unit_Size)
                                Market_Trade_SLTP(Account_Live_ID, Account_Live_CLIENT, -Unit_Size)

                            elif SMA_Short_PREVIOUS >= SMA_Long_PREVIOUS and SMA_Short_CURRENT < SMA_Long_CURRENT:
                                Market_Trade_SLTP(Account_Demo_ID, Account_Demo_CLIENT, -Unit_Size)
                                Market_Trade_SLTP(Account_Live_ID, Account_Live_CLIENT, Unit_Size)
                        CurrentCandle_DATETIME = CurrentCandle_DATA["DATETIME"]
                        Balance_CALL = False

        print("\n=----DATA---=", "\nLONG SMA CURRENT: ", SMA_Long_CURRENT, "\nSHORT SMA CURRENT: ", SMA_Short_CURRENT, "\n\nLONG SMA PREVIOUS: ",
              SMA_Long_PREVIOUS, "\nSHORT SMA PREVIOUS: ", SMA_Short_PREVIOUS)
        print('\n\nBALANCE LIST: ', Donchian_LIST)
        print("BALANCE CURRENT VALUE: ", Balance_CURRENT)
        print("DONCHIAN VALUE: ", Donchian_OUTPUT, "\n\n")

        print("\nOPEN POSITION:", Position_Instrument_UNITS_NET_STR())

        time.sleep(60)

    except Exception as Error:
        print(Error)
        time.sleep(10)