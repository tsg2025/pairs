import streamlit as st
import yfinance as yf
import pandas as pd
import tempfile
import os

# Streamlit App Title
st.title("Stock Price Downloader")

# Sidebar for user input
st.sidebar.header("Settings")
tickers = st.sidebar.multiselect("Select Stocks", ["MSFT", "AAPL"], default=["MSFT", "AAPL"])
period = st.sidebar.selectbox("Select Time Period", ["1d", "5d", "1mo", "6mo", "1y", "5y"], index=2)
interval = st.sidebar.selectbox("Select Interval", ["1h", "1d", "1wk", "1mo"], index=1)

# Fetch Data Button
if st.sidebar.button("Fetch Stock Data"):
    with st.spinner("Fetching data..."):
        try:
            if not tickers:
                st.error("Please select at least one stock.")
            else:
                # Fetch data for selected stocks
                stock_data = {}
                for ticker in tickers:
                    stock = yf.Ticker(ticker)
                    history = stock.history(period=period, interval=interval)

                    if not history.empty:
                        stock_data[ticker] = history["Close"]
                    else:
                        st.warning(f"No data found for {ticker}")

                # If data is available, create DataFrame
                if stock_data:
                    df = pd.DataFrame(stock_data)
                    st.success("Data fetched successfully!")
                    st.write(df.head())

                    # Save data to a temporary file
                    temp_dir = tempfile.gettempdir()
                    file_path = os.path.join(temp_dir, "stock_prices.csv")
                    df.to_csv(file_path)

                    # Provide a download link
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name="stock_prices.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("No valid data available. Please adjust the settings.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
