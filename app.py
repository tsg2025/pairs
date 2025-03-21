import streamlit as st
import yfinance as yf
import pandas as pd
import tempfile
import os

# Streamlit Title
st.title("Stock Price Downloader")

# Sidebar for user input
st.sidebar.header("Settings")

# Allow user to select stocks
tickers = st.sidebar.multiselect("Select Stocks", ["MSFT", "AAPL"], default=["MSFT", "AAPL"])

# Allow user to select start and end date
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
end_date = st.sidebar.date_input("End Date", pd.to_datetime("2024-12-31"))

# Convert dates to string format
start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# Fetch Data Button
if st.sidebar.button("Fetch Stock Data"):
    with st.spinner("Fetching data..."):
        try:
            if len(tickers) == 0:
                st.error("Please select at least one stock.")
            else:
                # Download stock data
                data = yf.download(tickers, start=start_date_str, end=end_date_str, progress=False)

                if not data.empty:
                    st.success("Data fetched successfully!")
                    st.write(data.head())  # Display first few rows

                    # Save data to a temporary CSV file
                    temp_dir = tempfile.gettempdir()
                    file_path = os.path.join(temp_dir, "stock_prices.csv")
                    data.to_csv(file_path)

                    # Provide a download link
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name="stock_prices.csv",
                            mime="text/csv"
                        )
                else:
                    st.error("No data found. Adjust the date range and try again.")

        except Exception as e:
            st.error(f"Error fetching data: {e}")
