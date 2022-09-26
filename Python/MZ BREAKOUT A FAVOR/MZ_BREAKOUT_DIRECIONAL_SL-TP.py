import time
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.positions as positions

try:
    #CHANGE ACCOUNTS ID
    print('-----------------------')
    print("---MZ BREAKOUT DIRECIONAL STOP---")
    Strategy_Codename = input("STRATEGY STOP CODENAME: ")
    print('-----------------------')
    Account_Type = input("Account Type [LIVE / PRACTICE]: ")
    Instrument = input("INSTRUMENT [XXX_YYY] -> ")
    Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M]: ")
    Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
    Units_Size = int(input("BASE UNITS SIZE: "))
    StopLossDistance = float(input("STOP LOSS [Price Units 0.xxx; 0.xxxxx: "))
    print("-----------------------", "\n")


    def AccID():
        if Account_Type == "LIVE":
            ID = "001-011-3186926-003"
            return ID
        elif Account_Type == "PRACTICE":
            ID = "101-011-12347680-009"
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
    CurrentCandle_DATA = None
    PreviousCandle_DATA = None
    PrePreviousCandle_DATA = None
    CurrentCandle_TIME = None
    Order_DETAILS_BUY = None
    Order_DETAILS_SELL = None

    Position_DATA = None

    Start_Lock = True
    Second_Lock = True
    Third_Lock = True
    Final_Lock = True
    Check_NET_Lock = True
    Breakout_Cycle = None

    BUY_Order_NAME = Strategy_Codename + "_" + "BUY"
    SELL_Order_NAME = Strategy_Codename + "_" + "SELL"


    def Instrument_CANDLES_Current():
        params = {"price": "B", "count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
        r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
        rv = Client.request(r)
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
        rv = Client.request(r)
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
        rv = Client.request(r)
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



    def Order_DETAILS(OrderClientExtension):
        Order_DATA = orders.OrderDetails(accountID=AccountID, orderID="@" + str(OrderClientExtension))
        Order_REQUEST = Client.request(Order_DATA)
        Order_DETAILS = Order_REQUEST["order"]
        return Order_DETAILS
    def Order_CANCEL(OrderClientExtension):
        Order_DATA = orders.OrderCancel(accountID=AccountID, orderID="@" + OrderClientExtension)
        Order_REQUEST = Client.request(Order_DATA)
        print(Order_REQUEST["orderCancelTransaction"]["clientOrderID"], " CANCELLED.")
    def Order_MIT(Price, Units, OrderClientExtension):  # , TradeClientExtension):
        data = {
            "order": {
                "type": "MARKET_IF_TOUCHED",
                "instrument": Instrument,
                "units": str(Units),
                "price": str(Price),
                "timeInForce": "GTC",
                "positionFill": "DEFAULT",
                "triggerCondition": "BID",
                "clientExtensions": {"id": str(OrderClientExtension)},
                "stopLossOnFill": {"distance": str(StopLossDistance)}
                # "tradeClientExtensions": {"id": str(TradeClientExtension)}
            }
        }
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print("Order MIT at: " + str(Price) + "_" + str(Units))
    def Order_MKT_DIFF_ID(Units):  # , TradeClientExtension):
        ID = "101-011-12347680-015"
        Clt = oandapyV20.API(access_token=AccTOKEN(), environment=AccEnvironment())
        data = {
            "order": {
                "type": "MARKET",
                "instrument": Instrument,
                "units": str(Units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {"distance": str(StopLossDistance)}
                # "clientExtensions": {"id": str(OrderClientExtension)},
                # "tradeClientExtensions": {"id": str(TradeClientExtension)}
            }
        }
        Order_Create = orders.OrderCreate(ID, data=data)
        Clt.request(Order_Create)
        print("Order Market Opened")



    def Position_DETAILS():
        params = positions.PositionDetails(accountID=AccountID, instrument=Instrument)
        Position_REQUEST = Client.request(params)
        Position_DETAILS = Position_REQUEST["position"]
        Long = Position_DETAILS["long"]["units"]
        Short = Position_DETAILS["short"]["units"]
        global Position_DATA
        Position_DATA = {"LONG": Long, "SHORT": Short}
        return Position_DETAILS
    def Position_CLOSE():
        data1 = {"longUnits": "ALL"}
        data2 = {"shortUnits": "ALL"}
        try:
            r1 = positions.PositionClose(accountID=AccountID, instrument=Instrument, data=data1)
            Client.request(r1)
            print("LONGs CLOSED")
        except:
            print("CLOSEALL: Long Units unavaiable to close.")
        try:
            r2 = positions.PositionClose(accountID=AccountID, instrument=Instrument, data=data2)
            Client.request(r2)
            print("SHORTs CLOSED")
        except:
            print("CLOSEALL: Short Units unavaiable to close.")



    def Order_UPDATE():
        global Order_DETAILS_BUY, Order_DETAILS_SELL
        try:
            Order_DETAILS_BUY = Order_DETAILS(BUY_Order_NAME)
            print("Order BUY Update")
        except:
            Order_DETAILS_BUY = "NONE"
            print("Order BUY NOT Updated")

        try:
            Order_DETAILS_SELL = Order_DETAILS(SELL_Order_NAME)
            print("Order SELL Update")
        except:
            Order_DETAILS_SELL = "NONE"
            print("Order SELL NOT Updated")
    def CloseAll():
        Position_CLOSE()
        try:
            Order_CANCEL(BUY_Order_NAME)
        except:
            print("CLOSEALL: ", BUY_Order_NAME, " not avaiable to cancel.")
        try:
            Order_CANCEL(SELL_Order_NAME)
        except:
            print("CLOSEALL: ", SELL_Order_NAME, "not avaiable to cancel.")
    def Reset_Variables():
        global CurrentCandle_DATA, PreviousCandle_DATA, PrePreviousCandle_DATA, CurrentCandle_TIME, Order_DETAILS_BUY, Order_DETAILS_SELL, Position_DATA, Start_Lock, Second_Lock, Third_Lock, Final_Lock, Check_NET_Lock, Breakout_Cycle
        CurrentCandle_DATA = None
        PreviousCandle_DATA = None
        PrePreviousCandle_DATA = None
        CurrentCandle_TIME = None
        Order_DETAILS_BUY = None
        Order_DETAILS_SELL = None

        Position_DATA = None

        Start_Lock = True
        Second_Lock = True
        Third_Lock = True
        Final_Lock = True
        Check_NET_Lock = True
        Breakout_Cycle = None

    def Breakout_Check():
        if PreviousCandle_DATA["HIGH"] > PrePreviousCandle_DATA["HIGH"] or PreviousCandle_DATA["LOW"] < PrePreviousCandle_DATA["LOW"]:
            print("-BREAKOUT CHECK OK-")
            global Breakout_Cycle
            Breakout_Cycle = "OK"
            return "OK"
        else:
            print("-BREAKOUT CHECK NONE-")
            Breakout_Cycle = "NONE"
            CloseAll()
            return "NONE"
        # and close Positions

    while True:
        try:
            while Final_Lock == True:
                try:
                    print("\n")
                    time.sleep(1)

                    Instrument_CANDLES_Current()
                    Instrument_CANDLES_Previous()
                    Instrument_CANDLES_Pre_Previous()
                    Order_UPDATE()
                    print(CurrentCandle_DATA["TIME"], CurrentCandle_TIME)
                    Breakout_Price_UP = round(float(PreviousCandle_DATA["HIGH"]) + 0.00001, Price_Decimal)
                    Breakout_Price_DOWN = round(float(PreviousCandle_DATA["LOW"]) - 0.00001, Price_Decimal)

                    time.sleep(1)

                    if CurrentCandle_DATA["TIME"] == CurrentCandle_TIME:
                        if Order_DETAILS_BUY["state"] == "FILLED" and Order_DETAILS_SELL["state"] == "PENDING":
                            try:
                                Order_CANCEL(SELL_Order_NAME)
                                print(SELL_Order_NAME, " CANCELLED BY OPPOSITE ORDER.")
                            except:
                                print(SELL_Order_NAME, " not avaiable to cancel by opposite order.")

                        elif Order_DETAILS_SELL["state"] == "FILLED" and Order_DETAILS_BUY["state"] == "PENDING":
                            try:
                                Order_CANCEL(BUY_Order_NAME)
                                print(BUY_Order_NAME, " CANCELLED BY OPPOSITE ORDER.")
                            except:
                                print(BUY_Order_NAME, "not avaiable to cancel by opposite order.")

                        time.sleep(10)

                    if CurrentCandle_DATA["TIME"] != CurrentCandle_TIME:
                        for X in [BUY_Order_NAME, SELL_Order_NAME]:
                            try:
                                Order_CANCEL(str(X))
                            except:
                                print(str(X), " -- Unable to Cancel")

                        time.sleep(1)

                        if Start_Lock == True:
                            Order_MIT(Breakout_Price_UP, Units_Size, BUY_Order_NAME)
                            Order_MIT(Breakout_Price_DOWN, -Units_Size, SELL_Order_NAME)
                            Start_Lock = False
                            Second_Lock = False

                            CurrentCandle_TIME = CurrentCandle_DATA["TIME"]
                            time.sleep(10)
                            continue

                        if Second_Lock == False:
                            print("SECOND LOCK TEST")
                            Breakout_Check()
                            if Breakout_Cycle == "OK":
                                Order_MIT(Breakout_Price_UP, Units_Size, BUY_Order_NAME)
                                Order_MIT(Breakout_Price_DOWN, -Units_Size, SELL_Order_NAME)
                                Third_Lock = False
                                Second_Lock = True

                                CurrentCandle_TIME = CurrentCandle_DATA["TIME"]
                                time.sleep(10)
                                continue
                            elif Breakout_Cycle == "NONE":
                                print("SECOND LOCK: Restarting Cycle\n\n")
                                Reset_Variables()
                                continue

                        if Third_Lock == False:
                            Breakout_Check()
                            print("THIRD LOCK TEST")
                            if Breakout_Cycle == "OK":
                                Order_MIT(Breakout_Price_UP, Units_Size, BUY_Order_NAME)
                                Order_MIT(Breakout_Price_DOWN, -Units_Size, SELL_Order_NAME)
                                Third_Lock = True
                                Final_Lock = False
                                Check_NET_Lock = False

                                CurrentCandle_TIME = CurrentCandle_DATA["TIME"]
                                time.sleep(10)
                                continue
                            elif Breakout_Cycle == "NONE":
                                print("THIRD LOCK: Restarting Cycle\n\n")
                                Reset_Variables()
                                continue

                except Exception as Loop:
                    print("MAIN LOOP ERROR\n", Loop)
                    time.sleep(10)

            while Final_Lock == False:
                try:
                    print("\n")
                    time.sleep(1)

                    Instrument_CANDLES_Current()
                    Instrument_CANDLES_Previous()
                    Instrument_CANDLES_Pre_Previous()
                    Order_UPDATE()

                    if CurrentCandle_DATA["TIME"] != CurrentCandle_TIME:
                        print("NO THIRD BREAKOUT. Reseting!")
                        CloseAll()
                        Reset_Variables()
                        time.sleep(10)
                        continue

                    if CurrentCandle_DATA["HIGH"] > PreviousCandle_DATA["HIGH"] or CurrentCandle_DATA["LOW"] < PreviousCandle_DATA["LOW"]:
                        Position_DETAILS()
                        NET = int(Position_DATA["LONG"]) + int(Position_DATA["SHORT"])

                        print("THIRD BREAKOUT. Order Sent. NET -> ", NET)

                        if NET == 0:
                            CloseAll()
                            Reset_Variables()
                            time.sleep(10)
                            continue

                        Order_MKT_DIFF_ID(NET)

                        while Check_NET_Lock == False:
                            try:
                                time.sleep(10)
                                Instrument_CANDLES_Current()
                                if CurrentCandle_DATA["TIME"] != CurrentCandle_TIME:
                                    Check_NET_Lock = True
                            except Exception as Loop:
                                print("CHECK NET ERROR\n", Loop)
                                time.sleep(10)

                        CloseAll()
                        Reset_Variables()

                    time.sleep(10)
                except Exception as Loop:
                    print("FINAL LOCK LOOP ERROR\n", Loop)
                    time.sleep(10)


        except Exception as MainLoop:
            print("LOOP ERROR\n", MainLoop)
            time.sleep(10)

except Exception as MainLoop:
    print("MAIN ERROR\n", MainLoop)
    input("QUIT [ENTER]")
    quit()