import matplotlib.pyplot as plt
import mplfinance as mpf
from binance.client import Client
from datetime import datetime, timedelta
from binance.client import Client
import pandas as pd

client = Client('b65854306de8d7181d8256a23f81e4fd64bb69b42ec6e32bebd429bdd7ca47ea',
                '4f7d67b539ebc3df31906f8962474c611bfd2abf20aec2c61e3eff11de6d6ba0')

def analyze_stock_data(symbol, timeframe):
    # Get candlestick data from Binance API
    klines = client.get_klines(symbol=symbol, interval=timeframe)
    df = pd.DataFrame(klines, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    # df['Close'] = df['Close'].astype(float)
    # df['Open'] = df['Open'].astype(float)
    df = df.drop(columns=['Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df = df.set_index('Time')

    # Determine market structure
    market_structure = []
    for i in range(1, len(df)):
        if df['High'][i] > df['High'][i - 1] and df['Low'][i] > df['Low'][i - 1]:
            market_structure.append('uptrend')
        elif df['High'][i] < df['High'][i - 1] and df['Low'][i] < df['Low'][i - 1]:
            market_structure.append('downtrend')
        else:
            market_structure.append('consolidation')

    # Determine break of structures
    break_structures = []
    for i in range(1, len(market_structure)):
        if market_structure[i] != market_structure[i - 1]:
            break_structures.append(market_structure[i])

    # Determine higher highs and higher lows
    hh = []
    hl = []
    for i in range(1, len(df)):
        if df['High'][i] > df['High'][i - 1]:
            hh.append(df['High'][i])
            hl.append(df['Low'][i - 1])

    # Determine lower lows and lower highs
    ll = []
    lh = []
    for i in range(1, len(df)):
        if df['Low'][i] < df['Low'][i - 1]:
            ll.append(df['Low'][i])
            lh.append(df['High'][i - 1])

    # Determine supply zones
    supply_zones = []
    for i in range(1, len(df)):
        if market_structure[i - 1] == 'uptrend' and market_structure[i] == 'downtrend':
            supply_zones.append({'time': df.index[i], 'value': df['High'][i]})

    # Determine demand zones
    demand_zones = []
    for i in range(1, len(df)):
        if market_structure[i - 1] == 'downtrend' and market_structure[i] == 'uptrend':
            demand_zones.append({'time': df.index[i], 'value': df['Low'][i]})

    # Determine fair value and imbalance gaps

    gaps = []
    for i in range(1, len(df)):
        if df['Close'][i] > df['Open'][i]:
            gap = df['Open'][i] - df['Low'][i - 1]
            if gap > 0:
                gaps.append({'start': df['Time'][i - 1], 'end': df['Time'][i], 'type': 'fair_value_gap'})
        else:
            gap = df['Close'][i] - df['Low'][i - 1]
            if gap > 0:
                gaps.append({'start': df['Time'][i - 1], 'end': df['Time'][i], 'type': 'imbalance_gap'})

    # Determine supply and demand zones
    # zones = []
    # for line in lines:
    #     if line[0]['value'] < line[1]['value']:
    #         supply_zone = {'start': line[0]['time'], 'end': line[1]['time'], 'type': 'supply_zone'}
    #         zones.append(supply_zone)
    #     else:
    #         demand_zone = {'start': line[2]['time'], 'end': line[3]['time'], 'type': 'demand_zone'}
    #         zones.append(demand_zone)

    # Plot the data with candles, market structure, gaps and zones
    fig, ax = plt.subplots(figsize=(16, 8))
    mpf.candlestick_ohlc(ax, df[['Time', 'Open', 'High', 'Low', 'Close']].values, width=0.001, colorup='g', colordown='r')
    for i in range(len(break_structures)):
        if break_structures[i] == 'uptrend':
            ax.axvline(x=df['Time'][i], color='g', linestyle='--')
        elif break_structures[i] == 'downtrend':
            ax.axvline(x=df['Time'][i], color='r', linestyle='--')
    # for line in lines:
    #     ax.plot([line[0]['time'], line[1]['time']], [line[0]['value'], line[1]['value']], color='k', linestyle='-')
    #     ax.plot([line[2]['time'], line[3]['time']], [line[2]['value'], line[3]['value']], color='k', linestyle='-')
    for zone in supply_zones:
        ax.axvspan(zone['start'], zone['end'], facecolor='b', alpha=0.1)
    for zone in demand_zones:
        ax.axvspan(zone['start'], zone['end'], facecolor='b', alpha=0.1)
    for gap in gaps:
        if gap['type'] == 'fair_value_gap':
            ax.axvspan(gap['start'], gap['end'], facecolor='g', alpha=0.3)
        elif gap['type'] == 'imbalance_gap':
            ax.axvspan(gap['start'], gap['end'], facecolor='r', alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.autoscale_view()
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()

def plot_chart(symbol, interval, start_time, end_time):
    # Get the candlestick data
    klines = client.futures_klines(symbol=symbol, interval=interval, startTime=start_time, endTime=end_time)
    # Convert the data to a pandas dataframe
    df = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                       'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                                       'Taker buy quote asset volume', 'Ignore'])

    # Convert the timestamps to datetime objects
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df['Close time'] = pd.to_datetime(df['Close time'], unit='ms')

    # Calculate the market structure, higher highs, higher lows, lower highs, lower lows, supply zones, demand zones
    lines = analyze_stock_data(df)

    # Plot the chart
    mpf.plot(df, type='candle', volume=True, style='yahoo', addplot=lines)

if __name__ == '__main__':
    analyze_stock_data('BTCUSDT', '4h')
