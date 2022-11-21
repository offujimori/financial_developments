import ccxt
import config
import PSAR
import openpyxl
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 20)
pd.set_option('display.precision', 6)

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
import time
import schedule

ASSET = input('ASSET [XYZ]: ')
PSAR_step = 0.00001  #float(input('STEP [0.00001]: '))
PSAR_max_step = 50  #int(input('MAX STEP [50]: '))

###INPUTS OHLC CALL
TICKER = input('TICKER [XXX/YYY]: ')
TIMEFRAME = '1m' #input('TIMEFRAME [1m, 1d, 1w, 1M]: ')
CANDLE_limit = 3000 #int(input('AMOUNT OF CANDLES [INT or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_limit == 0:
    CANDLE_limit = None
CANDLE_since = 0 #int(input('AMOUNT OF TIME [UNIX or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_since == 0:
    CANDLE_since = None
###INPUTS OHLC CALL


###LOAD MARKETS
EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
#    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_DCA}                                                            ##EXCHANGE SETUP
})                                                                                                                      ##EXCHANGE SETUP

def PSAR_load(DF, step=0.00001, max_step=50):
    INDICATOR_psar = PSAR.PSARIndicator(DF['high'], DF['low'], DF['close'], step, max_step)

    DF['PSAR'] = INDICATOR_psar.psar()
    DF['PSAR UP'] = INDICATOR_psar.psar_up()
    DF['PSAR DOWN'] = INDICATOR_psar.psar_down()
    #DF['Signal UP'] = INDICATOR_psar.psar_up_indicator()                                                                # if signal up = 1;
    #DF['Signal DOWN'] = INDICATOR_psar.psar_down_indicator()                                                            # if signal down = 1;

    DF['HIGHEST'] = 0                                                                                                  # COLOCANDO AQUI O HIGHEST/LOWEST PARA ECONOMIZAR TEMPO
    DF['HIGHEST'] = DF['HIGHEST'].astype(float)
    DF['LOWEST'] = 0
    DF['LOWEST'] = DF['LOWEST'].astype(float)

    lowest = 0
    highest = 0
    for index in range(1, len(DF.index)):                                                                               #IDENTIFICANDO EXTREMO OPOSTO DO PSAR ATUAL

        if not pd.isna(DF.at[index, 'PSAR UP']):
            lowest = 0
            if highest != 0:
                highest = max(DF.at[index, 'high'], highest)                                                           #para ajustar em momentos que n volta para minima
                #highest = DF.at[index, 'high']
                DF.at[index, 'HIGHEST'] = highest
            else:
                highest = DF.at[index, 'high']
                DF.at[index, 'HIGHEST'] = highest

        elif not pd.isna(DF.at[index, 'PSAR DOWN']):
            highest = 0
            if lowest != 0:
                lowest = min(DF.at[index, 'low'], lowest)                                                              #para ajustar em momentos que n volta para minima
                #lowest = DF.at[index, 'low']
                DF.at[index, 'LOWEST'] = lowest
            else:
                lowest = DF.at[index, 'low']
                DF.at[index, 'LOWEST'] = lowest

    return DF

timestamp = None


def REBALANCE_deploy(DF):
    global timestamp
    print(DF.tail(5))
    print("Checking for buy and sell signals")

    BALANCE = EXCHANGE.fetch_balance()
    BALANCE_usd = BALANCE['USD']['total']
    BALANCE_asset = BALANCE[ASSET]['total']
    print('-----------------BALANCE-----------------')
    print('BALANCE USD: ', BALANCE_usd)
    print('BALANCE ASSET: ', BALANCE_asset)

    if timestamp != DF['timestamp'].iloc[-1]:
        timestamp = DF['timestamp'].iloc[-1]
        EXCHANGE.cancel_all_orders(symbol=TICKER)

        if not pd.isna(DF['PSAR UP'].iloc[-1]):
            print('-----------------UP-----------------')
            PSAR_up = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['PSAR UP'].iloc[-1]))                          ##FACILITAÇÃO

            ASSET_psar_dollar_up = BALANCE_asset*PSAR_up
            ASSET_psar_ideal_up = ((BALANCE_usd + ASSET_psar_dollar_up)/2)/PSAR_up

            PSAR_lot = ASSET_psar_ideal_up - BALANCE_asset                                                                     ##QUANDO PREÇO ESTIVER EMBAIXO, SUGERE QUE EU TENHA MAIS DO OUTRO ASSET
            PSAR_lot_format = EXCHANGE.amount_to_precision(symbol=TICKER, amount=PSAR_lot)                              ##FORMATAÇÃO DE PRECISAO DE LOTE

            print('PSAR PRICE: ', PSAR_up)
            print('ASSET to DOLLAR at PSAR: ', ASSET_psar_dollar_up)
            print('ASSET lot at PSAR: ', ASSET_psar_ideal_up)
            print('PSAR LOT [BUY]: ', PSAR_lot, ' // FORMAT: ', PSAR_lot_format)
            if float(PSAR_lot_format) > 0:                                                                              ##CASO O SINAL GENUINAMENTE ESTEJA DANDO UM REBALANCEAMENTO CERTO
                order = EXCHANGE.create_limit_buy_order(symbol=TICKER, amount=PSAR_lot_format, price=PSAR_up)           ##BUY
                print(order)
            else:
                print('PSAR UP LOT FORMAT <= 0')

            print('@@@@@@@')
            highest = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['HIGHEST'].iloc[-1]))                   ##REBALANCEAMENTO ENQUANTO MERCADO SOBRE COM PSAR EMBAIXO
            ASSET_highest_dollar = BALANCE_asset*highest
            ASSET_highest_ideal = ((BALANCE_usd + ASSET_highest_dollar)/2)/highest

            highest_lot = BALANCE_asset - ASSET_highest_ideal
            highest_lot_format = EXCHANGE.amount_to_precision(symbol=TICKER, amount=highest_lot)

            ###
            highest2 = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['high'].iloc[-1]))                     #SOLUCAO PARA CASO EM QUE UMA VELA FAZ UM ULTRA HIGH E EXISTE RISCO DE NAO MELHORAR O MÉDIO
            ASSET_highest_dollar2 = BALANCE_asset*highest2
            ASSET_highest_ideal2 = ((BALANCE_usd + ASSET_highest_dollar2)/2)/highest2

            highest_lot2 = BALANCE_asset - ASSET_highest_ideal2
            highest_lot_format2 = EXCHANGE.amount_to_precision(symbol=TICKER, amount=highest_lot2)
            ###

            print('HIGHEST PRICE: ', highest)
            print('ASSET to DOLLAR at HIGHEST: ', ASSET_highest_dollar)
            print('ASSET lot at HIGHEST: ', ASSET_highest_ideal)
            print('PRICE at HIGHEST to LOT [SELL]: ', highest_lot, ' // FORMAT: ', highest_lot_format)

            if float(highest_lot_format2) > 0:
                order = EXCHANGE.create_limit_sell_order(symbol=TICKER, amount=highest_lot_format2, price=highest2)     ##SELL
                print(order)
            elif float(highest_lot_format) > 0:
                order = EXCHANGE.create_limit_sell_order(symbol=TICKER, amount=highest_lot_format, price=highest)       ##SELL
                print(order)
            else:
                print('PSAR UP HIGHEST LOT FORMAT <= 0')
            print('-----------------UP-----------------')

        elif not pd.isna(DF['PSAR DOWN'].iloc[-1]):
            print('-----------------DOWN-----------------')
            PSAR_down = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['PSAR DOWN'].iloc[-1]))               #só apra facilitar
            ASSET_psar_dollar_down = BALANCE_asset*PSAR_down
            ASSET_psar_ideal_down = ((BALANCE_usd + ASSET_psar_dollar_down)/2)/PSAR_down

            PSAR_lot = BALANCE_asset - ASSET_psar_ideal_down                                                            ##INVERTE PSAR LOT POIS SUPOE-SE QUE O REBALANCIAMENTO SEJA PARA CIMA
            PSAR_lot_format = EXCHANGE.amount_to_precision(symbol=TICKER, amount=PSAR_lot)

            print('PSAR PRICE: ', PSAR_down)
            print('ASSET to DOLLAR at PSAR: ', ASSET_psar_dollar_down)
            print('ASSET LOT at PSAR: ', ASSET_psar_ideal_down)
            print('PSAR LOT [SELL]: ', PSAR_lot, ' // FORMAT: ', PSAR_lot_format)
            if float(PSAR_lot_format) > 0:
                order = EXCHANGE.create_limit_sell_order(symbol=TICKER, amount=PSAR_lot_format, price=PSAR_down)        ##SELL
                print(order)
            else:
                print('PSAR DOWN LOT FORMAT <= 0')

            print('@@@@@@@')
            lowest = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['LOWEST'].iloc[-1]))
            ASSET_lowest_dollar = BALANCE_asset*lowest
            ASSET_lowest_ideal = ((BALANCE_usd + ASSET_lowest_dollar)/2)/lowest

            lowest_lot = ASSET_lowest_ideal - BALANCE_asset
            lowest_lot_format = EXCHANGE.amount_to_precision(symbol=TICKER, amount=lowest_lot)

            ###
            lowest2 = float(EXCHANGE.price_to_precision(symbol=TICKER, price=DF['low'].iloc[-1]))                       #SOLUCAO PARA CASO EM QUE UMA VELA FAZ UM ULTRA HIGH E EXISTE RISCO DE NAO MELHORAR O MÉDIO
            ASSET_lowest_dollar2 = BALANCE_asset*lowest2
            ASSET_lowest_ideal2 = ((BALANCE_usd + ASSET_lowest_dollar2)/2)/lowest2

            lowest_lot2 = ASSET_lowest_ideal2 - BALANCE_asset
            lowest_lot_format2 = EXCHANGE.amount_to_precision(symbol=TICKER, amount=lowest_lot2)
            ###

            print('LOWEST PRICE: ', lowest)
            print('ASSET to DOLLAR at LOWEST: ', ASSET_lowest_dollar)
            print('ASSET LOT at PSAR: ', ASSET_lowest_ideal )
            print('PRICE at LOWEST to LOT [BUY]: ', lowest_lot, ' // FORMAT: ', lowest_lot_format)
            if float(lowest_lot_format2) > 0:
                order = EXCHANGE.create_limit_buy_order(symbol=TICKER, amount=lowest_lot_format2, price=lowest2)        ##BUY
                print(order)

            elif float(lowest_lot_format) > 0:
                order = EXCHANGE.create_limit_buy_order(symbol=TICKER, amount=lowest_lot_format, price=lowest)          ##BUY
                print(order)
            else:
                print('PSAR DOWN LOWEST LOT FORMAT <= 0')
            print('-----------------DOWN-----------------')

def BOT_run():
    print('________________________________________________________________________________________')
    print(f"\nFetching new bars for {datetime.now().isoformat()}")
    BARS_ohlc = EXCHANGE.fetch_ohlcv(symbol=TICKER, timeframe=TIMEFRAME, limit=CANDLE_limit, since=CANDLE_since)        #REQUEST OHLC

    ###MAIN DATA ORGANIZE
    BARS_ohlc_df = pd.DataFrame(data=BARS_ohlc[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])   #FRAME DATA // "data=BARS_ohlc[:-1]'' exclui barra em andamento
    BARS_ohlc_df.drop(columns='volume', inplace=True)                                                                   #REMOVE VOLUME
    BARS_ohlc_df['timestamp'] = pd.to_datetime(BARS_ohlc_df['timestamp'], unit='ms')                                    #UNIX TIMESTAMP TO DATE
    BARS_ohlc_df.reset_index(level=0, inplace=True)                                                                     #SET INDEX
    ###MAIN DATA ORGANIZE

    PSAR_Data = PSAR_load(BARS_ohlc_df, PSAR_step, PSAR_max_step)
    REBALANCE_deploy(PSAR_Data)


try:
    schedule.every(5).seconds.do(BOT_run)
except Exception as e:
    print('ERRO: ', e)
    pass

while True:
    schedule.run_pending()
    time.sleep(1)


#############
###EXCEL###
#path = r'C:\Users\OFF\OneDrive\Documents\Synapse DeFi - Synapse MM.xlsx'

#book = openpyxl.load_workbook(path)
#writer = pd.ExcelWriter(path, mode='a', engine='openpyxl', if_sheet_exists='replace')
#writer.book = book
#writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
#BARS_ohlc_df.to_excel(writer, sheet_name='Database',)
#writer.save()
###EXCEL###



