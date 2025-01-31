import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import pymysql

# Page Configuration
st.set_page_config(layout="wide", page_title="Stock Data Analysis", initial_sidebar_state="expanded")

# Database Connection
engine = create_engine('mysql+pymysql://root:Abcd1234@localhost/stock_analysis')

# Fetch Data Function (Cached for Performance)
@st.cache_data
def fetch_data():
    df = pd.read_sql("SELECT * FROM stock_data1", engine)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = fetch_data()

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main Dashboard", "Selected Stocks Details"])

# Sidebar Filters
st.sidebar.header("Filters")
tickers = df["Ticker"].dropna().unique().tolist()
sectors = df["sector"].dropna().unique().tolist()
months = df['date'].dt.month_name().unique().tolist()
years = df['date'].dt.year.unique().tolist()

selected_ticker = st.sidebar.multiselect("Select Ticker", ["All"] + tickers)
selected_sector = st.sidebar.multiselect("Filter by Sector", ["All"] + sectors)
selected_month = st.sidebar.selectbox("Select Month", ["All"] + months)
selected_year = st.sidebar.selectbox("Select Year", ["All"] + years)

# Apply Filters Efficiently
filtered_df = df.copy()

if "All" not in selected_sector:
    filtered_df = filtered_df[filtered_df["sector"].isin(selected_sector)]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df['date'].dt.month_name() == selected_month]
if selected_year != "All":
    filtered_df = filtered_df[filtered_df['date'].dt.year == int(selected_year)]
if "All" not in selected_ticker:
    filtered_df = filtered_df[filtered_df["Ticker"].isin(selected_ticker)]

# === Main Dashboard ===
if page == "Main Dashboard":
    st.title("Stock Performance Dashboard")

    # Raw Data Preview
    with st.expander(" View Raw Data"):
        st.dataframe(filtered_df.head(10))

    
    # Volatility Chart
    if "volatility" in filtered_df.columns:
        top_volatile = filtered_df.groupby("Ticker")["volatility"].mean().nlargest(10).reset_index()
        st.plotly_chart(px.bar(top_volatile, x="Ticker", y="volatility", color="volatility", color_continuous_scale="RdYlGn_r", title="Top 10 Most Volatile Stocks"))

    # Yearly Return by Sector
    if "yearly_return" in filtered_df.columns:
        avg_return = filtered_df.groupby("sector")["yearly_return"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(30, 25))
        sns.barplot(x="sector", y="yearly_return", data=avg_return, ax=ax, palette="RdYlGn_r")
        ax.set_title("Average Yearly Return by Sector")
        st.pyplot(fig)

    # Correlation Heatmap
    if "close" in filtered_df.columns:
        correlation_data = filtered_df.pivot(index="date", columns="Ticker", values="close").corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_data, annot=False, cmap="coolwarm", ax=ax)
        ax.set_title("Stock Correlation Heatmap")
        st.pyplot(fig)

    # Cumulative Returns for Top 5 Stocks
    if "cumulative_return" in filtered_df.columns:
        top_5 = filtered_df.groupby('Ticker')['cumulative_return'].last().nlargest(5).index
        st.plotly_chart(px.line(filtered_df[filtered_df['Ticker'].isin(top_5)], x='date', y='cumulative_return', color='Ticker', title="Top 5 Stocks: Cumulative Returns Over Time"))

    # Gainers & Losers
    st.subheader("Top 5 Gainers and Losers")
    filtered_df["monthly_return"] = filtered_df.groupby("Ticker")["close"].pct_change() * 100

    latest_month_data = filtered_df if selected_month == "All" else filtered_df[filtered_df["date"].dt.month_name() == selected_month]
    top_5_gainers = latest_month_data.nlargest(5, "monthly_return")
    top_5_losers = latest_month_data.nsmallest(5, "monthly_return")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top 5 Gainers**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x="Ticker", y="monthly_return", data=top_5_gainers, ax=ax, palette="Greens_d")
        ax.set_title(f"Top 5 Gainers - {selected_month}")
        st.pyplot(fig)

    with col2:
        st.write("**Top 5 Losers**")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x="Ticker", y="monthly_return", data=top_5_losers, ax=ax, palette="Reds_d")
        ax.set_title(f"Top 5 Losers - {selected_month}")
        st.pyplot(fig)

    # Volume Analysis
    st.subheader("Top & Bottom 5 Volume Stocks")
    volume_data = filtered_df.groupby('Ticker')['volume'].mean().reset_index()
    top_5_volume = volume_data.nlargest(5, 'volume')
    bottom_5_volume = volume_data.nsmallest(5, 'volume')

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='Ticker', y='volume', data=top_5_volume, ax=ax, palette='Blues_d')
        ax.set_title('Top 5 Volume Stocks')
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(12,8))
        sns.barplot(x='Ticker', y='volume', data=bottom_5_volume, ax=ax, palette='Oranges_d')
        ax.set_title('Bottom 5 Volume Stocks')
        st.pyplot(fig)

# === Selected Stocks Details ===
elif page == "Selected Stocks Details":
    st.title(" Selected Stocks Details")
    if selected_ticker:
        st.subheader("Selected Stocks Details")
        selected_stocks = df[df['Ticker'].isin(selected_ticker)]
        st.dataframe(selected_stocks[['Ticker', 'date', 'volume', 'daily_return', 'high', 'low', 'open', 'close',"monthly_return",'yearly_return']])
        
    st.subheader("Summary")
        # Group by ticker to perform the necessary calculations
    summary = selected_stocks.groupby('Ticker').agg(
            total_volume=('volume', 'sum'),
            avg_daily_return=('daily_return', 'mean'),
            avg_yearly_return=('yearly_return', 'mean'),
            avg_monthly_return=('monthly_return', 'mean')
        ).reset_index()

        # Calculate profit/loss from yearly return (assuming baseline return is 0 or a certain threshold)
    summary['yearly_return_profit_loss'] = summary['avg_yearly_return'] - 0
    col1, col2 = st.columns(2)

        # Display each stock's summary in a card format using st.metric
    for _, row in summary.iterrows():
            with col1:
                st.metric(label=f"{row['Ticker']} - Total Volume", value=f"{row['total_volume']:,}", delta=None)
                st.metric(label=f"{row['Ticker']} - Avg Daily Return", value=f"{row['avg_daily_return']:.2f}%", delta=None)

            with col2:
                st.metric(label=f"{row['Ticker']} - Avg Yearly Return", value=f"{row['avg_yearly_return']:.2f}%", delta=None)
                st.metric(label=f"{row['Ticker']} - Avg Monthly Return", value=f"{row['avg_monthly_return']:.2f}%", delta=None)

            st.markdown("---")  # Divider for better separation between tickers
    # Filter data for a specific ticker
    ticker_data = df[df['Ticker'] == selected_ticker[0]]

   
    risk_return = df.groupby('Ticker').agg(
    avg_return=('daily_return', 'mean'),
    avg_volatility=('volatility', 'mean')
    ).reset_index()

    fig = px.scatter(risk_return, x='avg_volatility', y='avg_return', text='Ticker',
                 title="Risk vs Return",
                 labels={"avg_volatility": "Volatility", "avg_return": "Average Return"})
    fig.update_traces(textposition='top center')
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig)
    
    df['month'] = df['date'].dt.month_name()

    monthly_returns = df.pivot_table(index='Ticker', columns='month', values='monthly_return', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(monthly_returns, cmap="RdYlGn", annot=True, fmt=".2f", center=0)
    plt.title("Monthly Returns by Ticker")
    st.pyplot(plt)

    selected_stocks = df[df['Ticker'].isin(selected_ticker)]
    fig = px.line(selected_stocks, x='date', y='cumulative_return', color='Ticker',
              title="Cumulative Returns Over Time",
              labels={"cumulative_return": "Cumulative Return", "date": "Date"})
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig)

    fig = px.sunburst(df, path=['sector', 'Ticker'], values='volume',
                  title="Sector and Ticker Volume Distribution")
    st.plotly_chart(fig) 
    # Risk vs Return Scatter Plot
    risk_return = filtered_df.groupby('Ticker').agg(avg_return=('daily_return', 'mean'), avg_volatility=('volatility', 'mean')).reset_index()
    st.plotly_chart(px.scatter(risk_return, x='avg_volatility', y='avg_return', text='Ticker', title="Risk vs Return"))

    # Sector Volume Distribution
    st.plotly_chart(px.sunburst(filtered_df, path=['sector', 'Ticker'], values='volume', title="Sector & Ticker Volume Distribution"))

