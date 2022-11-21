import ccxt
from PSAR_Major import PSARIndicator as PSAR_slow

import config
import openpyxl
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 20)
pd.set_option('display.precision', 6)
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
import time
import schedule

PSAR_step = 0.00001  #float(input('STEP [0.00001]: '))
PSAR_max_step = 50  #int(input('MAX STEP [50]: '))

###INPUTS OHLC CALL
TICKER = 'BTC/USD'
TIMEFRAME = input('TIMEFRAME [1m, 1d, 1w, 1M]: ')
CANDLE_limit = 5000 #int(input('AMOUNT OF CANDLES [INT or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_limit == 0:
    CANDLE_limit = None
CANDLE_since = 0 #int(input('AMOUNT OF TIME [UNIX or 0]: ')) ##PARAMETERS MUST BE INT
if CANDLE_since == 0:
    CANDLE_since = None
###INPUTS OHLC CALL


###LOAD MARKETS
EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY_Synapse_R,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET_Synapse_R,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_Synapse_R}                                                            ##EXCHANGE SETUP
})                                                                                              ##EXCHANGE SETUP


def PSAR_major(dataframe, step=0.00001, max_step=50):
    df = dataframe.copy(deep=True)
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
            if df.at[index, 'signal up'] != 0:                                                                          ##CRIA LISTA, ANALISE SE O DADO ATUAL FOI UM GATILHO, DAI PEGA A ROW ANTERIOR, QUE FOI O ULTIMO DADO DO INDICADOR ANTES DO GATILHO
                list = df_list[index-1]
                data.append(list)

            elif df.at[index, 'signal down'] != 0:
                list = df_list[index-1]
                data.append(list)


    signals_dataframe = pd.DataFrame(data=data,
                             columns=['timestamp', 'open', 'high', 'low', 'close', 'psar', 'psar up', 'psar down',
                                      'signal up', 'signal down', 'highest', 'lowest'])
    signals_dataframe.drop(columns=['signal up', 'signal down'], inplace=True)                                          #CRIAÇÃO DE DF MÃE DOS SINAIS

    signals_dataframe['type'] = 0                                                                                       #SINAIS FECHADOS = 1; ABERTOS -1
    signals_dataframe['type'] = signals_dataframe['type'].astype(float)
    signals_dataframe['s_delta'] = 0                                                                                    #SIGNAL DELTA do atual sinal para o anterior
    signals_dataframe['s_delta'] = signals_dataframe['s_delta'].astype(float)
    signals_dataframe['ep_s_delta'] = 0                                                                                 #EP ATUAL PARA SIGNAL GATILHO ANTERIOR
    signals_dataframe['ep_s_delta'] = signals_dataframe['ep_s_delta'].astype(float)

    signals_closed_points = 0
    signals_closed_n = 0
    signals_open_points = 0                                                                                             #PARA CALCULAR DISTANCIA MEDIA DOS TIPOS DE SINAIS
    signals_open_n = 0

    delta_open_trigger_to_ep = 0
    delta_closed_trigger_to_ep = 0
    delta_open_trigger_to_n = 0
    delta_closed_trigger_to_n = 0

    for index in range(1, len(signals_dataframe)):
        current_psar_up = signals_dataframe.at[index, 'psar up']
        current_psar_down = signals_dataframe.at[index, 'psar down']
        previous_psar_up = signals_dataframe.at[index-1, 'psar up']
        previous_psar_down = signals_dataframe.at[index-1, 'psar down']

        current_highest = signals_dataframe.at[index, 'highest']
        current_lowest = signals_dataframe.at[index, 'lowest']

        if signals_dataframe.at[index-1, 'highest'] != 0 or signals_dataframe.at[index-1, 'lowest'] != 0:               #PULANDO PRIMEIRO SINAL PQ BUGARIA LOOP
            if current_psar_up <= previous_psar_down:                                                                   ##SINAIS FECHADOS
                delta_signals = abs(current_psar_up - previous_psar_down)
                signals_closed_points += delta_signals                                                                  ##SINAIS FECHADOS
                signals_closed_n += 1                                                                                   ##SINAIS FECHADOS
                signals_dataframe.at[index, 'type'] = 1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_highest - previous_psar_down)
                delta_closed_trigger_to_ep += delta_trigger_ep                                ##PONTO EXTREMO DESDE SINAL ANTERIOR
                delta_closed_trigger_to_n += 1
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep




            elif current_psar_down >= previous_psar_up:                                                                 ##SINAIS FECHADOS
                delta_signals = abs(current_psar_down - previous_psar_up)
                signals_closed_points += delta_signals                                     ##SINAIS FECHADOS
                signals_closed_n += 1                                                                                   ##SINAIS FECHADOS
                signals_dataframe.at[index, 'type'] = 1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_lowest - previous_psar_up)
                delta_closed_trigger_to_ep += delta_trigger_ep                                    ##PONTO EXTREMO DESDE SINAL ANTERIOR
                delta_closed_trigger_to_n += 1
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep

            elif current_psar_up > previous_psar_down:
                delta_signals = abs(current_psar_up - previous_psar_down)
                signals_open_points += delta_signals
                signals_open_n += 1
                signals_dataframe.at[index, 'type'] = -1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_highest - previous_psar_down)
                delta_open_trigger_to_ep += delta_trigger_ep                                   ##PONTO EXTREMO DESDE SINAL ANTERIOR
                delta_closed_trigger_to_n += 1
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep

            elif current_psar_down < previous_psar_up:
                delta_signals = abs(current_psar_down - previous_psar_up)
                signals_open_points += delta_signals
                signals_open_n += 1
                signals_dataframe.at[index, 'type'] = -1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_lowest - previous_psar_up)
                delta_open_trigger_to_ep += delta_trigger_ep                                     ##PONTO EXTREMO DESDE SINAL ANTERIOR
                delta_open_trigger_to_n += 1
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep

    delta_closed = signals_closed_points/signals_closed_n
    delta_open = signals_open_points/signals_open_n

    delta_closed_trigger_to_ep_average = delta_closed_trigger_to_ep/delta_closed_trigger_to_n
    delta_open_trigger_to_ep_average = delta_open_trigger_to_ep/delta_open_trigger_to_n

    return delta_closed, delta_open, signals_dataframe, signals_closed_n, signals_open_n, delta_closed_trigger_to_ep_average, delta_open_trigger_to_ep_average


def PSAR_signals_plot(dataframe, type=0, column='', bins=0.0):
    df = dataframe.copy(deep=True)
    if type == 1:
        for index in range(1, len(df.index)):
            if df.at[index, 'type'] != 1:
                df.drop(index=index, inplace=True)
    elif type == -1:
        for index in range(1, len(df.index)):
            if df.at[index, 'type'] != -1:
                df.drop(index=index, inplace=True)

    plt.hist(df[column], color='blue', edgecolor='black', bins=bins)
    plt.title('DELTA of Selected PSAR in Crypto')
    plt.xlabel('DELTA (USD)')
    plt.ylabel('Signals')
    plt.show()






def BOT_run():
    print('________________________________________________________________________________________')
    print(f"\nFetching new bars for {datetime.now().isoformat()}")
    BARS_ohlc = EXCHANGE.fetch_ohlcv(symbol=TICKER, timeframe=TIMEFRAME, limit=CANDLE_limit, since=CANDLE_since)        #REQUEST OHLC

    ###MAIN DATA ORGANIZE
    BARS_ohlc_df = pd.DataFrame(data=BARS_ohlc[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])   #FRAME DATA // "data=BARS_ohlc[:-1]'' exclui barra em andamento
    BARS_ohlc_df.drop(columns='volume', inplace=True)                                                                   #REMOVE VOLUME
    BARS_ohlc_df['timestamp'] = pd.to_datetime(BARS_ohlc_df['timestamp'], unit='ms')                                    #UNIX TIMESTAMP TO DATE
    ###MAIN DATA ORGANIZE

    PSAR_data_major = PSAR_major(BARS_ohlc_df, PSAR_step, PSAR_max_step)                                                ##SOMENTE PEGAR MEDIAS PARA MAJOR
    DELTA_closed, DELTA_open, SIGNALS_df, DELTA_closed_n, DELTA_open_n, DELTA_closed_ep_trigger, DELTA_open_ep_trigger = PSAR_signals_df(PSAR_data_major)                                             ##SOMENTE PEGAR MEDIAS PARA MAJOR
    PSAR_signals_plot(dataframe=SIGNALS_df, type=1, column='ep_s_delta', bins=50)
    PSAR_signals_plot(dataframe=SIGNALS_df, type=1, column='s_delta', bins=50)

    print(PSAR_data_major.head(5))
    print(PSAR_data_major.tail(5))
    print(SIGNALS_df.tail(5))
    print('\nCLOSED Delta: ', DELTA_closed, ' // ', DELTA_closed_n, '\nAVG EP-TRIGGER: ', DELTA_closed_ep_trigger)
    print('\nOPEN Delta: ', DELTA_open, ' // ', DELTA_open_n, '\nAVG EP-TRIGGER: ', DELTA_open_ep_trigger)

BOT_run()