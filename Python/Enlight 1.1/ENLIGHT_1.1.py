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
    print("---ENLIGHT 1.0---")
    Strategy_Codename = input("STRATEGY STOP CODENAME: ")
    print('-----------------------')
    Account_Type = input("Account Type [LIVE / PRACTICE]: ")
    Instrument = input("INSTRUMENT [XXX_YYY] -> ")
    Granularity = input("GRANULARITY [Sx, Mx, Hx, D, W, M]: ")
    Price_Decimal = int(input("PRICE DECIMAL [INT] -> "))
    DistanceStop = input("STOP DISTANCE [Price Units 0.xxxxx or 0.xxx]: ")
    Units_Size = int(input("BASE UNITS SIZE: "))
    Time = input("TIME[sec] : ")
    print("-----------------------", "\n")


    ################ SETUP ################
    def AccID():
        if Account_Type == "LIVE":
            ID = "001-011-3186926-003"
            return ID
        elif Account_Type == "PRACTICE":
            ID = "101-011-12347680-006"
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


    def Order_MKT(Units, TradeClientExtension):
        data = {
            "order": {
                "type": "MARKET",
                "instrument": Instrument,
                "units": str(Units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                #"clientExtensions": {"id": str(OrderClientExtension)},
                "tradeClientExtensions": {"id": str(TradeClientExtension)}
            }
        }
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print("Order Market Opened")
    def Trade_DETAILS(TradeClientExtension):
            Trade_DATA = trades.TradeDetails(accountID=AccountID, tradeID="@" + str(TradeClientExtension))
            Trade_REQUEST = Client.request((Trade_DATA))
            Trade_DETAILS = Trade_REQUEST["trade"]
            return Trade_DETAILS
    def Order_MIT(Price, Units): #, OrderClientExtension, TradeClientExtension):
        data = {
                "order": {
                            "type": "MARKET_IF_TOUCHED",
                            "instrument": Instrument,
                            "units": str(Units),
                            "price": str(Price),
                            "timeInForce": "GTC",
                            "positionFill": "DEFAULT",
                            "triggerCondition": "MID",
                            #"clientExtensions": {"id": str(OrderClientExtension)},
                            #"tradeClientExtensions": {"id": str(TradeClientExtension)}
                         }
                }
        Order_Create = orders.OrderCreate(AccountID, data=data)
        Client.request(Order_Create)
        print("Order MIT at: " + str(Price))
    def Trade_ClientExtensions(TradeID, NewID):
        data = {"clientExtensions": {"id": str(NewID)}}
        r = trades.TradeClientExtensions(accountID= AccountID, tradeID="@" + str(TradeID), data= data)
        Client.request(r)
    Index = 1

    ###############################################


    while True:
        try:
            Order_MKT(Units_Size, "BUY"+Strategy_Codename)
            BuyPrice = float(Trade_DETAILS("BUY"+Strategy_Codename)["price"])
            Order_MIT(round(float(BuyPrice - float(DistanceStop)), Price_Decimal), -1000)
            Trade_ClientExtensions("BUY"+Strategy_Codename, Strategy_Codename+str(Index))
            Index += 1

            Order_MKT(-Units_Size, "SELL"+Strategy_Codename)
            SellPrice = float(Trade_DETAILS("SELL"+Strategy_Codename)["price"])
            Order_MIT(round(float(SellPrice + float(DistanceStop)), Price_Decimal), 1000)
            Trade_ClientExtensions("SELL"+Strategy_Codename, Strategy_Codename+str(Index))
            Index += 1

            time.sleep(int(Time))
        except Exception as LoopException:
            print("LOOP EXCEPTION: ", LoopException)
            print("\n")
            time.sleep(1)



except Exception as MainException:
    print ("MAIN EXCEPTION\n", MainException)
    time.sleep(1)
    Close = input("SYSTEM CLOSING. [OK]")
    quit()



