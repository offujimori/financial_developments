import ccxt

import config
import datetime
import time
import schedule
import pandas as pd
import openpyxl
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 20)
pd.set_option('display.precision', 6)

import warnings
warnings.filterwarnings('ignore')

ASSET = input('ASSET [XYZ]: ')
PATH = input(r'PATH: ')

#CHANGE API IF DIFFERENT ACCOUNT
EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
#    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_DCA}                                                            ##EXCHANGE SETUP
})


def STATUS_update(asset):
    BALANCE = EXCHANGE.fetch_balance()
    BALANCE_usd = BALANCE['USD']['total']
    BALANCE_asset = None
    BALANCE_asset_shares = None
    info = EXCHANGE.fetch_ticker(asset + '/USD')['last']
    timestamp = EXCHANGE.fetch_ticker(asset + '/USD')['timestamp']


    for i in BALANCE['info']['result']:
        if i['coin'] == asset:
            BALANCE_asset = i['usdValue']
            BALANCE_asset_shares = i['total']

    TOTAL = round(float(BALANCE_usd) + float(BALANCE_asset), 2)


    DATA = {'TIMESTAMP': int(timestamp),
            'USD': float(BALANCE_usd),
            asset+' USD': float(BALANCE_asset),
            asset+' SHARES': float(BALANCE_asset_shares),
            asset+' PRICE': float(info),
            'TOTAL': float(TOTAL)}
    print(DATA)

    return DATA

def STATUS_run():
    DATA = STATUS_update(ASSET)
    DATA_df = pd.DataFrame(data=[DATA], columns=['TIMESTAMP', 'USD', ASSET+' USD', ASSET+' SHARES', ASSET+' PRICE', 'TOTAL'])
    DATA_df['TIMESTAMP'] = pd.to_datetime(DATA_df['TIMESTAMP'], unit='ms')
    print(DATA_df)

    #path = r'C:\Users\Administrator\Desktop\Synthesis - MM Status.xlsx'
    #PATH = r'C:\Users\OFF\Desktop\Alfa.xlsx'
    book = openpyxl.load_workbook(PATH)
    writer = pd.ExcelWriter(PATH, engine='openpyxl')
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    DATA_df.to_excel(writer, sheet_name=ASSET, startrow=writer.sheets[ASSET].max_row, index=False, header=False)
    writer.save()


#schedule.every().day.at('00:00').do(STATUS_run)
schedule.every().hour.at(':00').do(STATUS_run)

while True:
    try:
        schedule.run_pending()
        print('Waiting. . .')
        time.sleep(60)
    except Exception as e:
        print('ERROR: ', e)
        input('Press one key.')