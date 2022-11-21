#V3.1 --> ENTRA NO 5º SINAL

import ccxt
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

psar_step = 0.00001
psar_max_step = 50

###INPUTS OHLC CALL
ticker = input('TICKER [XXX/ZZZ]: ')
lot = float(input('LOT [float]: '))
timeframe = input('TIMEFRAME [1m, 1d, 1w, 1M]: ')                                                                                                                        #SET TO 0 TO INCREASE 1 LOT PER DAY
candle_limit = 5000 #int(input('AMOUNT OF CANDLES [INT or 0]: ')) ##PARAMETERS MUST BE INT
if candle_limit == 0:
    candle_limit = None
candle_since = 0 #int(input('AMOUNT OF TIME [UNIX or 0]: ')) ##PARAMETERS MUST BE INT
if candle_since == 0:
    candle_since = None
###INPUTS OHLC CALL

EXCHANGE = ccxt.ftx({                                                                                                   ##EXCHANGE SETUP
    'apiKey': config.FTX_API_KEY_Synapse_T_Longs,                                                                                       ##EXCHANGE SETUP
    'secret': config.FTX_API_SECRET_Synapse_T_Longs,                                                                                    ##EXCHANGE SETUP
    'enableRateLimit': True,                                                                                            ##EXCHANGE SETUP
    'options': {'fetchMinOrderAmounts': False},
    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_Synapse_T_Longs}                                                            ##EXCHANGE SETUP
})

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
                #highest = psar_df.at[index, 'high']
                df.at[index, 'highest'] = highest
            else:
                highest = df.at[index, 'high']
                df.at[index, 'highest'] = highest

        elif not pd.isna(df.at[index, 'psar down']):
            highest = 0
            if lowest != 0:
                lowest = min(df.at[index, 'low'], lowest)                                                              #para ajustar em momentos que n volta para minima
                #lowest = psar_df.at[index, 'low']
                df.at[index, 'lowest'] = lowest
            else:
                lowest = df.at[index, 'low']
                df.at[index, 'lowest'] = lowest

    return df


def PSAR_signals_df(dataframe):                                                                                         ###MODIFICADO PARA SYNAPSE 3.0. ORIGINAL EM '[STATISTICS]'
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
                signals_dataframe.at[index, 'type'] = 1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_highest - previous_psar_down)
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep




            elif current_psar_down >= previous_psar_up:                                                                 ##SINAIS FECHADOS
                delta_signals = abs(current_psar_down - previous_psar_up)                                                                    ##SINAIS FECHADOS
                signals_dataframe.at[index, 'type'] = 1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_lowest - previous_psar_up)
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep

            elif current_psar_up > previous_psar_down:
                delta_signals = abs(current_psar_up - previous_psar_down)
                signals_dataframe.at[index, 'type'] = -1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_highest - previous_psar_down)
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep

            elif current_psar_down < previous_psar_up:
                delta_signals = abs(current_psar_down - previous_psar_up)
                signals_dataframe.at[index, 'type'] = -1
                signals_dataframe.at[index, 's_delta'] = delta_signals

                delta_trigger_ep = abs(current_lowest - previous_psar_up)
                signals_dataframe.at[index, 'ep_s_delta'] = delta_trigger_ep


    return signals_dataframe

timestamp = None
order_sl = 0
count = 0
def ORDERS_trend_long(psar_df, signals_df):
    global timestamp, order_sl, count
    print('\nChecking for **TREND LONG** signals')

    if timestamp != psar_df['timestamp'].iloc[-1]:
        timestamp = psar_df['timestamp'].iloc[-1]

        if not pd.isna(psar_df['psar down'].iloc[-1]) and not pd.isna(psar_df['psar up'].iloc[-2]):
            if signals_df['type'].iloc[-1] == -1:

                delta = abs(float(signals_df['psar up'].iloc[-1]) - float(signals_df['lowest'].iloc[-2])) ##PEGAR O CRUZAMENTO QUE TEVE MAIS O EXTREME POINT ANTERIOR
                count += 1
                order_sl += delta
                print('******** LONG COUNT: ', count)

                if count == 5:
                    order_data = EXCHANGE.create_market_buy_order(symbol=ticker, amount=lot)
                    print('\nBUY ORDER CREATED: ', order_data, '\nID: ', int(order_data['info']['id']))

                    fetch_ticker = EXCHANGE.fetch_ticker(symbol=ticker)
                    ticker_last = float(fetch_ticker['last'])

                    sl = ticker_last - order_sl
                    sl_format = EXCHANGE.price_to_precision(symbol=ticker, price=sl)
                    sl_data = EXCHANGE.create_order(symbol=ticker, type='stop', side='sell', amount=lot, params={'triggerPrice': sl_format, 'reduceOnly': True})
                    print('SL[sell] ORDER CREATED: ', sl_data, '\nID: ', int(sl_data['info']['id']))

                    count = 0
                    order_sl = 0



def BOT_run():
    print('________________________________________________________________________________________')
    print(f"\nFetching new bars for {datetime.now().isoformat()}")
    BARS_ohlc = EXCHANGE.fetch_ohlcv(symbol=ticker, timeframe=timeframe, limit=candle_limit, since=candle_since)        #REQUEST OHLC

    ###MAIN DATA ORGANIZE
    BARS_ohlc_df = pd.DataFrame(data=BARS_ohlc[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])   #FRAME DATA // "data=BARS_ohlc[:-1]'' exclui barra em andamento
    BARS_ohlc_df.drop(columns='volume', inplace=True)                                                                   #REMOVE VOLUME
    BARS_ohlc_df['timestamp'] = pd.to_datetime(BARS_ohlc_df['timestamp'], unit='ms')                                    #UNIX TIMESTAMP TO DATE
    ###MAIN DATA ORGANIZE

    PSAR_data_major = PSAR_major(BARS_ohlc_df, psar_step, psar_max_step)                                                ##SOMENTE PEGAR MEDIAS PARA MAJOR
    SIGNALS_df = PSAR_signals_df(PSAR_data_major)                                                                       ##SOMENTE PEGAR MEDIAS PARA MAJOR


    print(PSAR_data_major.tail(5))
    print(SIGNALS_df.tail(5))
    ORDERS_trend_long(PSAR_data_major, SIGNALS_df)
    print('BOT RUN ', count)

schedule.every(5).seconds.do(BOT_run)


while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as error:
        print('SERVER ERROR:', error)
        continue