import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Database connection using SQLAlchemy
engine = create_engine('mysql+pymysql://root:Abcd1234@localhost/stock_analysis')

# Function to fetch data from MySQL
@st.cache_data
def fetch_data():
    query = "SELECT * FROM stock_data"
    df = pd.read_sql(query, engine)
    return df

# Title and Description
st.title("Interactive Stock Data Analysis")

# Load Data
try:
    df = fetch_data()

    # Data Cleaning
    df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is datetime

    # Sidebar Inputs
    st.sidebar.header("User Inputs")
    
    # Ensure that 'df' is available when these inputs are created
    selected_metric = st.sidebar.multiselect(
        "Select Metric to Visualize", 
        ["Open", "High", "Low", "Close", "Volume","monthly_return","cumulative_return","daily_return","volatility","yearly_return"] 
  )
    
    selected_ticker = st.sidebar.multiselect(
        "Select Ticker", 
        ["All"] + df["Ticker"].dropna().unique().tolist()
    )

    date_range = st.sidebar.date_input("Select Date Range", [])

    # Populate sectors in the filter dropdown
    if "sector" in df.columns:
        sectors = ["All"] + df["sector"].dropna().unique().tolist()
        selected_sector = st.sidebar.multiselect("Filter by Sector", sectors)
    else:
        selected_sector = ["All"]

    # Filter by Sector
    if "All" not in selected_sector:
        df = df[df["sector"].isin(selected_sector)]
    
    # Apply Date Filter
    if date_range and len(date_range) == 2:
        df = df[(df['date'] >= pd.Timestamp(date_range[0])) & (df['date'] <= pd.Timestamp(date_range[1]))]

    # --- Data Preview ---
    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # --- Top 10 Most Volatile Stocks ---
    st.subheader("Top 10 Most Volatile Stocks")
    if "volatility" in df.columns:
        top_10_volatile = df.groupby("Ticker")["volatility"].mean().nlargest(10)
        fig, ax = plt.subplots(figsize=(10, 6))
        top_10_volatile.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
        ax.set_title("Top 10 Most Volatile Stocks")
        ax.set_xlabel("Stock Ticker")
        ax.set_ylabel("Volatility (Standard Deviation)")
        st.pyplot(fig)
    else:
        st.error("Volatility data is missing!")

    # --- Top 5 Gainers and Losers (Month-wise) ---
    st.subheader("Top 5 Gainers and Losers (Month-wise)")
    
    monthly_data = df.groupby(['Ticker', 'month']).agg(
        open=('open', 'first'),
        close=('close', 'last')
    ).reset_index()
    
    monthly_data['monthly_return'] = ((monthly_data['close'] - monthly_data['open']) / 
                                      monthly_data['open']) * 100

    months = monthly_data['month'].unique()

    for month in months:
        month_data = monthly_data[monthly_data['month'] == month]
        top_5_gainers = month_data.nlargest(5, 'monthly_return')
        top_5_losers = month_data.nsmallest(5, 'monthly_return')

        col1, col2 = st.columns(2)

        with col1:
          st.write("**Top 5 Gainers**")
          fig, ax = plt.subplots(figsize=(10, 6))
          sns.barplot(x='Ticker', y='monthly_return', data=top_5_gainers, ax=ax, palette='Greens_d',hue='Ticker')
          ax.set_title(f'Top 5 Gainers - {month}')
          ax.set_xlabel('Ticker')
          ax.set_ylabel('Monthly Return (%)')
          ax.tick_params(axis='x', rotation=45)
          st.pyplot(fig)

          

        with col2:
          st.write("**Top 5 Losers**")
          fig, ax = plt.subplots(figsize=(10, 6))
          sns.barplot(x='Ticker', y='monthly_return', data=top_5_losers, ax=ax, palette='Reds_d',hue='Ticker')
          ax.set_title(f'Top 5 Losers - {month}')
          ax.set_xlabel('Ticker')
          ax.tick_params(axis='x', rotation=45)
          st.pyplot(fig)

       # --- Stock Price Correlation ---
    st.subheader("Stock Price Correlation")
    if "close" in df.columns:
        correlation_data = df.pivot(index="date", columns="Ticker", values="close")
        corr = correlation_data.corr()
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr, annot=False, cmap="coolwarm",cbar=True,ax=ax)
        plt.title("Stock Price Correlation")
        st.pyplot(fig)
    else:
        st.error("Close price data is missing!")

    # --- Top 5 Performing Stocks (Daily Return) ---
    st.subheader("Top 5 Performing Stocks (Daily Return)")
    top_stocks = (
        df.groupby('Ticker')['daily_return']
        .last()
        .nlargest(5)
        .index
    )

    plt.figure(figsize=(12, 8))
    for ticker in top_stocks:
        stock_data = df[df['Ticker'] == ticker]
        plt.plot(stock_data['date'], stock_data['cumulative_return'], label=ticker)

    plt.title(f"Top 5 Performing Stocks: {selected_metric}")
    plt.xlabel("Date")
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(visible=True, linestyle="--", alpha=0.7)
    st.pyplot(plt)
    
except Exception as e:
    st.error(f"An error occurred: {e}")

# Footer
st.sidebar.markdown("---")
