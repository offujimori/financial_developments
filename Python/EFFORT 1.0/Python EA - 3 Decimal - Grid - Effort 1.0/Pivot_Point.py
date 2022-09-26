import dict_digger
import oandapyV20
import oandapyV20.endpoints.instruments as instruments

Client = oandapyV20.API(access_token="d52df53ba7439a8e5e5d98e9aef0b10a-ee7136f4c65cc2b4faac66932bf28735")
AccountID = "101-011-12347680-002"

Instrument = input('INPUT Pair (XXX_YYY): ')
Granularity = input('INPUT Granularity (Sx; Mx; Hx; D; W; M): ')

params = {"count": 2, "granularity": Granularity, "weeklyAlignment": "Sunday", "dailyAlignment": "17"}
r = instruments.InstrumentsCandles(instrument= Instrument, params=params)
rv = Client.request(r)
print(rv)
##previousCandle Data Unlocking##
result = dict_digger.dig(rv, 'candles',)
previousCandle = result[0] #MUDAR EM DOMINGOS
##

##Data Open##
previousOpen = float(dict_digger.dig(previousCandle, 'mid', 'o'))
previousHigh = float(dict_digger.dig(previousCandle, 'mid', 'h'))
previousLow = float(dict_digger.dig(previousCandle, 'mid', 'l'))
previousClose = float(dict_digger.dig(previousCandle, 'mid', 'c'))
##

##Pivot_Point Calculus##
PP = round(((previousHigh + previousLow + previousClose) / 3), 3)
S1 = round((2*PP) - previousHigh, 3)
S2 = round(PP - (previousHigh - previousLow), 3)
S3 = round(previousLow - 2*(previousHigh - PP), 3)
R1 = round((2*PP) - previousLow, 3)
R2 = round(PP + (previousHigh - previousLow), 3)
R3 = round(previousHigh + 2*(PP - previousLow), 3)
##

#print(rv)
#print(type(rv))
#print(result)
#print(type(result))
#print(result2)
#print(type(result2))
print('Open -> ', previousOpen)
print('High -> ', previousHigh)
print('Low -> ', previousLow)
print('Close -> ', previousClose)
print('-------------------------')
print('R3 -> ', R3)
print('R2 -> ', R2)
print('R1 -> ', R1)
print('**PP -> ', PP,"**")
print('S1 -> ', S1)
print('S2 -> ', S2)
print("S3 -> ", S3)

