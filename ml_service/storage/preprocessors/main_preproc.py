#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np


class Preprocessor:

    def preprocess(self, cursor):

        cols = ['ticker', 'per', 'date', 'time', 'open', 'high', 'low', 'close', 'vol']

        data = pd.DataFrame(columns=['price_open', 'price_max', 'price_min',
                                     'price_close', 'vol',
                                     'price_mean', 'price_std',
                                     'price_open_max_dif', 'price_open_min_dif',
                                     'price_max_min_dif', 'price_max_close_dif',
                                     'price_min_close_dif', 'price_open_prev_dif',
                                     'price_min_prev_dif', 'price_max_prev_dif',
                                     'price_close_prev_dif', 'vol_prev_dif',
                                     'price_mean_prev_dif',
                                     'price_close_open_dif'])

        while(1):
            try:
                minute_data = pd.DataFrame(cursor.fetchone(), columns=cols)
                for i in range(12):
                    row = cursor.fetchone
                    if row[2:4] != minute_data.iloc[0, 2:4]:
                        break
                    minute_data.append(row)
            except:
                break

            minute_data.drop(['ticker', 'per', 'date', 'time'], axis=1, inplace=True)

            x_series = pd.Series()
            x_series['price_open'] = minute_data.iloc[0]['open']
            x_series['price_max'] = minute_data['high'].max()
            x_series['price_min'] = minute_data['low'].min()
            x_series['price_close'] = minute_data.iloc[-1]['close']
            x_series['vol'] = minute_data['vol'].sum()
            x_series['price_mean'] = minute_data['open'].mean()
            x_series['price_std'] = minute_data['open'].std()

            price_features = ['open', 'max', 'min', 'close']
            x_series = self._make_difs(x_series, suffix='price_',
                                       features=price_features)

            if data.shape[0] != 0:
                for feature in ['price_open', 'price_min', 'price_max', 'vol']:
                    x_series[feature + '_prev_dif'] = \
                        x_series[feature] - data.iloc[-1][feature]

            data.append(x_series, ignore_index=True)

        return np.array(data)

    def _make_difs(self, x, suffix, features):
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                x[suffix + features[i] + '_' + features[j] + '_dif'] = \
                    x[suffix + features[i]] - x[suffix + features[j]]

        return x



