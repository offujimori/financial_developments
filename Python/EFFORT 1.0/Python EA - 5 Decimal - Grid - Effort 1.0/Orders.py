import Pivot_Point
import Grid_Set
import time
import dict_digger
import oandapyV20.endpoints.positions as positions ##CLOSEALL
import oandapyV20 ##STANDARD
import oandapyV20.endpoints.trades as trades ##TRADE LIST PROCESS
import oandapyV20.endpoints.orders as orders ##ORDER PROCESS
import oandapyV20.endpoints.instruments as instruments ##PRICE RECALL
from oandapyV20.contrib.requests import (MITOrderRequest, TakeProfitDetails, StopLossDetails, ClientExtensions) ##ORDER PROCESS

##SETUP##
AccountID = "001-011-3186926-003"
Client = oandapyV20.API(access_token= "9e9f8572bb706a0eeb30f8b0d51c32aa-2b9cd8c20331edecb8ded48031f994d1", environment="live")
Instrument = Pivot_Point.Instrument
Time_Sleep = 30
StrategyName = "EFFORT_1.0_" + Pivot_Point.Instrument + Pivot_Point.Granularity
StrategyNameID = 0
Strategy_Orders_Opened = 0
nowHigh = Grid_Set.nowHigh
nowLow = Grid_Set.nowLow

##TARGET BUYS/STOP LOSS BUYS##
Buys_Target = Grid_Set.Grid_max
Buys_Loss = Grid_Set.Grid_min
##
##TARGET SELLS/STOP SELLS##
Sells_Target = Grid_Set.Grid_min
Sells_Loss = Grid_Set.Grid_max
##
##BOOLEAN INTERRUPTOR CICLOS##
C1 = False
C2 = False
C3 = False
C4 = False
C5 = False
C6 = False
C7 = False
C8 = False
C9 = False
C10 = False

X = 0 #Nº Ciclo


def StrategyID():
    global StrategyNameID
    StrategyNameID +=1
    global Strategy_Orders_Opened
    Strategy_Orders_Opened +=1
    STG = StrategyName+str(StrategyNameID)
    return STG


print("Running..."+StrategyName)
##

######################################
####TRADE LIST CALL
Trade_params = {"state": "OPEN", "instrument": Instrument, "count": 1}
Trades_list = trades.TradesList(accountID = AccountID, params = Trade_params)
Trades_list_request = Client.request(Trades_list)
    #print (Trades_list.response)
    #print (type(Trades_list_request))

######################################
def Trade_openUnits():
        try:
            Trades_list_request = Client.request(Trades_list)
            Trades_list_firstlock = Trades_list_request['trades']
            Trades_list_lastlock = Trades_list_firstlock[0]
            Check = float(Trades_list_lastlock['currentUnits'])
            return Check
        except:
            Check = 0
            return Check

def Price_Data_Recall():
    params = {"count": 2, "granularity": Pivot_Point.Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
    r = instruments.InstrumentsCandles(instrument=Instrument, params=params)
    rv = Client.request(r)
    result = dict_digger.dig(rv, 'candles', )
    nowCandle = result[1]
    global nowHigh, nowLow
    nowHigh = float(dict_digger.dig(nowCandle, 'mid', 'h'))
    nowLow = float(dict_digger.dig(nowCandle, 'mid', 'l'))



while nowHigh < Grid_Set.Grid_max and nowLow > Grid_Set.Grid_min and X < 11:
########################1º CYCLE########################
        if X == 0 and Trade_openUnits() == 0 and C1 == False:
            Trade_openUnits()
            ##SET BUY##
            Order_Buy_C1_TP = TakeProfitDetails(price = Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C1_SL = StopLossDetails(price = Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C1 = MITOrderRequest(instrument=Instrument, units=1, price = Grid_Set.Grid_3_channel_high, takeProfitOnFill = Order_Buy_C1_TP.data, stopLossOnFill = Order_Buy_C1_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C1_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C1.data)
            Client.request(Order_Buy_C1_Request)
            ##
            ##SET SELL##
            Order_Sell_C1_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C1_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C1 = MITOrderRequest(instrument=Instrument, units=-1, price=Grid_Set.Grid_2_channel_low, takeProfitOnFill = Order_Sell_C1_TP.data, stopLossOnFill = Order_Sell_C1_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C1_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C1.data)
            Client.request(Order_Sell_C1_Request)
            ##
            C1 = True
            print(Trade_openUnits())
            while X == 0:
                time.sleep((Time_Sleep))
                Trade_openUnits()
                Price_Data_Recall()
                print("WAITING FOR C1 COMPLETION // ", Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 1
                    break
                elif Trade_openUnits() < 0:
                    X = -1
                    break

########################2º CYCLE########################
        if X == 1 and C2 == False:
            Order_Sell_C2_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C2_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C2 = MITOrderRequest(instrument=Instrument, units=-2, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C2_TP.data, stopLossOnFill=Order_Sell_C2_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C2_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C2.data)
            Client.request(Order_Sell_C2_Request)
            C2 = True
            while Trade_openUnits() > 0 and C2 == True and X == 1:
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C2 SELL TRIGGER // ', Trade_openUnits())
                time.sleep(Time_Sleep)
                if Trade_openUnits() < 0:
                    X = -2
                    break
        elif X == -1 and C2 == False:
            Order_Buy_C2_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C2_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C2 = MITOrderRequest(instrument=Instrument, units= 2, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C2_TP.data, stopLossOnFill=Order_Buy_C2_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C2_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C2.data)
            Client.request(Order_Buy_C2_Request)
            C2 = True
            while Trade_openUnits() < 0 and C2 == True and X == -1:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C2 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 2
                    break

########################3º CYCLE########################
        if X == 2 and C3 == False:
            Order_Sell_C3_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C3_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C3 = MITOrderRequest(instrument=Instrument, units=-6, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C3_TP.data, stopLossOnFill=Order_Sell_C3_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C3_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C3.data)
            Client.request(Order_Sell_C3_Request)
            C3 = True
            while Trade_openUnits() > 0 and C3 == True and X == 2:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C3 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -3
                    break
        elif X == -2 and C3 == False:
            Order_Buy_C3_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C3_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C3 = MITOrderRequest(instrument=Instrument, units= 6, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C3_TP.data, stopLossOnFill=Order_Buy_C3_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C3_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C3.data)
            Client.request(Order_Buy_C3_Request)
            C3 = True
            while Trade_openUnits() < 0 and C3 == True and X == -2:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C3 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 3
                    break

########################4º CYCLE########################
        if X == 3 and C4 == False:
            Order_Sell_C4_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C4_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C4 = MITOrderRequest(instrument=Instrument, units=-12, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C4_TP.data, stopLossOnFill=Order_Sell_C4_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C4_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C4.data)
            Client.request(Order_Sell_C4_Request)
            C4 = True
            while Trade_openUnits() > 0 and C4 == True and X == 3:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C4 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -4
                    break
        elif X == -3 and C4 == False:
            Order_Buy_C4_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C4_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C4 = MITOrderRequest(instrument=Instrument, units= 12, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C4_TP.data, stopLossOnFill=Order_Buy_C4_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C4_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C4.data)
            Client.request(Order_Buy_C4_Request)
            C4 = True
            while Trade_openUnits() < 0 and C4 == True and X == -3:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C4 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 4
                    break

########################5º CYCLE########################
        if X == 4 and C5 == False:
            Order_Sell_C5_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C5_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C5 = MITOrderRequest(instrument=Instrument, units=-24, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C5_TP.data, stopLossOnFill=Order_Sell_C5_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C5_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C5.data)
            Client.request(Order_Sell_C5_Request)
            C5 = True
            while Trade_openUnits() > 0 and C5 == True and X == 4:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C5 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -5
                    break
        elif X == -4 and C5 == False:
            Order_Buy_C5_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C5_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C5 = MITOrderRequest(instrument=Instrument, units= 24, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C5_TP.data, stopLossOnFill=Order_Buy_C5_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C5_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C5.data)
            Client.request(Order_Buy_C5_Request)
            C5 = True
            while Trade_openUnits() < 0 and C5 == True and X == -4:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C5 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 5
                    break

########################6º CYCLE########################
        if X == 5 and C6 == False:
            Order_Sell_C6_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C6_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C6 = MITOrderRequest(instrument=Instrument, units=-48, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C6_TP.data, stopLossOnFill=Order_Sell_C6_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C6_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C6.data)
            Client.request(Order_Sell_C6_Request)
            C6 = True
            while Trade_openUnits() > 0 and C6 == True and X == 5:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C6 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -6
                    break
        elif X == -5 and C6 == False:
            Order_Buy_C6_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C6_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C6 = MITOrderRequest(instrument=Instrument, units= 48, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C6_TP.data, stopLossOnFill=Order_Buy_C6_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C6_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C6.data)
            Client.request(Order_Buy_C6_Request)
            C6 = True
            while Trade_openUnits() < 0 and C6 == True and X == -5:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C6 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 6
                    break

########################7º CYCLE########################
        if X == 6 and C7 == False:
            Order_Sell_C7_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C7_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C7 = MITOrderRequest(instrument=Instrument, units=-96, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C7_TP.data, stopLossOnFill=Order_Sell_C7_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C7_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C7.data)
            Client.request(Order_Sell_C7_Request)
            C7 = True
            while Trade_openUnits() > 0 and C7 == True and X == 6:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C7 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -7
                    break
        elif X == -6 and C7 == False:
            Order_Buy_C7_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C7_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C7 = MITOrderRequest(instrument=Instrument, units= 96, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C7_TP.data, stopLossOnFill=Order_Buy_C7_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C7_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C7.data)
            Client.request(Order_Buy_C7_Request)
            C7 = True
            while Trade_openUnits() < 0 and C7 == True and X == -6:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C7 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 7
                    break

########################8º CYCLE########################
        if X == 7 and C8 == False:
            Order_Sell_C8_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C8_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C8 = MITOrderRequest(instrument=Instrument, units=-192, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C8_TP.data, stopLossOnFill=Order_Sell_C8_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C8_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C8.data)
            Client.request(Order_Sell_C8_Request)
            C8 = True
            while Trade_openUnits() > 0 and C8 == True and X == 7:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C8 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -8
                    break
        elif X == -7 and C8 == False:
            Order_Buy_C8_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C8_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C8 = MITOrderRequest(instrument=Instrument, units= 192, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C8_TP.data, stopLossOnFill=Order_Buy_C8_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C8_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C8.data)
            Client.request(Order_Buy_C8_Request)
            C8 = True
            while Trade_openUnits() < 0 and C8 == True and X == -7:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C8 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 8
                    break

########################9º CYCLE########################
        if X == 8 and C9 == False:
            Order_Sell_C9_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C9_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C9 = MITOrderRequest(instrument=Instrument, units=-384, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C9_TP.data, stopLossOnFill=Order_Sell_C9_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C9_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C9.data)
            Client.request(Order_Sell_C9_Request)
            C9 = True
            while Trade_openUnits() > 0 and C9 == True and X == 8:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C9 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -9
                    break
        elif X == -8 and C9 == False:
            Order_Buy_C9_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C9_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C9 = MITOrderRequest(instrument=Instrument, units= 384, price=Grid_Set.Grid_3_channel_high,takeProfitOnFill=Order_Buy_C9_TP.data, stopLossOnFill=Order_Buy_C9_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C9_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C9.data)
            Client.request(Order_Buy_C9_Request)
            C9 = True
            while Trade_openUnits() < 0 and C9 == True and X == -8:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C9 BUY TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() > 0:
                    X = 9
                    break

########################10º CYCLE########################
        if X == 9 and C10 == False:
            Order_Sell_C10_TP = TakeProfitDetails(price=Sells_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C10_SL = StopLossDetails(price=Sells_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C10 = MITOrderRequest(instrument=Instrument, units=-768, price=Grid_Set.Grid_2_channel_low,takeProfitOnFill=Order_Sell_C10_TP.data, stopLossOnFill=Order_Sell_C10_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Sell_C10_Request = orders.OrderCreate(accountID=AccountID, data=Order_Sell_C10.data)
            Client.request(Order_Sell_C10_Request)
            C10 = True
            while Trade_openUnits() > 0 and C10 == True and X == 9:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C10 SELL TRIGGER // ', Trade_openUnits())
                if Trade_openUnits() < 0:
                    X = -10
                    break
        elif X == -9 and C10 == False:
            Order_Buy_C10_TP = TakeProfitDetails(price=Buys_Target, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C10_SL = StopLossDetails(price=Buys_Loss, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C10 = MITOrderRequest(instrument=Instrument, units= 768, price=Grid_Set.Grid_3_channel_high, takeProfitOnFill=Order_Buy_C10_TP.data, stopLossOnFill=Order_Buy_C10_SL.data, clientExtensions=ClientExtensions(clientID= StrategyID()).data)
            Order_Buy_C10_Request = orders.OrderCreate(accountID=AccountID, data=Order_Buy_C10.data)
            Client.request(Order_Buy_C10_Request)
            C10 = True
            while Trade_openUnits() < 0 and C10 == True and X == -9:
                time.sleep(Time_Sleep)
                Trade_openUnits()
                Price_Data_Recall()
                print('WAITING C10 BUY TRIGGER // ', Trade_openUnits())
                time.sleep(Time_Sleep)
                if Trade_openUnits() > 0:
                    X = 10
                    break

########################END CYCLE CLOSE########################
        if X == 10 or X == -10:
            print("ATENÇÃO: ALERTA DE ULTIMO CICLO")
            print("***DESEJA ENCERRAR TODAS POSIÇÕES???***")

            while True:
                Trade_openUnits()
                CloseAll = input("YES_FOR_SURE_YES/NO_FOR_SURE_NO: ")
                if CloseAll in {"YES_FOR_SURE_YES"}:
                    try:
                        Close_Data = {"longUnits": "ALL", "shortUnits": "ALL"}
                        CloseTrade_Request = positions.PositionClose(accountID=AccountID, instrument=Instrument, data = Close_Data)
                        Client.request(CloseTrade_Request)
                    except:
                        print("***VERIFY POSITIONS TO BE SURE THEY ARE CLOSED***")
                    for Orders in range(Strategy_Orders_Opened+1):
                        try:
                            Close_Orders = orders.OrderCancel (accountID = AccountID, orderID = "@"+StrategyName+str(Orders))
                            Client.request(Close_Orders)
                            print("----SUCESS CLOSE: "+StrategyName+str(Orders)+"----")
                        except:
                            print("ORDER CLOSE "+StrategyName+str(Orders)+" FAILED.")


                    print("TRADES&ORDERS CLOSED")

                else:
                    time.sleep(60)

else:
        Trade_openUnits()
        CloseAll = input("YES_FOR_SURE_YES/NO_FOR_SURE_NO: ")
        if CloseAll in {"YES_FOR_SURE_YES"}:
            try:
                Close_Data = {"longUnits": "ALL", "shortUnits": "ALL"}
                CloseTrade_Request = positions.PositionClose(accountID=AccountID, instrument=Instrument, data=Close_Data)
                Client.request(CloseTrade_Request)
            except:
                print ("***VERIFY POSITIONS TO BE SURE THEY ARE CLOSED***")
            for Orders in range(Strategy_Orders_Opened+1):
                try:
                    Close_Orders = orders.OrderCancel(accountID=AccountID, orderID="@"+StrategyName+str(Orders))
                    Client.request(Close_Orders)
                    print("----SUCESS CLOSE: " + StrategyName + str(Orders) + "----")
                except:
                    print("ORDER CLOSE "+StrategyName+str(Orders)+" FAILED.")
            print("TRADES&ORDERS CLOSED")

        else:
            time.sleep(60)
