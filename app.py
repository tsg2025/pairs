import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import pytz

# Streamlit app details
st.set_page_config(page_title="Pair Trading Backtesting", layout="wide")

# Cache data fetching to improve performance
@st.cache_data
def fetch_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        if data.empty:
            raise ValueError(f"No data found for {ticker}")
        return data
    except Exception as e:
        st.error(f"Failed to fetch data for {ticker}: {e}")
        return None

# Function to calculate z-score
def calculate_zscore(series, lookback):
    mean = series.rolling(window=lookback).mean()
    std = series.rolling(window=lookback).std()
    zscore = (series - mean) / std
    return zscore

# Streamlit app
st.title("Pair Trading Backtesting")

# Input boxes
st.sidebar.header("Input Parameters")
symbol1 = st.sidebar.text_input("Enter Stock Symbol 1", "AAPL")
symbol2 = st.sidebar.text_input("Enter Stock Symbol 2", "MSFT")
lookback = st.sidebar.number_input("Lookback Period for Z-Score", min_value=1, value=30)
from_date = st.sidebar.text_input("From Date (YYYY-MM-DD)", "2020-01-01")
to_date = st.sidebar.text_input("To Date (YYYY-MM-DD)", "2023-01-01")

# Go button
if st.sidebar.button("Go"):
    if not symbol1.strip() or not symbol2.strip():
        st.error("Please provide valid stock tickers.")
    else:
        try:
            # Add timezone information to the start and end dates
            tz = pytz.timezone("America/New_York")
            start = tz.localize(datetime.strptime(from_date, "%Y-%m-%d"))
            end = tz.localize(datetime.strptime(to_date, "%Y-%m-%d"))

            # Fetch data for both stocks
            data1 = fetch_stock_data(symbol1, start, end)
            data2 = fetch_stock_data(symbol2, start, end)

            if data1 is not None and data2 is not None:
                # Calculate ratio and z-score
                data1['Close'] = data1['Adj Close']
                data2['Close'] = data2['Adj Close']
                ratio = data1['Close'] / data2['Close']
                zscore = calculate_zscore(ratio, lookback)

                # Display results
                st.subheader("Backtest Results")
                st.write("### Z-Score Series")
                st.line_chart(zscore)

                st.write("### Stock Prices")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"#### {symbol1} Close Prices")
                    st.line_chart(data1['Close'])
                with col2:
                    st.write(f"#### {symbol2} Close Prices")
                    st.line_chart(data2['Close'])

                # Trade logic (example)
                entry_threshold = 2.5
                exit_threshold = 1.5
                trades = []
                position = None  # None, 'long', or 'short'

                for i in range(lookback, len(data1)):
                    if position is None:
                        # Entry logic
                        if zscore[i] > entry_threshold:
                            position = 'short'
                            entry_price = data1['Close'][i] - data2['Close'][i]
                            entry_date = data1.index[i]
                        elif zscore[i] < -entry_threshold:
                            position = 'long'
                            entry_price = data2['Close'][i] - data1['Close'][i]
                            entry_date = data1.index[i]
                    else:
                        # Exit logic
                        if (position == 'short' and zscore[i] < exit_threshold) or \
                           (position == 'long' and zscore[i] > -exit_threshold):
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

                # Display trades
                if trades:
                    st.write("### Trades")
                    trades_df = pd.DataFrame(trades)
                    st.dataframe(trades_df)
                else:
                    st.write("No trades were executed during the selected period.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
