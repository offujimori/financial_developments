import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import time
import pandas as pd
import matplotlib.pyplot as plt

print("*** CANDLE MINER ***")
Account_Type = input("Account Type [LIVE / PRACTICE]: ")
Instrument = input("INSTRUMENT [XXX_YYY]: ")
Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
Granularity = input("PIVOT LINES TIMEFRAME [Sx, Mx, Hx, D, W, M]: ")
BTChoice = input("CHOOSE BT FORM [COUNT; FROM; FROMTO]: ")
if BTChoice == "COUNT":
    CandleCount = input("BARS COUNT: ")
elif BTChoice == "FROM":
    print("DATETIME EX [2019-01-30T22:00:00.000000000Z]")
    FromDate = input("SELECT FROM DATE: ")
elif BTChoice == "FROMTO":
    print("DATETIME EX [2019-01-30T22:00:00.000000000Z]")
    FromDate = input("SELECT FROM DATE: ")
    ToDate = input("SELECT TO DATE: ")



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

Bar_OPENCLOSE_Average_UP = 0
Bar_OPENCLOSE_Average_DOWN = 0
Bar_DOWN_Average = 0
Bar_UP_Average = 0
Bar_DOJI_Average = 0
Bars_List = []
Bar_UP = 0
Bar_DOWN = 0
Bar_DOJI = 0
Breakout_UP = 0
Breakout_DOWN = 0

Wick_UP_List = []
Wick_Down_List = []

def FROMTO_Bars():
    params = {"price": "B", "granularity": Granularity, "from": FromDate, "to": ToDate, "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
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
        if float(BarData["CLOSE"]) > float(BarData["OPEN"]):
            Size_UP = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["CLOSE"]) - float(BarData["OPEN"])
            global  Bar_UP, Bar_UP_Average, Bar_OPENCLOSE_Average_UP
            Bar_UP_Average += Size_UP
            Bar_OPENCLOSE_Average_UP += OpenClose
            Bar_UP += 1
        elif float(BarData["CLOSE"]) < float(BarData["OPEN"]):
            Size_DOWN = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["OPEN"]) - float(BarData["CLOSE"])
            global Bar_DOWN, Bar_DOWN_Average, Bar_OPENCLOSE_Average_DOWN
            Bar_DOWN_Average += Size_DOWN
            Bar_OPENCLOSE_Average_DOWN += OpenClose
            Bar_DOWN += 1
        elif float(BarData["CLOSE"]) == float(BarData["OPEN"]):
            Size_DOJI = float(BarData["HIGH"]) - float(BarData["LOW"])
            global Bar_DOJI, Bar_DOJI_Average
            Bar_DOJI_Average += Size_DOJI
            Bar_DOJI += 1

def FROM_Bars():
    params = {"price": "B", "granularity": Granularity, "from": FromDate, "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
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
        if float(BarData["CLOSE"]) > float(BarData["OPEN"]):
            Size_UP = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["CLOSE"]) - float(BarData["OPEN"])
            global  Bar_UP, Bar_UP_Average, Bar_OPENCLOSE_Average_UP
            Bar_UP_Average += Size_UP
            Bar_OPENCLOSE_Average_UP += OpenClose
            Bar_UP += 1
        elif float(BarData["CLOSE"]) < float(BarData["OPEN"]):
            Size_DOWN = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["OPEN"]) - float(BarData["CLOSE"])
            global Bar_DOWN, Bar_DOWN_Average, Bar_OPENCLOSE_Average_DOWN
            Bar_DOWN_Average += Size_DOWN
            Bar_OPENCLOSE_Average_DOWN += OpenClose
            Bar_DOWN += 1
        elif float(BarData["CLOSE"]) == float(BarData["OPEN"]):
            Size_DOJI = float(BarData["HIGH"]) - float(BarData["LOW"])
            global Bar_DOJI, Bar_DOJI_Average
            Bar_DOJI_Average += Size_DOJI
            Bar_DOJI += 1

def COUNT_Bars():
    params = {"price": "B", "granularity": Granularity, "count": str(CandleCount), "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    request = Client.request(r)
    List = request["candles"]
    print(List)
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


        if float(BarData["CLOSE"]) > float(BarData["OPEN"]):
            Size_UP = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["CLOSE"]) - float(BarData["OPEN"])
            #WICKS#
            WickUp = round(float(BarData["HIGH"]) - float(BarData["CLOSE"]), Price_Decimal)
            WickDown = round(float(BarData["OPEN"]) - float(BarData["LOW"]), Price_Decimal)
            Wick_UP_List.append(WickUp)
            Wick_Down_List.append(WickDown)
            ##
            global  Bar_UP, Bar_UP_Average, Bar_OPENCLOSE_Average_UP
            Bar_UP_Average += Size_UP
            Bar_OPENCLOSE_Average_UP += OpenClose
            Bar_UP += 1
        elif float(BarData["CLOSE"]) < float(BarData["OPEN"]):
            Size_DOWN = float(BarData["HIGH"]) - float(BarData["LOW"])
            OpenClose = float(BarData["OPEN"]) - float(BarData["CLOSE"])
            #WICKS#
            WickUp = round(float(BarData["HIGH"]) - float(BarData["OPEN"]), Price_Decimal)
            WickDown = round(float(BarData["CLOSE"]) - float(BarData["LOW"]), Price_Decimal)
            Wick_UP_List.append(WickUp)
            Wick_Down_List.append(WickDown)
            ##
            global Bar_DOWN, Bar_DOWN_Average, Bar_OPENCLOSE_Average_DOWN
            Bar_DOWN_Average += Size_DOWN
            Bar_OPENCLOSE_Average_DOWN += OpenClose
            Bar_DOWN += 1
        elif float(BarData["CLOSE"]) == float(BarData["OPEN"]):
            Size_DOJI = float(BarData["HIGH"]) - float(BarData["LOW"])
            global Bar_DOJI, Bar_DOJI_Average, Bar_OPENCLOSE_Average
            Bar_DOJI_Average += Size_DOJI
            Bar_DOJI += 1
        try:
            if float(BarData["HIGH"]) > float(Bars_List[-2]["HIGH"]):
                global Breakout_UP
                Breakout_UP += 1
            elif float(BarData["LOW"]) < float(Bars_List[-2]["LOW"]):
                global Breakout_DOWN
                Breakout_DOWN += 1
        except:
            pass




if BTChoice == "COUNT":
    COUNT_Bars()
elif BTChoice == "FROM":
    FROM_Bars()
elif BTChoice == "FROMTO":
    FROMTO_Bars()

try:
    UP_Average = round(Bar_UP_Average/Bar_UP, Price_Decimal)
except ZeroDivisionError:
    UP_Average = 0

try:
    DOWN_Average = round(Bar_DOWN_Average/Bar_DOWN, Price_Decimal)
except ZeroDivisionError:
    DOWN_Average = 0

try:
    DOJI_Average = round(Bar_DOJI_Average/Bar_DOJI, Price_Decimal)
except ZeroDivisionError:
    DOJI_Average = 0
try:
    UP_OPENCLOSE = round(Bar_OPENCLOSE_Average_UP/Bar_UP, Price_Decimal)
except ZeroDivisionError:
    UP_OPENCLOSE = 0
try:
    DOWN_OPENCLOSE = round(Bar_OPENCLOSE_Average_DOWN/Bar_DOWN, Price_Decimal)
except ZeroDivisionError:
    DOWN_OPENCLOSE = 0

Balance = round((Bar_UP*UP_OPENCLOSE)-(Bar_DOWN*DOWN_OPENCLOSE), Price_Decimal)


print("\nNº UP: ", Bar_UP)
print("UP AVERAGE: ", UP_Average)
print("OPEN-CLOSE: ", UP_OPENCLOSE)
print("PIPS: ", round(UP_Average, 4))

print("\nNº DOWN: ",Bar_DOWN)
print("DOWN AVERAGE:", DOWN_Average)
print("OPEN-CLOSE: ", DOWN_OPENCLOSE)
print("PIPS: ", round(DOWN_Average, 4))

print("\n*** BALANCE: ", Balance, " ***")

print("\nDOJI: ", Bar_DOJI)
print("DOJI AVERAGE: ", DOJI_Average)
print("PIPS: ", round((DOJI_Average), 4))


_ = plt.hist(Wick_Down_List+Wick_UP_List, bins=100)
plt.show()


print("\nBarData:", Bars_List)
print("\nBreakout UP: ", Breakout_UP)
print("Breakout DOWN: ", Breakout_DOWN)

if Bar_UP > Bar_DOWN:
    print("\nA: UP")
elif Bar_UP < Bar_DOWN:
    print("\nA: DOWN")
elif Bar_UP == Bar_DOWN:
    print("\nA: 0")
if Balance > 0:
    print("###B: UP")
elif Balance < 0:
    print("###B: DOWN")
elif Balance == 0:
    print("###B: 0")
if Breakout_UP > Breakout_DOWN:
    print("C: UP")
elif Breakout_UP < Breakout_DOWN:
    print("C: DOWN")
elif Breakout_UP == Breakout_DOWN:
    print("C: 0")


input("DATA COLLECTED. PRESS ENTER")
