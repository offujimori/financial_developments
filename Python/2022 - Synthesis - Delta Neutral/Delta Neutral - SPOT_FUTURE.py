import ccxt
import config
from datetime import datetime
import schedule
import time

import warnings
warnings.filterwarnings('ignore')

#CHANGE API IF DIFFERENT ACCOUNT
EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
#    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_DCA}                                                           ##EXCHANGE SETUP
})

print('VERIFY PRECISION AT SPOT AND FUTURES\n\n\nLONG SPOT & SHORT FUTURE 1m\n')


pair_spot = input('PAIR SPOT [XYZ/USD]: ')
pair_futures = input('PAIR FUTURES [XYZ-PERP]: ')
pair_lot = float(input('PAIR LOT [consider precision]: '))

action = input('ACTION [BUILD/DISMANTLE]: ')

def TRADE():
    EXCHANGE.load_markets()
    print('________________________________________________________________________________________')
    print(f"\nSpot LONG & Futures SHORT at {datetime.now().isoformat()}")
    pair_lot_precision = EXCHANGE.amount_to_precision(symbol=pair_spot, amount=pair_lot)

    if action == 'BUILD' or action == 'build':
        order_spot = EXCHANGE.create_market_buy_order(symbol=pair_spot, amount=pair_lot_precision)
        order_futures = EXCHANGE.create_market_sell_order(symbol=pair_futures, amount=pair_lot_precision)
        print('SPOT ORDER: ', order_spot)
        print('FUTURES ORDER: ', order_futures)

    elif action == 'DISMANTLE' or action == 'dismantle':
        order_spot = EXCHANGE.create_market_sell_order(symbol=pair_spot, amount=pair_lot_precision)
        order_futures = EXCHANGE.create_market_buy_order(symbol=pair_futures, amount=pair_lot_precision)
        print('SPOT ORDER: ', order_spot)
        print('FUTURES ORDER: ', order_futures)


schedule.every(15).seconds.do(TRADE)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        print('ERROR: ', e)





