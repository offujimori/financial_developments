import time
import yagmail
import oandapyV20
from requests.exceptions import HTTPError
import oandapyV20.endpoints.trades as trades ##TRADE LIST PROCESS
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
from oandapyV20.contrib.requests import (MITOrderRequest, ClientExtensions, StopLossOrderRequest)

try:
    ################ INPUTS ################
    print('-----------------------')
    print("---STOP---")
    STOP_Strategy_Codename = input("STRATEGY STOP CODENAME: ")
    print('-----------------------')
    Account_Type = input("Account Type [LIVE / PRACTICE]: ")
    Instrument = input("INSTRUMENT [XXX_YYY] -> ")
    Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M]: ")
    Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
    Grid_Max_Price = round(float(input("DEFINE RANGE MAX PRICE -> ")), Price_Decimal)
    Grid_Minimum_Price = round(float(input("DEFINE RANGE MINIMUM PRICE -> ")), Price_Decimal)
    ########################################


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


    ################ DEFINITIONS ################
    def STOP_Grid_Size_Box():
        Grid_Scale = float(5)
        Grid_Distance = round((Grid_Max_Price - Grid_Minimum_Price), Price_Decimal)
        Grid_Size_Box = round((Grid_Distance/Grid_Scale), Price_Decimal)
        return Grid_Size_Box

    def Recent_High():
        params = {"count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignement": "17"}
        r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
        rv = Client.request(r)
        nowHigh = round(float(rv["candles"][1]["mid"]["h"]), Price_Decimal)
        return nowHigh
    def Recent_Low():
        params = {"count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignement": "17"}
        r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
        rv = Client.request(r)
        nowLow = round(float(rv["candles"][1]["mid"]["l"]), Price_Decimal)
        return nowLow
    def GridVerify():
        if Recent_High() >= Grid_Max_Price or Recent_Low() <= Grid_Minimum_Price:
            for X in Trades_ClientIDs:
                try:
                    Trade_Close(X)
                except Exception as xxxx:
                    print(xxxx)
                    print("****TRADE "+str(X)+" not closed. ***")
                    pass
            for Y in Buy_Cycle + Sell_Cycle:
                try:
                    Order_Cancel(Y)
                except Exception as xxx:
                    print(xxx)
                    print("****ORDER "+str(Y)+" not closed. ***")
                    pass
            print("***ALL CLOSED***")
            input("EA will be closed by GridVerify. Ok?")
            quit()
        else:
            print("Grid Verified")

    def Email_Send(subject, body):
        receiver = "bus.fujimori@gmail.com"
        #filename = "document.pdf"
        yag = yagmail.SMTP(user="bus.fujimori@gmail.com", password= "r3h8u3m8")
        yag.send(
            to=receiver,
            subject=subject,
            contents=body,
            #attachments=filename,
            )
    def Trade_Close(ClientID):
        r = trades.TradeClose(accountID= AccountID, tradeID="@"+ ClientID)
        Client.request(r)
    def Order_Cancel(ClientID):
        r = orders.OrderCancel(accountID= AccountID, orderID="@"+ ClientID)
        Client.request(r)
    def Trade_Details(ClientID):
        r= trades.TradeDetails(accountID=AccountID, tradeID="@"+ ClientID)
        rv = Client.request(r)
        Data = (rv["trade"])
        return Data
    def Order_Details(ClientID):
        r= orders.OrderDetails(accountID=AccountID, orderID="@"+ ClientID)
        rv = Client.request(r)
        Data = (rv["order"])
        return Data
    def Trade_Last_Open():
        Trade_Params = {"state:": "OPEN", "instrument": Instrument, "count": 1}
        Trades_List = trades.TradesList(accountID=AccountID, params=Trade_Params)
        Trades_List_Request = Client.request(Trades_List)
        try:
            Open_Trades = int(Trades_List_Request["trades"][0]["currentUnits"])
            return Open_Trades
        except:
            Open_Trades = 0
            return Open_Trades

    #def Set_TP(KeyTrade_ClientID, TP_Price, Trigger):
    #    TradeID = Trade_Details(KeyTrade_ClientID)["id"]
    #    TP_Settings =  {
    #            "order": {
    #                "type": "TAKE_PROFIT", #MARKET, LIMIT, STOP, MARKET_IF_TOUCHED, TAKE_PROFIT, STOP_LOSS
    #                "tradeID": str(TradeID),
    #                "price": str(TP_Price),
    #                "timeInForce": "GTC",
    #                "triggerCondition": str(Trigger), #BUY COM BID; SELL COM ASK (Dai sai a mercado junto com Stops)
    #                "clientExtensions": {"id": str(New_TPSL_ClientID())}
    #                     }
    #             }
    #    TP_Create = orders.OrderCreate(accountID=AccountID, data=TP_Settings)
    #    Client.request(TP_Create)
    #    TPsSLs.append(Current_TPSP_ClientID())
    #    print("***Take Profit SET at "+str(TP_Price)+"***")
    #def Set_SL(KeyTrade_ClientID, SL_Price):
    #    TradeID = Trade_Details(KeyTrade_ClientID)["id"]
    #    SL_Settings = StopLossOrderRequest(tradeID= TradeID, price= SL_Price, clientExtensions=ClientExtensions(clientID=New_TPSL_ClientID()))
    #    SL_Create = orders.OrderCreate(accountID= AccountID, data= SL_Settings.data)
    #    Client.request(SL_Create)
    #    TPsSLs.append(Current_TPSP_ClientID())
    #    print("***Stop Loss SET at "+str(SL_Price)+"***")
    def New_KeyTrade_ClientID():
        global Strategy_Keytrade_Index
        Strategy_Keytrade_Index += 1
        STG = Current_Keytrade_ClientID()
        return STG
    def New_Trade_ClientID():
        global Strategy_Trade_Index
        Strategy_Trade_Index += 1
        STG = Current_Trade_ClientID()
        return STG
    #def New_TPSL_ClientID():
    #    global Strategy_TPSL_Index
    #    Strategy_TPSL_Index +=1
    #    STG = Current_TPSP_ClientID()
    #    return STG
    def MITOrder(Price, UnitsInteger):
        MIT_Settings = MITOrderRequest(instrument=Instrument,
                                       units= UnitsInteger,
                                       price= Price,
                                       positionFill= "OPEN_ONLY",
                                       clientExtensions=ClientExtensions(clientID=New_KeyTrade_ClientID()).data,
                                       tradeClientExtensions=ClientExtensions(clientID=New_Trade_ClientID()).data)
        MIT_Create = orders.OrderCreate(accountID=AccountID, data= MIT_Settings.data)
        Client.request(MIT_Create)
        print("***Open Order " + str(UnitsInteger) + " at " + str(Price))

    #############################################



    ################ TIME ################
    Time_Sleep = 15
    ################ GLOBAL VARIABLES STOP ################
    Strategy_KeyTrade_Name = "MAIN_" + STOP_Strategy_Codename + "_" + Instrument + "_" + Granularity
    Strategy_Keytrade_Index = 0
    def Current_Keytrade_ClientID():
        a = str(Strategy_KeyTrade_Name) + str(Strategy_Keytrade_Index)
        return a
    ###########
    Strategy_Trade_Name = "TRADE_" + STOP_Strategy_Codename + "_" + Instrument + "_" + Granularity
    Strategy_Trade_Index = 0
    def Current_Trade_ClientID():
        a = Strategy_Trade_Name + str(Strategy_Keytrade_Index)
        return a
    #############################################



    ############ GLOBAL VARIABLES ############
    Cycle_Switch = 0
    Buy_Cycle = []
    Sell_Cycle = []
    Trades_ClientIDs = []
    #TPsSLs = []
    First_Trigger = 0
    C1 = False
    Cycle_Loop_Switch = True
    Main_Cycle_Loop_Switch = True
    Initial_Lot_Buy = 100
    Initial_Lot_Sell = -100
    Triggers = ["C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14"]#, "C15"]
    def CycleLots(X):
        if First_Trigger == -1:
            Lots = {"C1": -100, "C2": 235, "C3": -317, "C4": 428, "C5": -578, "C6": 781, "C7": -1054, "C8": 1423, "C9": -1920, "C10": 2593, "C11": -3500, "C12": 4725, "C13": -6379, "C14": 8611}#, "C15": -1163}
            CycleLot = Lots.get(str(X))
            return CycleLot
        if First_Trigger == 1:
            Lots = {"C1": 100, "C2": -235, "C3": 317, "C4": -428, "C5": 578, "C6": -781, "C7": 1054, "C8": -1423, "C9": 1920, "C10": -2593, "C11": 3500, "C12": -4725, "C13": 6379, "C14": -8611}#, "C15": 1163}
            CycleLot = Lots.get(str(X))
            return CycleLot
    ########################################


    ################ STOP GRID CALCULATIONS ####################
    STOP_Grid_TOP = Grid_Max_Price
    #STOP_Grid_Mid_TOP = round(Grid_Minimum_Price + (4 * STOP_Grid_Size_Box()), Price_Decimal)
    STOP_Grid_Channel_High = round(float(input("\nDEFINE CHANNEL HIGH -> ")), Price_Decimal) #round(Grid_Minimum_Price + (3 * STOP_Grid_Size_Box()), Price_Decimal)
    STOP_Grid_Channel_Low = round(float(input("DEFINE CHANNEL LOW -> ")), Price_Decimal) #round(Grid_Minimum_Price + (2 * STOP_Grid_Size_Box()), Price_Decimal)
    #STOP_Grid_Mid_BOTTOM = round(Grid_Minimum_Price + (1 * STOP_Grid_Size_Box()), Price_Decimal)
    STOP_Grid_BOTTOM = Grid_Minimum_Price
    ##############################################
    ################ OUTPUT STOP GRID #################
    print('')
    print('----- STOP GRID PRICES -----')
    print('TOP: ', STOP_Grid_TOP)
    #print('MID_TOP: ', STOP_Grid_Mid_TOP)
    print('CHANNEL HIGH: ', STOP_Grid_Channel_High)
    print('*')
    print('CHANNEL LOW: ', STOP_Grid_Channel_Low)
    #print('MID_BOTTOM: ', STOP_Grid_Mid_BOTTOM)
    print('BOTTOM: ', STOP_Grid_BOTTOM)
    print('----------------------------')
    ##############################################
    ################ GRID VARIABLES #################
    Buy_Price = STOP_Grid_Channel_High
    Buy_Target = Grid_Max_Price
    Buy_Loss = Grid_Minimum_Price
    #
    Sell_Price = STOP_Grid_Channel_Low
    Sell_Target = Grid_Minimum_Price
    Sell_Loss = Grid_Max_Price
    ##############################################


    while Main_Cycle_Loop_Switch == True:
        try:
            while Recent_High() < Grid_Max_Price and Recent_Low() > Grid_Minimum_Price:
                time.sleep(5)
                if Cycle_Switch == 0 and Trade_Last_Open() == 0 and C1 == False:
                    ########################1º CYCLE########################
                    ##SET BUY##
                    MITOrder(Buy_Price, Initial_Lot_Buy)
                    Buy_Cycle.append(Current_Keytrade_ClientID())
                    Trades_ClientIDs.append(Current_Trade_ClientID())
                    time.sleep(3)

                    ##SET SELL##
                    MITOrder(Sell_Price, Initial_Lot_Sell)
                    Sell_Cycle.append(Current_Keytrade_ClientID())
                    Trades_ClientIDs.append(Current_Trade_ClientID())

                    C1 = True


                if Cycle_Switch == 0 and C1 == True:
                    print("\nWaiting C1 Fill... | Last Open Units: "+ str(Trade_Last_Open()))
                    time.sleep(Time_Sleep)
                    if Trade_Last_Open() > 0:
                        Cycle_Switch = 1
                        First_Trigger = 1
                        Order_Cancel(Sell_Cycle[0])

                    elif Trade_Last_Open() < 0:
                        Cycle_Switch = -1
                        First_Trigger = -1
                        Order_Cancel(Buy_Cycle[0])


                #######################CYCLE########################
                if Cycle_Switch == -1:
                    Current_Cycle = Triggers[0]
                    MITOrder(Buy_Price, CycleLots(Current_Cycle))
                    Buy_Cycle.append(Current_Keytrade_ClientID())
                    Trades_ClientIDs.append(Current_Trade_ClientID())
                    Triggers.remove(Triggers[0])
                    Cycle_Loop_Switch = True
                    Cycle_Switch = 1
                    print(Triggers)
                    time.sleep(Time_Sleep)
                    while Cycle_Loop_Switch == True:
                        try:
                            while Order_Details(Current_Keytrade_ClientID())["state"] == "PENDING":
                                print("\nWaiting "+Current_Cycle+" Fill... | Last Key Open: " + str(Current_Keytrade_ClientID()))
                                GridVerify()
                                time.sleep(Time_Sleep)
                            Cycle_Loop_Switch = False
                        except Exception as cx:
                            print("------CYCLE LOOP ERROR------")
                            print(cx)
                            time.sleep(Time_Sleep)
                            pass


                elif Cycle_Switch == 1: ###VENDA C2+###
                    Current_Cycle = Triggers [0]
                    MITOrder(Sell_Price, CycleLots(Current_Cycle))
                    Sell_Cycle.append(Current_Keytrade_ClientID())
                    Trades_ClientIDs.append(Current_Trade_ClientID())
                    Triggers.remove(Triggers[0])
                    Cycle_Loop_Switch = True
                    Cycle_Switch = -1
                    print(Triggers)
                    time.sleep(Time_Sleep)
                    while Cycle_Loop_Switch == True:
                        try:
                            while Order_Details(Current_Keytrade_ClientID())["state"] == "PENDING":
                                print("\nWaiting "+ Current_Cycle +" Fill... | Last Key Open: " + str(Current_Keytrade_ClientID()))
                                GridVerify()
                                time.sleep(Time_Sleep)
                            Cycle_Loop_Switch = False
                        except Exception as fx:
                            print("------CYCLE LOOP ERROR------")
                            print(fx)
                            time.sleep(Time_Sleep)
                            pass

            else:
                GridVerify()
                Main_Cycle_Loop_Switch = False
                input("CLOSING EA BY ELSE, OK?")
        except Exception as xx:
            print("------MAIN CYCLE LOOP ERROR------")
            print(xx)
            time.sleep(Time_Sleep)
            pass


except Exception as ex:
    print(ex)
    input("------FULL SCRIPT ERROR. OK?------")











































