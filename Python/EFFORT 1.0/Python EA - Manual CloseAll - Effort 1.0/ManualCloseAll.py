import time
import oandapyV20
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.orders as orders

##SETUP##
AccountID = "101-011-12347680-002"
Client = oandapyV20.API(access_token="d52df53ba7439a8e5e5d98e9aef0b10a-ee7136f4c65cc2b4faac66932bf28735")
Strategy_Name = input("'STRATEGY NAME' + '_VERSION_': ")
Strategy_Instrument = input("'XXX_YYY': ")
Strategy_Granularity = input("'Sx; Mx; Hx; D; W; M': ")
Strategy_MaxID = input("0 -> 35: ")
Desire = input("SELECT DESIRED ACTION -> CLOSE_EVERYTHING; CLOSE_ORDERS; CLOSE_TRADES: ")
Sleep_Time = 5
print(Desire)
print(type(Desire))

Strategy_Data = Strategy_Name + Strategy_Instrument + Strategy_Granularity
print(Strategy_Data)
print('Max ID to check: ', Strategy_MaxID)
print('ACTION: '+Desire)
##

###ORDERS CLOSE###
def Close_All_Orders():
    for Orders in range(int(Strategy_MaxID)):
        try:
            Close_Orders = orders.OrderCancel(accountID=AccountID, orderID="@"+Strategy_Data+str(Orders))
            Client.request(Close_Orders)
            print("--- ORDER CLOSED: "+Strategy_Data+str(Orders)+" ---")
        except:
            print('.')
###
##TRADES CLOSE###
def Close_All_Trades():
    for Trades in range(int(Strategy_MaxID)):
        try:
            Close_Trades = trades.TradeClose(accountID=AccountID, tradeID="@"+Strategy_Data+str(Trades))
            Client.request(Close_Trades)
            print("--- TRADE CLOSED: "+Strategy_Data+str(Trades)+" ---")
        except:
            print('.')
##

if Desire == "CLOSE_EVERYTHING":
    Close_All_Orders()
    Close_All_Trades()
    time.sleep(Sleep_Time)


elif Desire == "CLOSE_ORDERS":
    Close_All_Orders()
    time.sleep(Sleep_Time)

elif Desire == "CLOSE_TRADES":
    Close_All_Trades()
    time.sleep(Sleep_Time)