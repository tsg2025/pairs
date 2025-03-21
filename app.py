import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# Function to calculate z-score
def calculate_zscore(series, lookback):
    mean = series.rolling(window=lookback).mean()
    std = series.rolling(window=lookback).std()
    zscore = (series - mean) / std
    return zscore

# Function to calculate RSI
def calculate_rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate trading metrics
def calculate_metrics(trades):
    if len(trades) == 0:
        return {}
    
    trades['PnL'] = trades['Exit Price'] - trades['Entry Price']
    total_pnl = trades['PnL'].sum()
    win_rate = (trades['PnL'] > 0).mean() * 100
    sharpe_ratio = trades['PnL'].mean() / trades['PnL'].std() * np.sqrt(252)  # Annualized
    max_drawdown = (trades['PnL'].cumsum().cummax() - trades['PnL'].cumsum()).max()
    avg_trade_duration = (trades['Exit Date'] - trades['Entry Date']).mean()
    
    metrics = {
        "Total PnL": total_pnl,
        "Number of Trades": len(trades),
        "Win Rate (%)": win_rate,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Average Trade Duration": avg_trade_duration
    }
    return metrics

# Streamlit app
st.title("Pair Trading Backtesting")

# Input boxes
st.sidebar.header("Input Parameters")
symbol1 = st.sidebar.text_input("Enter Stock Symbol 1", "AAPL")
symbol2 = st.sidebar.text_input("Enter Stock Symbol 2", "MSFT")
lookback = st.sidebar.number_input("Lookback Period for Z-Score", min_value=1, value=30)
rsi_period = st.sidebar.number_input("RSI Period (Optional)", min_value=1, value=14)
use_rsi = st.sidebar.checkbox("Enable RSI Filter")
from_date = st.sidebar.text_input("From Date (YYYY-MM-DD)", "2020-01-01")
to_date = st.sidebar.text_input("To Date (YYYY-MM-DD)", "2023-01-01")
entry_deviation = 2.5  # Fixed as per requirement
exit_deviation = 1.5   # Fixed as per requirement

# Go button
if st.sidebar.button("Go"):
    # Fetch data
    data1 = yf.download(symbol1, start=from_date, end=to_date)
    data2 = yf.download(symbol2, start=from_date, end=to_date)
    
    # Calculate ratio and z-score
    data1['Close'] = data1['Adj Close']
    data2['Close'] = data2['Adj Close']
    ratio = data1['Close'] / data2['Close']
    zscore = calculate_zscore(ratio, lookback)
    
    # Calculate RSI (if enabled)
    if use_rsi:
        rsi = calculate_rsi(data1['Close'], rsi_period)
    else:
        rsi = None
    
    # Backtesting logic
    trades = []
    position = None  # None, 'long', or 'short'
    for i in range(lookback, len(data1)):
        if position is None:
            # Entry logic
            if zscore[i] > entry_deviation and (not use_rsi or rsi[i] > 70):
                position = 'short'
                entry_price = data1['Close'][i] - data2['Close'][i]
                entry_date = data1.index[i]
            elif zscore[i] < -entry_deviation and (not use_rsi or rsi[i] < 30):
                position = 'long'
                entry_price = data2['Close'][i] - data1['Close'][i]
                entry_date = data1.index[i]
        else:
            # Exit logic
            if (position == 'short' and zscore[i] < exit_deviation) or \
               (position == 'long' and zscore[i] > -exit_deviation):
                exit_price = data1['Close'][i] - data2['Close'][i] if position == 'short' else data2['Close'][i] - data1['Close'][i]
                exit_date = data1.index[i]
                trades.append({
                    "Entry Date": entry_date,
                    "Exit Date": exit_date,
                    "Entry Price": entry_price,
                    "Exit Price": exit_price,
                    "Position": position
                })
                position = None
    
    # Convert trades to DataFrame
    trades_df = pd.DataFrame(trades)
    
    # Calculate metrics
    metrics = calculate_metrics(trades_df)
    
    # Display results
    st.subheader("Backtest Results")
    st.write("### Trades")
    st.dataframe(trades_df)
    
    st.write("### Metrics")
    st.write(pd.DataFrame.from_dict(metrics, orient='index', columns=['Value']))
    
    st.write("### Z-Score Series")
    st.line_chart(zscore)
    
    if use_rsi:
        st.write("### RSI Series")
        st.line_chart(rsi)

# GitHub integration (hosting)
st.sidebar.markdown("""
### Hosted on GitHub
[View on GitHub](https://github.com/your-repo/pair-trading-backtest)
""")
