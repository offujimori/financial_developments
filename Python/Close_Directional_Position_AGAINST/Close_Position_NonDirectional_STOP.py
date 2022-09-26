import time
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.positions as positions


try:
    print('-----------------------')
    print("---FECHAMENTO POSICAO INDIRECIONAL STOP---")
    Strategy_Codename = input("STRATEGY STOP CODENAME: ")
    print('-----------------------')
    Account_Type = input("Account Type [LIVE / PRACTICE]: ")
    Instrument = input("INSTRUMENT [XXX_YYY] -> ")
    Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M]: ")
    Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
    Units_Size = int(input("BASE UNITS SIZE: "))
    StopLossDistance = float(input("STOP LOSS [Price Units 0.xxxxx: "))
    print("-----------------------", "\n")


    def AccID():
        if Account_Type == "LIVE":
            ID = "001-011-3186926-003"
            return ID
        elif Account_Type == "PRACTICE":
            ID = "101-011-12347680-007"
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

    ##############################################################################

    CurrentCandle_DATA = None
    PreviousCandle_DATA = None
    PrePreviousCandle_DATA = None
    CurrentCandle_TIME = None

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


    def Order_MKT(Units):  # , OrderClientExtension, TradeClientExtension):
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
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print("Order Market Opened")

    while True:
        try:
            print("\n")

            Instrument_CANDLES_Current()
            Instrument_CANDLES_Previous()
            print(CurrentCandle_DATA["TIME"], CurrentCandle_TIME)

            time.sleep(1)

            if CurrentCandle_DATA["TIME"] != CurrentCandle_TIME and PreviousCandle_DATA["CLOSE"] > PreviousCandle_DATA["OPEN"]:
                Order_MKT(-Units_Size)
                CurrentCandle_TIME = CurrentCandle_DATA["TIME"]
                time.sleep(10)

            elif CurrentCandle_DATA["TIME"] != CurrentCandle_TIME and PreviousCandle_DATA["CLOSE"] < PreviousCandle_DATA["OPEN"]:
                Order_MKT(+Units_Size)
                CurrentCandle_TIME = CurrentCandle_DATA["TIME"]
                time.sleep(10)

            else:
                time.sleep(10)
                print("Same Candle")

        except Exception as Loop:
            print("MAIN LOOP ERROR\n", Loop)
            time.sleep(1)


except Exception as Main:
    print("MAIN ERROR\n", Main)
    input("QUIT [ENTER]")
    quit()