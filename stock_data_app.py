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
    df['month'] = df['date'].dt.month
    df['month_str'] = df['date'].dt.strftime('%B %Y')
    return df

df = fetch_data()
print(df.columns)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Main Dashboard","Selected Stocks Details"])

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
    st.subheader("Top 10 Most Volatile Stocks")
    if "volatility" in filtered_df.columns:
        top_volatile = filtered_df.groupby("Ticker")["volatility"].mean().nlargest(10).reset_index()
        st.plotly_chart(px.bar(top_volatile, x="Ticker", y="volatility", color="volatility", color_continuous_scale="RdYlGn_r", title="Top 10 Most Volatile Stocks"))

    # Yearly Return by Sector
    st.subheader("Average Yearly Return by Sector")
    if "yearly_return" in filtered_df.columns:
        avg_return = filtered_df.groupby("sector")["yearly_return"].mean().reset_index()
        fig, ax = plt.subplots(figsize=(15, 10))
        sns.barplot(x="sector", y="yearly_return", data=avg_return, ax=ax, palette="RdYlGn_r")
        ax.set_title("Average Yearly Return by Sector")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    # Correlation Heatmap
    st.subheader("Stock Correlation Heatmap")
    if "close" in filtered_df.columns:
        correlation_data = filtered_df.pivot(index="date", columns="Ticker", values="close").corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_data, annot=False, cmap="coolwarm", ax=ax)
        ax.set_title("Stock Correlation Heatmap")
        st.pyplot(fig)

    # Cumulative Returns for Top 5 Stocks
    st.subheader("Top 5 Stocks: Cumulative Returns Over Time")
    if "cumulative_return" in filtered_df.columns:
        top_5 = filtered_df.groupby('Ticker')['cumulative_return'].last().nlargest(5).index
        st.plotly_chart(px.line(filtered_df[filtered_df['Ticker'].isin(top_5)], x='date', y='cumulative_return', color='Ticker', title="Top 5 Stocks: Cumulative Returns Over Time"))
    
        # Top 10 Green & Red Stocks
    # Remove duplicates and sort by yearly_return
    top_10_green_stocks = df.drop_duplicates(subset=['Ticker']).sort_values(by='yearly_return', ascending=False).head(10)
    top_10_red_stocks = df.drop_duplicates(subset=['Ticker']).sort_values(by='yearly_return').head(10)
    st.subheader("Top 10 Green Stocks and Top 10 Red Stocks")
    col1, col2 = st.columns(2)

    with col1:      
      fig_green = px.bar(top_10_green_stocks, x='Ticker', y='yearly_return', color='yearly_return',
                       color_continuous_scale='Greens', title="Top 10 Best Performing Stocks")
      st.plotly_chart(fig_green)

    with col2:
      fig_red = px.bar(top_10_red_stocks, x='Ticker', y='yearly_return', color='yearly_return',
                     color_continuous_scale='Reds', title="Top 10 Worst Performing Stocks")
      st.plotly_chart(fig_red)

# === Monthly Top 5 Gainers and Losers ===
    st.subheader("Monthly Top 5 Gainers and Losers")

    if selected_month != "All":
        month_data = df[df['date'].dt.month_name() == selected_month]

        # Ensure no duplicates for tickers
        month_data_unique = month_data.drop_duplicates(subset=['Ticker'])

        if len(month_data_unique) >= 5:
            top_5_gainers = month_data_unique.nlargest(5, 'monthly_return')
            top_5_losers = month_data_unique.nsmallest(5, 'monthly_return')

            col1, col2 = st.columns(2)

            with col1:                
                fig_gainers = px.bar(top_5_gainers, x='Ticker', y='monthly_return', color='monthly_return',
                                     color_continuous_scale='Blues', title=f"Top 5 Gainers - {selected_month}")
                st.plotly_chart(fig_gainers)

            with col2:                
                fig_losers = px.bar(top_5_losers, x='Ticker', y='monthly_return', color='monthly_return',
                                    color_continuous_scale='Reds', title=f"Top 5 Losers - {selected_month}")
                st.plotly_chart(fig_losers)

    # Volume Analysis
    st.subheader("Top & Bottom 5 Volume Stocks")
    volume_data = filtered_df.groupby('Ticker')['volume'].mean().reset_index()
    top_5_volume = volume_data.nlargest(5, 'volume')
    bottom_5_volume = volume_data.nsmallest(5, 'volume')
    col1, col2 = st.columns(2)
    with col1:      
      fig_top_volume = px.bar(top_5_volume, x='Ticker', y='volume', color='volume',
                        color_continuous_scale='greens', title="Top 5 Volume Stocks")
      st.plotly_chart(fig_top_volume)
      
    with col2:      
      fig_bottom_volume = px.bar(bottom_5_volume, x='Ticker', y='volume', color='volume',
                           color_continuous_scale='Oranges', title="Bottom 5 Volume Stocks")
      st.plotly_chart(fig_bottom_volume)

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
    
    st.subheader("Average Monthly Returns Heatmap")
    # Filter data for a specific ticker
    ticker_data = df[df['Ticker'] == selected_ticker[0]]

    df['month'] = df['date'].dt.month_name()

    monthly_returns = df.pivot_table(index='Ticker', columns='month', values='monthly_return', aggfunc='mean')
    plt.figure(figsize=(12, 8))
    sns.heatmap(monthly_returns, cmap="RdYlGn", annot=True, fmt=".2f", center=0)
    st.pyplot(plt)

    st.subheader("Cumulative Returns Over Time")
    selected_stocks = df[df['Ticker'].isin(selected_ticker)]
    fig = px.line(selected_stocks, x='date', y='cumulative_return', color='Ticker',
              title="Cumulative Returns Over Time",
              labels={"cumulative_return": "Cumulative Return", "date": "Date"})
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig)
     
    # Risk vs Return Scatter Plot
    st.subheader("Risk vs Return Scatter Plot")
    risk_return = filtered_df.groupby('Ticker').agg(avg_return=('daily_return', 'mean'), avg_volatility=('volatility', 'mean')).reset_index()
    st.plotly_chart(px.scatter(risk_return, x='avg_volatility', y='avg_return', text='Ticker', title="Risk vs Return"))

    # Sector Volume Distribution
    st.subheader("Sector & Ticker Volume Distribution")
    st.plotly_chart(px.sunburst(filtered_df, path=['sector', 'Ticker'], values='volume', title="Sector & Ticker Volume Distribution"))
