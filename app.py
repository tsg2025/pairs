import streamlit as st
import yfinance as yf
import pandas as pd
import tempfile
import os

# Streamlit Title
st.title("Stock Price Downloader")

# Sidebar for user input
st.sidebar.header("Settings")
tickers = ["MSFT", "AAPL"]
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Fetch Data Button
if st.sidebar.button("Fetch Stock Data"):
    with st.spinner("Fetching data..."):
        data = yf.download(tickers, start=start_date, end=end_date)
        
        if not data.empty:
            st.success("Data fetched successfully!")
            st.write(data.head())  # Display first few rows
            
            # Save to a temporary file
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, "msft_aapl_prices.csv")
            data.to_csv(file_path)
            
            # Provide a download link
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name="msft_aapl_prices.csv",
                    mime="text/csv"
                )
        else:
            st.error("No data found. Please check the date range.")

