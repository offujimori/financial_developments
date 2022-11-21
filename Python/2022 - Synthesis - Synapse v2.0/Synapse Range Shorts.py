import ccxt
from PSAR_Minor import PSARIndicator as PSAR_fast
from PSAR_Major import PSARIndicator as PSAR_slow

import config
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

PSAR_step = 0.00001  #float(input('STEP [0.00001]: '))
PSAR_max_step = 50  #int(input('MAX STEP [50]: '))
LOT = float(input('MINIMUM LOT: '))
DELTA_X = 10

###INPUTS OHLC CALL
TICKER = input('PAIR [XYZ/USD || XYZ-PERP]: ')
TIMEFRAME = input('TIMEFRAME [1m, 1d, 1w, 1M]: ')
CANDLE_limit = 3000 #int(input('AMOUNT OF CANDLES [INT or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_limit == 0:
    CANDLE_limit = None
CANDLE_since = 0 #int(input('AMOUNT OF TIME [UNIX or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_since == 0:
    CANDLE_since = None
###INPUTS OHLC CALL


###LOAD MARKETS
EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY_Synapse_R_Shorts,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET_Synapse_R_Shorts,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_Synapse_R_Shorts}                                                            ##EXCHANGE SETUP
})                                                                                              ##EXCHANGE SETUP

def PSAR_minor(dataframe, step=0.00001, max_step=50):
    df = dataframe.copy(deep=True)                                                                                      ##CRIA COPIA DA DF PARA TRABALHAR
    INDICATOR_psar = PSAR_fast(df['high'], df['low'], df['close'], step, max_step)                                      ##PSAR CURTO

    df['psar'] = INDICATOR_psar.psar()
    df['psar up'] = INDICATOR_psar.psar_up()
    df['psar down'] = INDICATOR_psar.psar_down()
    df['signal up'] = INDICATOR_psar.psar_up_indicator()                                                                # if signal up = 1;
    df['signal down'] = INDICATOR_psar.psar_down_indicator()                                                            # if signal down = 1;

    df['highest'] = 0                                                                                                  # COLOCANDO AQUI O HIGHEST/LOWEST PARA ECONOMIZAR TEMPO
    df['highest'] = df['highest'].astype(float)
    df['lowest'] = 0
    df['lowest'] = df['lowest'].astype(float)

    lowest = 0
    highest = 0
    for index in range(1, len(df.index)):                                                                               #IDENTIFICANDO EXTREMO OPOSTO DO PSAR ATUAL

        if not pd.isna(df.at[index, 'psar up']):
            lowest = 0
            if highest != 0:
                highest = max(df.at[index, 'high'], highest)                                                           #para ajustar em momentos que n volta para minima
                #highest = df.at[index, 'high']
                df.at[index, 'highest'] = highest
            else:
                highest = df.at[index, 'high']
                df.at[index, 'highest'] = highest

        elif not pd.isna(df.at[index, 'psar down']):
            highest = 0
            if lowest != 0:
                lowest = min(df.at[index, 'low'], lowest)                                                              #para ajustar em momentos que n volta para minima
                #lowest = df.at[index, 'low']
                df.at[index, 'lowest'] = lowest
            else:
                lowest = df.at[index, 'low']
                df.at[index, 'lowest'] = lowest

    return df


def PSAR_major(dataframe, step=0.00001, max_step=50):
    df = dataframe.copy(deep=True)                                                                                      ##CRIA COPIA DA DF PARA TRABALHAR
    INDICATOR_psar = PSAR_slow(df['high'], df['low'], df['close'], step, max_step)                                      ##PSAR LONGO

    df['psar'] = INDICATOR_psar.psar()
    df['psar up'] = INDICATOR_psar.psar_up()
    df['psar down'] = INDICATOR_psar.psar_down()
    df['signal up'] = INDICATOR_psar.psar_up_indicator()                                                                # if signal up = 1;
    df['signal down'] = INDICATOR_psar.psar_down_indicator()                                                            # if signal down = 1;

    df['highest'] = 0                                                                                                  # COLOCANDO AQUI O HIGHEST/LOWEST PARA ECONOMIZAR TEMPO
    df['highest'] = df['highest'].astype(float)
    df['lowest'] = 0
    df['lowest'] = df['lowest'].astype(float)

    lowest = 0
    highest = 0
    for index in range(1, len(df.index)):                                                                               #IDENTIFICANDO EXTREMO OPOSTO DO PSAR ATUAL

        if not pd.isna(df.at[index, 'psar up']):
            lowest = 0
            if highest != 0:
                highest = max(df.at[index, 'high'], highest)                                                           #para ajustar em momentos que n volta para minima
                #highest = df.at[index, 'high']
                df.at[index, 'highest'] = highest
            else:
                highest = df.at[index, 'high']
                df.at[index, 'highest'] = highest

        elif not pd.isna(df.at[index, 'psar down']):
            highest = 0
            if lowest != 0:
                lowest = min(df.at[index, 'low'], lowest)                                                              #para ajustar em momentos que n volta para minima
                #lowest = df.at[index, 'low']
                df.at[index, 'lowest'] = lowest
            else:
                lowest = df.at[index, 'low']
                df.at[index, 'lowest'] = lowest

    return df


def PSAR_signals_df(dataframe):                                                                                                #RANGE ONLY
    data = []
    df = dataframe.copy(deep=True)                                                                                      ##COPIA PARA MANIPULAR
    df_list = df.values.tolist()
    for index in range(1, len(df.index)):                                                                               #CRIAÇÃO DE DF MÃE DOS SINAIS
        if df.at[index, 'signal up'] != 0 or df.at[index, 'signal down'] != 0:                                          #CRIAÇÃO DE DF MÃE DOS SINAIS
            if df.at[index, 'signal up'] != 0:
                list = df_list[index-1]
                data.append(list)

            elif df.at[index, 'signal down'] != 0:
                list = df_list[index-1]
                data.append(list)


    signals_dataframe = pd.DataFrame(data=data,
                             columns=['timestamp', 'open', 'high', 'low', 'close', 'psar', 'psar up', 'psar down',
                                      'signal up', 'signal down', 'highest', 'lowest'])
    signals_dataframe.drop(columns=['signal up', 'signal down'], inplace=True)                                          #CRIAÇÃO DE DF MÃE DOS SINAIS

    signals_closed_points = 0
    signals_closed_n = 0
    signals_open_points = 0                                                                                             #PARA CALCULAR DISTANCIA MEDIA DOS TIPOS DE SINAIS
    signals_open_n = 0
    for index in range(1, len(signals_dataframe)):
        current_psar_up = signals_dataframe.at[index, 'psar up']
        current_psar_down = signals_dataframe.at[index, 'psar down']
        previous_psar_up = signals_dataframe.at[index-1, 'psar up']
        previous_psar_down = signals_dataframe.at[index-1, 'psar down']
        if signals_dataframe.at[index-1, 'highest'] != 0 or signals_dataframe.at[index-1, 'lowest'] != 0:               #PULANDO PRIMEIRO SINAL PQ BUGARIA LOOP
            if current_psar_up <= previous_psar_down:                                                                   ##SINAIS FECHADOS
                signals_closed_points += abs(current_psar_up - previous_psar_down)                                      ##SINAIS FECHADOS
                signals_closed_n += 1                                                                                   ##SINAIS FECHADOS
            elif current_psar_down >= previous_psar_up:                                                                 ##SINAIS FECHADOS
                signals_closed_points += abs(current_psar_down - previous_psar_up)                                      ##SINAIS FECHADOS
                signals_closed_n += 1                                                                                   ##SINAIS FECHADOS

            elif current_psar_up > previous_psar_down:
                signals_open_points += abs(current_psar_up - previous_psar_down)
                signals_open_n += 1
            elif current_psar_down < previous_psar_up:
                signals_open_points += abs(current_psar_down - previous_psar_up)
                signals_open_n += 1

    delta_closed = signals_closed_points/signals_closed_n
    delta_open = signals_open_points/signals_open_n

    return delta_closed, delta_open, signals_dataframe


timestamp = None
def ORDERS_range_short(df_major, df_minor, delta):
    global timestamp
    print("\nChecking for **RANGE SHORT** signals")

    if timestamp != df_major['timestamp'].iloc[-1]:
        timestamp = df_major['timestamp'].iloc[-1]

        if not pd.isna(df_major['psar up'].iloc[-1]):
            if df_minor['signal up'].iloc[-1] != 0:
                order_market = EXCHANGE.create_market_sell_order(symbol=TICKER, amount=LOT)
                market = EXCHANGE.fetch_ticker(symbol=TICKER)

                price_tp = float(market['bid']) - delta*DELTA_X
                price_tp_format = EXCHANGE.price_to_precision(symbol=TICKER, price=price_tp)
                order_tp = EXCHANGE.create_limit_buy_order(symbol=TICKER, amount=LOT, price=price_tp_format)
                print('\nMAJOR UP // MINOR UP // Range SELL...: ', order_market)
                print('MAJOR UP // MINOR UP // Range SELL TP...: ', order_tp)


def BOT_run():
    print('________________________________________________________________________________________')
    print(f"\nFetching new bars for {datetime.now().isoformat()}")
    BARS_ohlc = EXCHANGE.fetch_ohlcv(symbol=TICKER, timeframe=TIMEFRAME, limit=CANDLE_limit, since=CANDLE_since)        #REQUEST OHLC

    ###MAIN DATA ORGANIZE
    BARS_ohlc_df = pd.DataFrame(data=BARS_ohlc[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])   #FRAME DATA // "data=BARS_ohlc[:-1]'' exclui barra em andamento
    BARS_ohlc_df.drop(columns='volume', inplace=True)                                                                   #REMOVE VOLUME
    BARS_ohlc_df['timestamp'] = pd.to_datetime(BARS_ohlc_df['timestamp'], unit='ms')                                    #UNIX TIMESTAMP TO DATE
    ###MAIN DATA ORGANIZE

    PSAR_data_minor = PSAR_minor(BARS_ohlc_df, PSAR_step, PSAR_max_step)

    PSAR_data_major = PSAR_major(BARS_ohlc_df, PSAR_step, PSAR_max_step)                                                ##SOMENTE PEGAR MEDIAS PARA MAJOR
    DELTA_closed, DELTA_open, SIGNALS_df = PSAR_signals_df(PSAR_data_major)                                             ##SOMENTE PEGAR MEDIAS PARA MAJOR
    ORDERS_range_short(df_major=PSAR_data_major, df_minor=PSAR_data_minor, delta=DELTA_closed)



    print(PSAR_data_major.tail(5))
    print(PSAR_data_minor.tail(5))
    print(SIGNALS_df.tail(5))
    print('\nDELTA Closed: ', DELTA_closed)
    print('DELTA Open: ', DELTA_open)

try:
    schedule.every(5).seconds.do(BOT_run)
except Exception as e:
    print('ERROR: ', e)
    pass

while True:
    schedule.run_pending()
    time.sleep(1)

