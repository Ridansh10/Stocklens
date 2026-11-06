import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

def get_data(tickers, start, end) -> pd.DataFrame:
    """Return a DataFrame of Close prices with one column per ticker."""
    if isinstance(tickers, str):
        tickers = [tickers]
        # Deduplicate tickers while keeping the original order
    tickers = list(dict.fromkeys(tickers)) 
    data = yf.download(tickers, start=start, end=end, progress=False)
    if data.empty:
        return pd.DataFrame()
    # yfinance returns different column structures depending on whether you request one ticker or multiple. 
    # We normalize both cases here so the rest of the app always gets a clean, predictable DataFrame.
    if isinstance(data.columns, pd.MultiIndex):
        if "Close" in data.columns.get_level_values(0):
            close = data["Close"]
        elif "Close" in data.columns.get_level_values(1):
            close = data.xs("Close", level=1, axis=1)
        else:
            close = data.xs("Close", axis=1, level=-1)
        if isinstance(close, pd.Series):
            close = close.to_frame()
    else:
        if "Close" in data.columns:
            close = data["Close"]
        else:
            close = data
        if isinstance(close, pd.Series):
            close = close.to_frame(name=tickers[0])
    if len(tickers) == 1 and len(close.columns) == 1:
        close.columns = [tickers[0]]
    else:
        if isinstance(close.columns, pd.MultiIndex):
            close.columns = [column[-1] for column in close.columns]
        else:
            close.columns = [str(column) for column in close.columns]

    existing = [ticker for ticker in tickers if ticker in close.columns]
    return close[existing].dropna(how="all")

def lookup_ticker(company_name):
    try:
        search = yf.Search(company_name)
        if search.quotes:
            return search.quotes[0].get("symbol")
    except Exception:
        return None
    return None

def calculate_returns(prices):
    return prices.pct_change().dropna()

def calculate_moving_average(prices, window):
    return prices.rolling(window=window).mean()

def normalize_prices(prices):
    return (prices / prices.iloc[0]) * 100

def calculate_volatility(returns, window=30):
    # Annualized volatility: standard deviation of returns multiplied by the 
    # square root of 252 (the standard number of trading days in a year).
    return returns.rolling(window=window).std() * np.sqrt(252)

def calculate_drawdown(prices):
    running_max = prices.cummax()
    return (prices - running_max) / running_max

def finish_chart(figure):
    """Apply consistent styling to all charts."""
    figure.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        colorway=["#0f172a", "#6366f1", "#0ea5e9"],
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", title=""),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", title=""),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

def plot_stock_trends(prices: pd.DataFrame):
    charts = {
        "price": go.Figure(),
        "ma20": go.Figure(),
        "ma50": go.Figure(),
        "normalized": go.Figure(),
        "volatility": go.Figure(),
        "drawdown": go.Figure(),
    }
    for ticker in prices.columns:
        ticker_prices = prices[ticker].dropna()
        if ticker_prices.empty:
            continue
        ma20 = calculate_moving_average(ticker_prices, 20)
        ma50 = calculate_moving_average(ticker_prices, 50)
        normalized = normalize_prices(ticker_prices)
        returns = calculate_returns(ticker_prices)
        volatility = calculate_volatility(returns)
        drawdown = calculate_drawdown(ticker_prices)
        chart_data = {
            "price": ticker_prices,
            "ma20": ma20,
            "ma50": ma50,
            "normalized": normalized,
            "volatility": volatility,
            "drawdown": drawdown,
        }
        for chart_name, values in chart_data.items():
            charts[chart_name].add_trace(
                go.Scatter(
                    x=values.index,
                    y=values,
                    mode="lines",
                    name=ticker,
                )
            )
    for chart in charts.values():
        finish_chart(chart)
    return (
        charts["price"],
        charts["ma20"],
        charts["ma50"],
        charts["normalized"],
        charts["volatility"],
        charts["drawdown"],
    )