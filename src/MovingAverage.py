#!/usr/bin/env python
"""
Author: Raquel Manzano <https://github.com/RaqManzano>
Date: 23 Jan 2021
Script: Scripts generated for Hex Cambridge Hackathon.
Using a csv file with a trading history it will calculate simple and exponential moving averages
Input needs Timestamp and price column minimum.
TODO: set an appropiate time for rolling functions
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

sns.set(style='darkgrid', context='talk', palette='Dark2')


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', help='CSV input file', default="../data/PHILIPS_B.csv")
    parser.add_argument('--short_window', help='Window time for short SMA',default='20T')
    parser.add_argument('--long_window', help='Window time for long SMA', default='500T')
    parser.add_argument('--short_span', help='Window time for short EMA', default=100, type=int)
    parser.add_argument('--long_span', help='Window time for short EMA', default=500, type=int)
    parser.add_argument('--plot_out', help='If set will generate a png into a file with the same base name as CSV',
                        action="store_true")
    return parser.parse_args()


class MovingAverage:

    def __init__(self, start_date, end_date, window_short=20, window_long=500):
        self.window_short = window_short
        self.window_long = window_long
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

    def simple(self, data, price_column='price'):
        """Extract price and calculate short and long Simple Moving Average"""
        print('- Calculating SMAs')
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
        """Extract price and calculate short and long Simple Moving Average"""
        print('- Calculating EMAs')
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
        if timestamp_column not in data.columns:
            # Generating timestamp from date and time column
            data[timestamp_column] = pd.to_datetime(data[date_column] + ' ' + data[time_column],
                                                    format='%Y-%m-%d %H:%M:%S')
        data[timestamp_column] = pd.to_datetime(data[timestamp_column])
        # date limit
        data = data[(data[timestamp_column] >= self.start_date) & (data[timestamp_column] <= self.end_date)]
        data.set_index(timestamp_column, inplace=True)

        return data

    def plot_ma(self, ma_res, instr, plot_out=False):
        """ Plot short and long MS and the real price."""
        print('- Plotting')
        fig, ax = plt.subplots(figsize=(16, 9))
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
        if plot_out:
            plt.savefig(instr.replace('.csv', '.png'))
        else:
            plt.show()


if __name__ == '__main__':
    args = argparser()
    ma = MovingAverage(start_date='2021-01-22', end_date='2021-01-24',
                       window_short=args.short_window, window_long=args.long_window)
    moving_average = {}
    moving_average['simple'] = ma.simple(data=args.csv)
    moving_average['exponential'] = ma.exponential(data=args.csv, span_short=args.short_span, span_long=args.long_span)
    ma.plot_ma(ma_res=moving_average, instr=args.csv, plot_out=args.plot_out)
