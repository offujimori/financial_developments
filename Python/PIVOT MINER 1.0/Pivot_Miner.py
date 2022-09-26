import time
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd


#try:
print("***PIVOT MINER***")
Account_Type = input("Account Type [LIVE / PRACTICE]: ")
Instrument = input("INSTRUMENT [XXX_YYY]: ")
Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
Granularity = input("PIVOT LINES TIMEFRAME [Sx, Mx, Hx, D, W, M]: ")
CandleCount = input("PIVOT BARS COUNT: ")
Minor_Granularity = input("\nMinor Granularity [Sx, Mx, Hx, D, W, M]: ")


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

Pivot_Bar_List = []
Minor_Granularity_List = []
BackTest =[]

def Pivot_Lines(Line):
    try:
        HIGH = float(Pivot_Bar_List[-1]["HIGH"])
        LOW = float(Pivot_Bar_List[-1]["LOW"])
        OPEN = float(Pivot_Bar_List[-1]["OPEN"])
        CLOSE = float(Pivot_Bar_List[-1]["CLOSE"])
        PP = round(((HIGH + LOW + CLOSE) / 3), Price_Decimal)
        S1 = round((2 * PP) - HIGH, Price_Decimal)
        S2 = round(PP - (HIGH - LOW), Price_Decimal)
        S3 = round(LOW - 2 * (HIGH - PP), Price_Decimal)
        R1 = round((2 * PP) - LOW, Price_Decimal)
        R2 = round(PP + (HIGH - LOW), Price_Decimal)
        R3 = round(HIGH + 2 * (PP - LOW), Price_Decimal)
    except Exception as Pivot_Line_ERROR:
        HIGH = 0
        LOW =  0
        OPEN = 0
        CLOSE = 0
        PP = 0
        S1 = 0
        S2 = 0
        S3 = 0
        R1 = 0
        R2 = 0
        R3 = 0
    if Line == "PP":
        return PP
    elif Line == "S1":
        return S1
    elif Line == "S2":
        return S2
    elif Line == "S3":
        return S3
    elif Line == "R1":
        return R1
    elif Line == "R2":
        return R2
    elif Line == "R3":
        return R3
def Pivot_Bars_Data():
    params = {"price": "M", "granularity": Granularity, "count": str(CandleCount), "dailyAlignement": "17", "weeklyAlignment": "Sunday"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    request = Client.request(r)
    List = request["candles"]
    for Candle in List:
        BarStatus = str(Candle["complete"])
        BarDateTime = Candle["time"]
        BarOpen = Candle["mid"]["o"]
        BarHigh = Candle["mid"]["h"]
        BarLow = Candle["mid"]["l"]
        BarClose = Candle["mid"]["c"]
        BarDay = (BarDateTime[8:10])
        BarMonth = (BarDateTime[5:7])
        BarYear = (BarDateTime[0:4])
        BarTime = (BarDateTime[11:19])
        BarData =   {
                "STATUS": BarStatus, "DAY": BarDay, "MONTH": BarMonth, "YEAR": BarYear,
                "TIME": BarTime, "DateTime": BarDateTime,
                "HIGH": BarHigh, "LOW": BarLow, "OPEN": BarOpen, "CLOSE": BarClose,
                "PP": str(Pivot_Lines("PP")),
                "S1": str(Pivot_Lines("S1")), "S2": str(Pivot_Lines("S2")), "S3": str(Pivot_Lines("S3")),
                "R1": str(Pivot_Lines("R1")), "R2": str(Pivot_Lines("R2")), "R3": str(Pivot_Lines("R3"))
                    }
        Pivot_Bar_List.append(BarData)
def Pivot_Inside(Major_FROM_DateTime, Major_TO_DateTime):
    params =    {
            "price": "M", "granularity": Minor_Granularity,
            "from": Major_FROM_DateTime, "to": Major_TO_DateTime,
            "dailyAlignement": "17", "weeklyAlignment": "Sunday"
                }
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    request = Client.request(r)
    List = request["candles"]
    for Candle in List:
        BarDateTime = Candle["time"]
        BarHigh = Candle["mid"]["h"]
        BarLow = Candle["mid"]["l"]
        BarDay = (BarDateTime[8:10])
        BarMonth = (BarDateTime[5:7])
        BarYear = (BarDateTime[0:4])
        BarTime = (BarDateTime[11:19])
        BarData =   {
            "DateTime": BarDateTime, "HIGH": BarHigh, "LOW": BarLow
                    }
        Minor_Granularity_List.append(BarData)


Pivot_Bars_Data()
for Next, Bar in enumerate(Pivot_Bar_List):
    if Bar == Pivot_Bar_List[-1]:
        continue
    elif Bar == Pivot_Bar_List[0]:
        continue
    else:
        Major_High = float(Bar["HIGH"])
        Major_Low = float(Bar["LOW"])
        Major_Open = float(Bar["OPEN"])
        Major_Close = float(Bar["CLOSE"])
        Major_Initial_DateTime = Bar["DateTime"]
        MJD = Pivot_Bar_List[Next+1]
        Major_Final_Datetime = MJD["DateTime"]
        PP = float(Bar["PP"])
        R1 = float(Bar["R1"])
        R2 = float(Bar["R2"])
        R3 = float(Bar["R3"])
        S1 = float(Bar["S1"])
        S2 = float(Bar["S2"])
        S3 = float(Bar["S3"])
        Pivot_Inside(Major_Initial_DateTime, Major_Final_Datetime)
        PP_Lock = False
        R1_Lock = False
        R2_Lock = False
        R3_Lock = False
        S1_Lock = False
        S2_Lock = False
        S3_Lock = False

        Touch_List = ["0", "0", "0", "0","0","0","0"]
        Index = 0
        PP_R1 = round(R1 - PP, Price_Decimal)
        PP_S1 = round(PP - S1, Price_Decimal)

        for Minor in Minor_Granularity_List:
            if Major_Open > PP and Major_Open < R1:
                if PP_Lock == False and float(Minor["LOW"]) <= PP:
                    Touch_List[Index] = "PP"
                    Index += 1
                    PP_Lock = True
                elif R1_Lock == False and float(Minor["HIGH"]) >= R1:
                    Touch_List[Index] = "R1"
                    Index += 1
                    R1_Lock = True
                elif R2_Lock == False and float(Minor["HIGH"]) >= R2:
                    Touch_List[Index] = "R2"
                    Index += 1
                    R2_Lock = True
                elif R3_Lock == False and float(Minor["HIGH"]) >= R3:
                    Touch_List[Index] = "R3"
                    Index += 1
                    R3_Lock = True
                elif S1_Lock == False and float(Minor["LOW"]) <= S1:
                    Touch_List[Index] = "S1"
                    Index += 1
                    S1_Lock = True
                elif S2_Lock == False and float(Minor["LOW"]) <= S2:
                    Touch_List[Index] = "S2"
                    Index += 1
                    S2_Lock = True
                elif S3_Lock == False and float(Minor["LOW"]) <= S3:
                    Touch_List[Index] = "S3"
                    Index += 1
                    S3_Lock = True

            elif Major_Open < PP and Major_Open > S1:
                if PP_Lock == False and float(Minor["HIGH"]) >= PP:
                    Touch_List[Index] = "PP"
                    Index += 1
                    PP_Lock = True
                elif R1_Lock == False and float(Minor["HIGH"]) >= R1:
                    Touch_List[Index] = "R1"
                    Index += 1
                    R1_Lock = True
                elif R2_Lock == False and float(Minor["HIGH"]) >= R2:
                    Touch_List[Index] = "R2"
                    Index += 1
                    R2_Lock = True
                elif R3_Lock == False and float(Minor["HIGH"]) >= R3:
                    Touch_List[Index] = "R3"
                    Index += 1
                    R3_Lock = True
                elif S1_Lock == False and float(Minor["LOW"]) <= S1:
                    Touch_List[Index] = "S1"
                    Index += 1
                    S1_Lock = True
                elif S2_Lock == False and float(Minor["LOW"]) <= S2:
                    Touch_List[Index] = "S2"
                    Index += 1
                    S2_Lock = True
                elif S3_Lock == False and float(Minor["LOW"]) <= S3:
                    Touch_List[Index] = "S3"
                    Index += 1
                    S3_Lock = True

        Bar_Dict = {"DATE": Bar["DAY"]+"-"+Bar["MONTH"]+"-"+Bar["YEAR"], "PP_R1": PP_R1, "PP_S1": PP_S1,
                    "First": Touch_List[0], "Second": Touch_List[1], "Third": Touch_List[2], "Fourth": Touch_List[3], "Fifth": Touch_List[4], "Sixth": Touch_List[5], "Seventh": Touch_List[6]}
        print(Bar_Dict)
        BackTest.append(dict(Bar_Dict))
        Touch_List.clear()
        Bar_Dict.clear()
        Minor_Granularity_List.clear()

df = pd.DataFrame(BackTest)
df.to_excel("Pivot_Week.xls","EUR_USD")



















#except Exception as Main_Exception:
    #print(Main_Exception)