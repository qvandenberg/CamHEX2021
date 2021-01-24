import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# %matplotlib inline
import seaborn as sns

sns.set(style='darkgrid', context='talk', palette='Dark2')


class MovingAverage:

    def __init__(self, start_date, end_date, window_short=20, window_long=500):
        self.window_short = window_short
        self.window_long = window_long
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

    def simple(self, data, price_column='price'):
        """Extract price and calculate short and long MAs -- TODO: set time for rolling function"""
        print('- Calculating MAs')
        results = {'real': [], 'short': [], 'long': []}
        data = self.read_data(data)
        data = data.rolling(window='60T').mean()
        # Calculating the short-window simple moving average
        short_rolling = data.rolling(window=self.window_short).mean()
        # Calculating the long-window simple moving average
        long_rolling = data.rolling(window=self.window_long, min_periods=1).mean()
        # extract values
        results['real'] = (data.index, data[price_column])  # Price
        results['short'] = (long_rolling.index, long_rolling[price_column])
        results['long'] = (short_rolling.index, short_rolling[price_column])
        return results

    def exponential(self, data, span_short, span_long, price_column='price'):
        data = self.read_data(data)
        results = {'real': [], 'short': [], 'long': []}
        # Calculating the short-window simple moving average
        short_rolling = data.rolling(window=self.window_short).mean()
        # Calculating the long-window simple moving average
        long_rolling = data.rolling(window=self.window_long, min_periods=1).mean()
        # Exponential weighted mean
        ema_short = short_rolling.ewm(span=span_short, adjust=False).mean()
        ema_long = long_rolling.ewm(span=span_long, adjust=False).mean()
        results['short'] = (ema_short.index, ema_short[price_column])
        results['long'] = (ema_long.index, ema_long[price_column])
        return results

    def read_data(self, data, time_column='time', date_column='date', timestamp_column='Timestamp'):
        data = pd.read_csv(data)
        data.columns = [x.strip() for x in data.columns]
        print(data)
        # print(timestamp_column not in data.columns)
        # exit()
        if timestamp_column not in data.columns:
            # Generating timestamp from date and time column
            data[timestamp_column] = pd.to_datetime(data[date_column] + ' ' + data[time_column],
                                                    format='%Y-%m-%d %H:%M:%S')
        data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        # date limit
        data = data[(data[timestamp_column] >= self.start_date) & (data[timestamp_column] <= self.end_date)]
        data.set_index(timestamp_column, inplace=True)

        return data

    def plot_sma(self, ma_res, instr):
        """ [WGN] matplotlib not present in IDE environment
        Plot short and long MS and the real price.
        """
        print('- Plotting')
        fig, ax = plt.subplots(figsize=(16, 9))
        # ax.set_ylim(bottom=0.0, top=200.0)
        for ma_type, res in ma_res.items():
            for span, timestamp_price in res.items():
                if not timestamp_price:
                    continue
                print(timestamp_price)
                label = ma_type + '_' + span
                if 'real' in label:
                    label = 'real'
                ax.plot(timestamp_price[0], timestamp_price[1], label=label)
        ax.legend(loc='best')
        ax.set_ylabel('Price in £')
        plt.title(instr)
        plt.show()


if __name__ == '__main__':
    ma = MovingAverage(window_short='20T', window_long="500T", start_date='2021-01-22', end_date='2021-01-24')
    moving_average = {}
    moving_average['simple'] = ma.simple(data='data/PHILIPS_B.csv')
    moving_average['exponential'] = ma.exponential(data='data/PHILIPS_B.csv', span_short=100, span_long=100)
    # print(moving_average)
    # print(res['long'], res['real'])
    # exit()
    ma.plot_sma(ma_res=moving_average, instr='PHILIPS_B')
