import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

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
    try:
        # Fetch data
        st.write(f"Downloading data for {symbol1} and {symbol2}...")
        data1 = yf.download(symbol1, start=from_date, end=to_date, progress=False)
        data2 = yf.download(symbol2, start=from_date, end=to_date, progress=False)
        
        # Check if data is empty
        if data1.empty or data2.empty:
            st.error(f"Failed to fetch data for {symbol1} or {symbol2}. Please check the ticker symbols and try again.")
        else:
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
            st.write(f"#### {symbol1} Close Prices")
            st.line_chart(data1['Close'])
            st.write(f"#### {symbol2} Close Prices")
            st.line_chart(data2['Close'])
            
    except Exception as e:
        st.error(f"Error: {e}")
