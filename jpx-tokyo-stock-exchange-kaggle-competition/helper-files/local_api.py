import pandas as pd, os, numpy as np

def calc_spread_return_per_day(df, portfolio_size, toprank_weight_ratio):
    """
    Args:
        df (pd.DataFrame): predicted results
        portfolio_size (int): # of equities to buy/sell
        toprank_weight_ratio (float): the relative weight of the most highly ranked stock compared to the least.
    Returns:
        (float): spread return
    """
    assert df['Rank'].min() == 0
    assert df['Rank'].max() == len(df['Rank']) - 1
    weights = np.linspace(start=toprank_weight_ratio, stop=1, num=portfolio_size)
    purchase = (df.sort_values(by='Rank')['Target'][:portfolio_size] * weights).sum() / weights.mean()
    short = (df.sort_values(by='Rank', ascending=False)['Target'][:portfolio_size] * weights).sum() / weights.mean()
    return purchase - short

def calc_spread_return_sharpe(df: pd.DataFrame, portfolio_size: int = 200, toprank_weight_ratio: float = 2) -> float:
    """
    Args:
        df (pd.DataFrame): predicted results
        portfolio_size (int): # of equities to buy/sell
        toprank_weight_ratio (float): the relative weight of the most highly ranked stock compared to the least.
    Returns:
        (float): sharpe ratio
    """
    buf = df.groupby('Date').apply(calc_spread_return_per_day, portfolio_size, toprank_weight_ratio)
    sharpe_ratio = buf.mean() / buf.std()
    return sharpe_ratio, buf

class iter_test():
    def __init__(self, prices, options, financials, trades, secondary_prices, myapi):
        self.myapi = myapi
        self.dates = sorted(list(prices['Date'].unique()))
        self.prices = prices.groupby('Date')
        self.options = options.groupby('Date')
        self.financials = financials.groupby('Date')
        self.trades = trades.groupby('Date')
        self.secondary_prices = secondary_prices.groupby('Date')
        self.idx = 0
    def __next__(self):
        if self.idx == len(self.dates):
            self.myapi.submission = pd.concat(self.myapi.submission)
            os.getcwd()
            self.myapi.submission.to_csv('local_submission.csv', index=False)
            self.idx = 0
            raise StopIteration
        else:
            prices = self.prices.get_group(self.dates[self.idx])
            options = self.options.get_group(self.dates[self.idx])
            financials = self.financials.get_group(self.dates[self.idx])
            trades = self.trades.get_group(self.dates[self.idx])
            secondary_prices = self.secondary_prices.get_group(self.dates[self.idx])
            sample_submission = pd.DataFrame(prices['Date'].copy(), columns = ['Date'])
            sample_submission['SecuritiesCode'] = prices['SecuritiesCode'].copy()
            self.idx += 1
            return prices, options, financials, trades, secondary_prices, sample_submission.reset_index(drop=True)
    def __iter__(self):
        return self
    def __len__(self):
        return len(self.dates)

class local_api():
    def __init__(self, data_dir, start_date='2021-12-06', end_date='2022-02-28'):
        """
        This module simulates the online API in a local environment, in order for people to estimate running time and memory.
        Parameters:
            data_dir: directory in which data files are stored.
            start_date: str, evaluation starting date.
            end_date: str, evaluation ending date.
        """
        self.prices = pd.read_csv(os.path.join(data_dir, 'stock_prices.csv'))
        self.options = pd.read_csv(os.path.join(data_dir, 'options.csv'))
        self.financials = pd.read_csv(os.path.join(data_dir, 'financials.csv'))
        self.trades = pd.read_csv(os.path.join(data_dir, 'trades.csv'))
        self.secondary_prices = pd.read_csv(os.path.join(data_dir, 'secondary_stock_prices.csv'))
        self.prices = self.prices.loc[(self.prices['Date'] >= start_date) & (self.prices['Date'] <= end_date)]
        self.options = self.options.loc[(self.options['Date'] >= start_date) & (self.options['Date'] <= end_date)]
        self.financials = self.financials.loc[(self.financials['Date'] >= start_date) & (self.financials['Date'] <= end_date)]
        self.trades = self.trades.loc[(self.trades['Date'] >= start_date) & (self.trades['Date'] <= end_date)]
        self.secondary_prices = self.secondary_prices.loc[(self.secondary_prices['Date'] >= start_date) &\
                                                (self.secondary_prices['Date'] <= end_date)]
        self.gt_prices = self.prices[['Date', 'SecuritiesCode', 'Target']].copy()
        self.prices.drop(['Target'], inplace=True, axis = 1)
    def make_env(self):
        return self
    def iter_test(self):
        self.submission = []
        return iter_test(self.prices, self.options, self.financials, self.trades, self.secondary_prices, self)
    def predict(self, prediction):
        self.submission.append(prediction)
    def score(self):
        return calc_spread_return_sharpe(self.submission.merge(self.gt_prices))[0]