import ccxt
import pandas as pd
import numpy as np
import os
import openpyxl

import config

###INPUTS DCA
CAPITAL = float(100000)
PERIOD = int(6000)
WEIGHT = float(1)
CAPITAL_perperiod = round(CAPITAL/PERIOD, 2)
###INPUTS DCA


###INPUTS OHLC CALL
TICKER = 'BTC/USD' #input('TICKER [XXX/YYY]: ')
TIMEFRAME = '1m' #input('TIMEFRAME [1m, 1d, 1w, 1M]: ')
CANDLE_limit = 6000 #int(input('AMOUNT OF CANDLES [INT or 0]: ')) ##PARAMETERS MUST BE INT
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
    'headers': {'FTX-SUBACCOUNT': config.FTX_SUBACCOUNT_DCA}                                                            ##EXCHANGE SETUP
})                                                                                                                      ##EXCHANGE SETUP
MARKETS = EXCHANGE.load_markets()                                                                                       ##LOAD DATA
###LOAD MARKETS
BARS_ohlc = EXCHANGE.fetch_ohlcv(symbol=TICKER, timeframe=TIMEFRAME, limit=CANDLE_limit, since=CANDLE_since)            #REQUEST OHLC



###MAIN DATA ORGANIZE
BARS_ohlc_df = pd.DataFrame(data=BARS_ohlc[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])       #FRAME DATA // "data=BARS_ohlc[:-1]'' exclui barra em andamento
BARS_ohlc_df.drop(columns='volume', inplace=True)                                                                            #REMOVE VOLUME
BARS_ohlc_df['timestamp'] = pd.to_datetime(BARS_ohlc_df['timestamp'], unit='ms')                                        #UNIX TIMESTAMP TO DATE
BARS_ohlc_df.reset_index(level=0, inplace=True)                                                                         #SET INDEX
##BARS_ohlc_df['previous open'] = BARS_ohlc_df['open'].shift(1)                                                         #SET PREVIOUS OPEN
##BARS_ohlc_df['previous close'] = BARS_ohlc_df['close'].shift(1)                                                       #SET PREVIOUS CLOSE
BARS_ohlc_df['%chg'] = abs((1 - BARS_ohlc_df['close']/BARS_ohlc_df['open']))                                            #SETADO EM DECIMAL
###MAIN DATA ORGANIZE


###DCA DATA ORGANIZE
BARS_ohlc_df['IDEAL Trade'] = CAPITAL_perperiod ##SET COLUMNS
BARS_ohlc_df['IDEAL Acum'] = 0                  ##SET COLUMNS
BARS_ohlc_df['REAL Trade'] = 0                  ##SET COLUMNS
BARS_ohlc_df['REAL Acum'] = 0                   ##SET COLUMNS

for index, data in BARS_ohlc_df.iterrows():                                                                             ##Dado em DF é passado como séries sendo a linha(index)...
                                                                                                                        ##... a capa do da lista de ''dicionários''...
                                                                                                                        ##...Portanto, para cada DATA internalizado em cada INDEX do DF... fazer:
    REAL_Trade_up = round(BARS_ohlc_df.at[index, 'IDEAL Trade'] -
                          ((BARS_ohlc_df.at[index, '%chg'] * WEIGHT) * BARS_ohlc_df.at[index, 'IDEAL Trade']), 2)       ##PARA VARIAVEL DE VELA EM ALTA
    REAL_Trade_down = round(BARS_ohlc_df.at[index, 'IDEAL Trade'] +
                            ((BARS_ohlc_df.at[index, '%chg'] * WEIGHT) * BARS_ohlc_df.at[index, 'IDEAL Trade']), 2)     ##PARA VARIAVEL DE VELA EM QUEDA

    if data['index'] == 0:

        BARS_ohlc_df.at[index, 'IDEAL Trade'] = round(CAPITAL_perperiod, 2)                                             ##ALTERANDO VALOR DA CELULA ATRAVÉS DE COMANDO QUE LOCALIZA POR X, Y
        BARS_ohlc_df.at[index, 'IDEAL Acum'] = round(CAPITAL_perperiod, 2)                                              ##ALTERANDO VALOR DA CELULA ATRAVÉS DE COMANDO QUE LOCALIZA POR X, Y

        if data['close'] >= data['open']:                                                                               ##SE FECHAMENTO EM ALTA, SUBTRAIR DO LOTE BASE
            #print(BARS_ohlc_df.at[index, '%chg'])
            BARS_ohlc_df.at[index, 'REAL Trade'] = REAL_Trade_up
            BARS_ohlc_df.at[index, 'REAL Acum'] = REAL_Trade_up

        elif data['close'] < data['open']:                                                                              ##SE FECHAMENTO EM QUEDA, SOMAR AO LOTE BASE
            #print(BARS_ohlc_df.at[index, '%chg'])
            BARS_ohlc_df.at['REAL Trade'] = REAL_Trade_down
            BARS_ohlc_df.at['REAL Acum'] = REAL_Trade_down

        BARS_ohlc_df['Prev.I.A'] = BARS_ohlc_df['IDEAL Acum'].shift(1)                                                  ##SETANDO PARA CALCULAR ACUMULADO EM LOOP PÓS ESTABELECIMENTO DE TODA LINHA
        BARS_ohlc_df['Prev.R.A'] = BARS_ohlc_df['REAL Acum'].shift(1)                                                   ##SETANDO PARA CALCULAR ACUMULADO EM LOOP PÓS ESTABELECIMENTO DE TODA LINHA

    else:

        BARS_ohlc_df.at[index, 'IDEAL Trade'] = round(CAPITAL_perperiod, 2)
        BARS_ohlc_df.at[index, 'IDEAL Acum'] = round(BARS_ohlc_df.at[index, 'IDEAL Trade'] + BARS_ohlc_df.at[index, 'Prev.I.A'], 2)

        if data['close'] >= data['open']:                                                                               ##SE FECHAMENTO EM ALTA, SUBTRAIR DO LOTE BASE
            #print(BARS_ohlc_df.at[index, '%chg'])
            BARS_ohlc_df.at[index, 'REAL Trade'] = REAL_Trade_up
            BARS_ohlc_df.at[index, 'REAL Acum'] = round(REAL_Trade_up + BARS_ohlc_df.at[index, 'Prev.R.A'], 2)

        elif data['close'] < data['open']:                                                                              ##SE FECHAMENTO EM QUEDA, SOMAR AO LOTE BASE
            #print(BARS_ohlc_df.at[index, '%chg'])
            BARS_ohlc_df.at[index, 'REAL Trade'] = REAL_Trade_down
            BARS_ohlc_df.at[index, 'REAL Acum'] = round(REAL_Trade_down + BARS_ohlc_df.at[index, 'Prev.R.A'], 2)

        BARS_ohlc_df['Prev.I.A'] = BARS_ohlc_df['IDEAL Acum'].shift(1)                                                  ##SETANDO PARA CALCULAR ACUMULADO EM LOOP PÓS ESTABELECIMENTO DE TODA LINHA
        BARS_ohlc_df['Prev.R.A'] = BARS_ohlc_df['REAL Acum'].shift(1)                                                   ##SETANDO PARA CALCULAR ACUMULADO EM LOOP PÓS ESTABELECIMENTO DE TODA LINHA


path = r'C:\Users\OFF\OneDrive\Documents\Syn.DeFi - Volatility DCA.xlsx'

book = openpyxl.load_workbook(path)
writer = pd.ExcelWriter(path, mode='a', engine='openpyxl', if_sheet_exists='replace')
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
BARS_ohlc_df.to_excel(writer, sheet_name='Database',)
writer.save()





print(BARS_ohlc_df)


















