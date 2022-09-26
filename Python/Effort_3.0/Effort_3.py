import time
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades

##ATENÇÃO##
# CASO DESEJE UTILIZAR MAIS DE UM ALGO NO MESMO ATIVO, É NECESSÁRIO REVISAR O CÓDIGO DE "ORDERCLIENT" JÁ QUE EXISTIRÁ PROBLEMA POIS TODOS MARKET ORDERS ESTÃO COM O MESMO ORDERCLIENTEXTENSION.
# CASO SEJA APLICADO OS MESMOS ORDERSCLIENTEXTENSION SIMULTANEAMENTE NO MESMO ATIVO, DARÁ PAU.

try:

    print('-----------------------')
    print("---EFFORT 3.0---")
    Strategy_Codename = input("STRATEGY STOP CODENAME: ")
    print('-----------------------')
    Account_Type = input("Account Type [LIVE / PRACTICE]: ")
    Instrument = input("INSTRUMENT [XXX_YYY] -> ")
    Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M]: ")
    Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
    print("-----------------------", "\n")


    ################ SETUP ################
    def AccID():
        if Account_Type == "LIVE":
            ID = "001-011-3186926-003"
            return ID
        elif Account_Type == "PRACTICE":
            ID = "101-011-12347680-002"
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
    #######################################
    Units = 1000
    Time = 15

    PivotLines_DATA = None
    CurrentBar_DATA = None
    PreviousBar_DATA = None
    Status_DATA = None
    OpenGAP_DATA = None

    Buy_Trade_CLIENT = "BUY_Trade_" + Instrument + "_" + Granularity + "_" + Strategy_Codename
    Sell_Trade_CLIENT = "SELL_Trade_" + Instrument + "_" + Granularity + "_" + Strategy_Codename
    Buy_Lock_CLIENT = "BUY_Lock_" + Instrument + "_" + Granularity + "_" + Strategy_Codename
    Sell_Lock_CLIENT = "SELL_Lock_" + Instrument + "_" + Granularity + "_" + Strategy_Codename

    def CurrentBar_UPDATE():
        params = {"price": "M", "count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
        r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
        rv = Client.request(r)
        result = rv["candles"]
        CurrentBar_CANDLE = result[1]
        CurrentBar_STATUS = str(CurrentBar_CANDLE["complete"])
        CurrentBar_OPEN = round(float(CurrentBar_CANDLE["mid"]["o"]), Price_Decimal)
        CurrentBar_HIGH = round(float(CurrentBar_CANDLE["mid"]["h"]), Price_Decimal)
        CurrentBar_LOW = round(float(CurrentBar_CANDLE["mid"]["l"]), Price_Decimal)
        CurrentBar_CLOSE = round(float(CurrentBar_CANDLE["mid"]["c"]), Price_Decimal)
        CurrentBar_DATETIME = CurrentBar_CANDLE["time"]
        CurrentBar_DAY = (CurrentBar_DATETIME[8:10])
        CurrentBar_MONTH = (CurrentBar_DATETIME[5:7])
        CurrentBar_YEAR = (CurrentBar_DATETIME[0:4])
        CurrentBar_TIME = (CurrentBar_DATETIME[11:19])
        global CurrentBar_DATA
        CurrentBar_DATA = {"STATUS": CurrentBar_STATUS, "DAY": CurrentBar_DAY, "MONTH": CurrentBar_MONTH, "YEAR": CurrentBar_YEAR,
                            "TIME": CurrentBar_TIME, "DATETIME": CurrentBar_DATETIME,
                            "HIGH": CurrentBar_HIGH, "LOW": CurrentBar_LOW, "OPEN": CurrentBar_OPEN, "CLOSE": CurrentBar_CLOSE
                            }
        return print("**CURRENT BAR DATA UPDATE**")
    def PreviousBar_UPDATE():
        params = {"price": "M", "count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
        r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
        rv = Client.request(r)
        result = rv["candles"]
        PreviousBar_CANDLE = result[0]
        PreviousBar_STATUS = str(PreviousBar_CANDLE["complete"])
        PreviousBar_OPEN = round(float(PreviousBar_CANDLE["mid"]["o"]), Price_Decimal)
        PreviousBar_HIGH = round(float(PreviousBar_CANDLE["mid"]["h"]), Price_Decimal)
        PreviousBar_LOW = round(float(PreviousBar_CANDLE["mid"]["l"]), Price_Decimal)
        PreviousBar_CLOSE = round(float(PreviousBar_CANDLE["mid"]["c"]), Price_Decimal)
        PreviousBar_DATETIME = PreviousBar_CANDLE["time"]
        PreviousBar_DAY = (PreviousBar_DATETIME[8:10])
        PreviousBar_MONTH = (PreviousBar_DATETIME[5:7])
        PreviousBar_YEAR = (PreviousBar_DATETIME[0:4])
        PreviousBar_TIME = (PreviousBar_DATETIME[11:19])
        global PreviousBar_DATA
        PreviousBar_DATA =  {"STATUS": PreviousBar_STATUS, "DAY": PreviousBar_DAY, "MONTH": PreviousBar_MONTH, "YEAR": PreviousBar_YEAR,
                            "TIME": PreviousBar_TIME, "DATETIME": PreviousBar_DATETIME,
                            "HIGH": PreviousBar_HIGH, "LOW": PreviousBar_LOW, "OPEN": PreviousBar_OPEN, "CLOSE": PreviousBar_CLOSE
                               }
        return print("**PREVIOUS BAR DATA UPDATE**")
    def PivotLines_UPDATE(Line):
        HIGH = float(PreviousBar_DATA["HIGH"])
        LOW = float(PreviousBar_DATA["LOW"])
        OPEN = float(PreviousBar_DATA["OPEN"])
        CLOSE = float(PreviousBar_DATA["CLOSE"])
        PP = round(((HIGH + LOW + CLOSE) / 3), Price_Decimal)
        S1 = round((2 * PP) - HIGH, Price_Decimal)
        S2 = round(PP - (HIGH - LOW), Price_Decimal)
        S3 = round(LOW - 2 * (HIGH - PP), Price_Decimal)
        R1 = round((2 * PP) - LOW, Price_Decimal)
        R2 = round(PP + (HIGH - LOW), Price_Decimal)
        R3 = round(HIGH + 2 * (PP - LOW), Price_Decimal)
        global PivotLines_DATA
        PivotLines_DATA = {"S3": S3, "S2": S2, "S1": S1, "PP": PP, "R1": R1, "R2": R2, "R3": R3}
        print("***PIVOT LINES UPDATED***")
        if Line == "PP":
            return PP
        elif Line == "S1":
            return S1
        elif Line == "S2":
            return  S2
        elif Line == "S3":
            return  S3
        elif Line == "R1":
            return R1
        elif Line == "R2":
            return R2
        elif Line == "R3":
            return R3

    def Trade_CLOSE(TradeClientExtension):
        data = {"units": "ALL"}
        Trade_DATA = trades.TradeClose(accountID=AccountID, tradeID="@"+str(TradeClientExtension), data=data)
        Client.request(Trade_DATA)
        print("*** "+str(TradeClientExtension)+" CLOSED***")
    def Trade_DETAILS(TradeClientExtension):
        Trade_DATA = trades.TradeDetails(accountID=AccountID, tradeID="@" + str(TradeClientExtension))
        Trade_REQUEST = Client.request((Trade_DATA))
        Trade_DETAILS = Trade_REQUEST["trade"]
        return Trade_DETAILS
    def Order_DETAILS(OrderClientExtension):
        Order_DATA = orders.OrderDetails(accountID=AccountID, orderID= "@" + str(OrderClientExtension))
        Order_REQUEST = Client.request(Order_DATA)
        Order_DETAILS = Order_REQUEST["order"]
        return Order_DETAILS
    def Order_MKT(Units, OrderClientExtension, TradeClientExtension):
        data = {
            "order": {
                "type": "MARKET",
                "instrument": Instrument,
                "units": str(Units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "clientExtensions": {"id": str(OrderClientExtension)},
                "tradeClientExtensions": {"id": str(TradeClientExtension)}
            }
        }
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print ("Order Market Opened")
    def Order_MIT(Price, Units, OrderClientExtension, TradeClientExtension):
        data = {
                "order": {
                            "type": "MARKET_IF_TOUCHED",
                            "instrument": Instrument,
                            "units": str(Units),
                            "price": str(Price),
                            "timeInForce": "GTC",
                            "positionFill": "DEFAULT",
                            "triggerCondition": "MID",
                            "clientExtensions": {"id": str(OrderClientExtension)},
                            "tradeClientExtensions": {"id": str(TradeClientExtension)}
                         }
                }
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print("Order MIT at: " + str(Price))

    def Status_IDENTIFY():
        Buy_Trade = None
        Buy_Lock = None
        Sell_Trade = None
        Sell_Lock = None

        try:
            if Trade_DETAILS(Buy_Trade_CLIENT)["state"] == "OPEN":
                Buy_Trade = True
            else:
                Buy_Trade = False
        except Exception as Status:
            print(Status)
            Buy_Trade = False

        try:
            if Trade_DETAILS(Buy_Lock_CLIENT)["state"] == "OPEN":
                Buy_Lock = True
            else:
                Buy_Lock = False
        except Exception as Status:
            print(Status)
            Buy_Lock = False

        try:
            if Trade_DETAILS(Sell_Trade_CLIENT)["state"] == "OPEN":
                Sell_Trade = True
            else:
                Sell_Trade = False
        except Exception as Status:
            print(Status)
            Sell_Trade = False

        try:
            if Trade_DETAILS(Sell_Lock_CLIENT)["state"] == "OPEN":
                Sell_Lock = True
            else:
                Sell_Lock = False
        except Exception as Status:
            print(Status)
            Sell_Lock = False
        print (Buy_Trade, Buy_Lock, Sell_Trade, Sell_Lock)
        if Buy_Trade == False and Buy_Lock == False and Sell_Trade == False and Sell_Lock == False:
            global Status_DATA
            Status_DATA = "ZERO_POSITION"
            print("***STATUS UPDATED***")
            return "ZERO_POSITION"
        if Buy_Trade == True and Buy_Lock == False and Sell_Trade == True and Sell_Lock == False:
            Status_DATA = "EQUILIBRIUM_POSITION"
            print("***STATUS UPDATED***")
            return "EQUILIBRIUM_POSITION"
        if Buy_Trade == True and Buy_Lock == True and Sell_Trade == False and Sell_Lock == False:
            Status_DATA = "BUY_HEDGE"
            print("***STATUS UPDATED***")
            return "BUY_HEDGE"
        if Buy_Trade == False and Buy_Lock == False and Sell_Trade == True and Sell_Lock == True:
            Status_DATA = "SELL_HEDGE"
            print("***STATUS UPDATED***")
            return "SELL_HEDGE"

    def OpenGAP():
        if float(CurrentBar_DATA["OPEN"]) > float(PivotLines_DATA["PP"]) and float(CurrentBar_DATA["OPEN"]) < float(PivotLines_DATA["R1"])\
                and float(CurrentBar_DATA["HIGH"]) < float(PivotLines_DATA["R1"]) and float(CurrentBar_DATA["LOW"]) > float(PivotLines_DATA["S1"]):

            global OpenGAP_DATA
            OpenGAP_DATA = "PP_R1"
            GAP = "PP_R1"

        elif float(CurrentBar_DATA["OPEN"]) < float(PivotLines_DATA["PP"]) and float(CurrentBar_DATA["OPEN"]) > float(PivotLines_DATA["S1"]) \
                and float(CurrentBar_DATA["LOW"]) > float(PivotLines_DATA["S1"]) and float(CurrentBar_DATA["HIGH"]) < float(PivotLines_DATA["R1"]):

            OpenGAP_DATA = "PP_S1"
            GAP = "PP_S1"

        else:
            OpenGAP_DATA = "GAP_CLOSED"
            GAP = "GAP_CLOSED"
        return GAP


    while True:
        try:
            PreviousBar_UPDATE()
            print("Previous Bar Data: ", PreviousBar_DATA)
            CurrentBar_UPDATE()
            print("Current Bar Data: ", CurrentBar_DATA)
            Status_IDENTIFY()
            print("Status: ", Status_DATA)
            PivotLines_UPDATE("PP")
            print(PivotLines_DATA)
            OpenGAP()
            print("Open GAP DAta: ", OpenGAP_DATA)
            print(Buy_Trade_CLIENT,"\n\n")

            if Status_DATA == "ZERO_POSITION":
                if OpenGAP_DATA == "PP_R1" and float(CurrentBar_DATA["LOW"]) <= float(PivotLines_DATA["PP"]):
                    Order_MKT(Units, "Buy", Buy_Trade_CLIENT)
                    Order_MKT(-Units, "Sell", Sell_Trade_CLIENT)
                elif OpenGAP_DATA == "PP_S1" and float(CurrentBar_DATA["HIGH"]) >= float(PivotLines_DATA["PP"]):
                    Order_MKT(Units, "Buy", Buy_Trade_CLIENT)
                    Order_MKT(-Units, "Sell", Sell_Trade_CLIENT)

            if Status_DATA == "EQUILIBRIUM_POSITION":
                if float(CurrentBar_DATA["HIGH"]) >= float(PivotLines_DATA["R1"]):
                    Trade_CLOSE(Buy_Trade_CLIENT)
                    Order_MKT(Units, "Lock", Sell_Lock_CLIENT)
                elif float(CurrentBar_DATA["LOW"]) <= float(PivotLines_DATA["S1"]):
                    Trade_CLOSE(Sell_Trade_CLIENT)
                    Order_MKT(Units, "Lock", Buy_Lock_CLIENT)

            if Status_DATA == "BUY_HEDGE":
                if OpenGAP_DATA == "PP_R1" and float(CurrentBar_DATA["HIGH"]) < float(PivotLines_DATA["R1"]) and float(CurrentBar_DATA["LOW"]) <= float(PivotLines_DATA["PP"]):
                    Trade_CLOSE(Buy_Lock_CLIENT)
                    Order_MKT(-Units, "Sell", Sell_Trade_CLIENT)
                elif OpenGAP_DATA == "PP_S1" and float(CurrentBar_DATA["LOW"]) > float(PivotLines_DATA["S1"]) and float(CurrentBar_DATA["HIGH"]) >= float(PivotLines_DATA["PP"]):
                    Trade_CLOSE(Buy_Lock_CLIENT)
                    Order_MKT(-Units, "Sell", Sell_Trade_CLIENT)

            if Status_DATA == "SELL_HEDGE":
                if OpenGAP_DATA == "PP_R1" and float(CurrentBar_DATA["HIGH"]) < float(PivotLines_DATA["R1"]) and float(CurrentBar_DATA["LOW"]) <= float(PivotLines_DATA["PP"]):
                    Trade_CLOSE(Sell_Lock_CLIENT)
                    Order_MKT(Units, "Buy", Buy_Trade_CLIENT)
                if OpenGAP_DATA == "PP_S1" and float(CurrentBar_DATA["LOW"]) > float(PivotLines_DATA["S1"]) and float(CurrentBar_DATA["HIGH"]) >= float(PivotLines_DATA["PP"]):
                    Trade_CLOSE(Sell_Lock_CLIENT)
                    Order_MKT(Units, "Buy", Buy_Trade_CLIENT)

            time.sleep(Time)

        except Exception as LoopException:
            print("LOOP EXCEPTION: ", LoopException)
            print("\n")
            time.sleep(Time)

except Exception as MainException:
    print ("MAIN EXCEPTION\n", MainException)
    time.sleep(Time)
    Close = input("SYSTEM CLOSING. [OK]")
    quit()









