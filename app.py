import yfinance as yf

# Define stock tickers
tickers = ["MSFT", "AAPL"]

# Define time period
start_date = "2020-01-01"
end_date = "2024-12-31"

# Fetch historical data
data = yf.download(tickers, start=start_date, end=end_date)

# Display the first few rows
print(data.head())

# Save to CSV
data.to_csv("msft_aapl_prices.csv")
