import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import pymysql
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    layout="wide",
    page_title="Stock Data Analysis",
    initial_sidebar_state="expanded"
)

# Page styling
st.markdown(
    """
    <style>
    .stApp {        
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(100, 60, 50, 0.4);
    }
    
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 style="color:red;">Stock Performance Dashboard</h1>', unsafe_allow_html=True)
# Database connection using SQLAlchemy
engine = create_engine('mysql+pymysql://root:Abcd1234@localhost/stock_analysis')

# Function to fetch data from MySQL
@st.cache_data
def fetch_data():
    query = "SELECT * FROM stock_data1"
    df = pd.read_sql(query, engine)
    return df

# Load Data
try:
    df = fetch_data()

    # Data Cleaning
    df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' is datetime

    # Sidebar Inputs
    st.sidebar.header("User Inputs")
    selected_ticker = st.sidebar.multiselect(
        "Select Ticker", 
        ["All"] + df["Ticker"].dropna().unique().tolist()
    )

    # Populate sectors in the filter dropdown
    if "sector" in df.columns:
        sectors = ["All"] + df["sector"].dropna().unique().tolist()
        selected_sector = st.sidebar.multiselect("Filter by Sector", sectors)
    else:
        selected_sector = ["All"]

    # Filter by Sector
    if "All" not in selected_sector:
        df = df[df["sector"].isin(selected_sector)]

    # Month and Year Filter
    df['month'] = df['date'].dt.month_name()
    df['year'] = df['date'].dt.year

    months = ["All"] + df['month'].unique().tolist()
    selected_month = st.sidebar.selectbox("Select Month", months)

    years = ["All"] + df['year'].unique().tolist()
    selected_year = st.sidebar.selectbox("Select Year", years)

    if selected_month != "All":
        df = df[df['month'] == selected_month]
    if selected_year != "All":
        df = df[df['year'] == selected_year]

    # --- Data Preview ---
    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # --- Top 10 Most Volatile Stocks ---
    st.subheader("Top 10 Most Volatile Stocks")
    if "volatility" in df.columns:
        top_10_volatile = df.groupby("Ticker")["volatility"].mean().nlargest(10).reset_index()
        fig = px.bar(top_10_volatile, 
                     x="Ticker", 
                     y="volatility", 
                     color="volatility", 
                     color_continuous_scale="RdYlGn_r",  # Green to Red palette
                     title="Top 10 Most Volatile Stocks",
                     labels={"volatility": "Volatility (Standard Deviation)", "Ticker": "Stock Ticker"})
        fig.update_layout(
            xaxis_title="Stock Ticker",
            yaxis_title="Volatility (Standard Deviation)",
            xaxis_tickangle=-45,
            template="plotly_dark"
        )
        st.plotly_chart(fig)
    else:
        st.error("Volatility data is missing!")

    # --- Average Yearly Return by Sector ---
    st.subheader("Average Yearly Return by Sector")
    avg_yearly_return = df.groupby("sector")["yearly_return"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(30, 20))
    sns.barplot(x="sector", y="yearly_return", data=avg_yearly_return, ax=ax, palette="RdYlGn_r")
    ax.set_title("Average Yearly Return by Sector")
    ax.set_xlabel("Sector")
    ax.set_ylabel("Average Yearly Return (%)")
    st.pyplot(fig)

    # --- Stock Price Correlation ---
    st.subheader("Stock Price Correlation")
    if "close" in df.columns:
        correlation_data = df.pivot(index="date", columns="Ticker", values="close")
        corr = correlation_data.corr()
        fig, ax = plt.subplots(figsize=(12, 10))
        sns.heatmap(corr, annot=False, cmap="coolwarm", cbar=True, ax=ax)
        plt.title("Stock Price Correlation")
        st.pyplot(fig)
    else:
        st.error("Close price data is missing!")

    # --- Top 5 Performing Stocks ---
    st.subheader("Top 5 Performing Stocks")
    top_5_stocks = df.groupby('Ticker')['cumulative_return'].last().nlargest(5).index
    plt.figure(figsize=(12, 8))
    for ticker in top_5_stocks:
        stock_data = df[df['Ticker'] == ticker]
        plt.plot(stock_data['date'], stock_data['cumulative_return'], label=ticker)
    plt.title('Cumulative Return for Top 5 Performing Stocks')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(visible=True, linestyle="--", alpha=0.7)
    st.pyplot(plt)

    # --- Top 5 Gainers and Losers ---
    st.subheader("Top 5 Gainers and Losers")
    df["monthly_return"] = df.groupby("Ticker")["close"].pct_change() * 100
    latest_month_data = df[df["month"] == selected_month] if selected_month != "All" else df
    
    top_5_gainers = latest_month_data.nlargest(5, "monthly_return")
    top_5_losers = latest_month_data.nsmallest(5, "monthly_return")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top 5 Gainers**")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Ticker", y="monthly_return", data=top_5_gainers, ax=ax, palette="Greens_d")
        ax.set_title(f"Top 5 Gainers - {selected_month}")
        st.pyplot(fig)

    with col2:
        st.write("**Top 5 Losers**")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x="Ticker", y="monthly_return", data=top_5_losers, ax=ax, palette="Reds_d")
        ax.set_title(f"Top 5 Losers - {selected_month}")
        st.pyplot(fig)

    # --- Top 5 and Bottom 5 Volume Stocks ---
    st.subheader("Top 5 and Bottom 5 Volume Stocks")
    volume_data = df.groupby('Ticker')['volume'].mean().reset_index()
    top_5_volume = volume_data.nlargest(5, 'volume')
    bottom_5_volume = volume_data.nsmallest(5, 'volume')

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top 5 Volume Stocks**")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Ticker', y='volume', data=top_5_volume, ax=ax, palette='Greens_d', hue='Ticker')
        ax.set_title('Top 5 Volume Stocks')
        ax.set_xlabel('Ticker')
        ax.set_ylabel('Average Volume')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    with col2:
        st.write("**Bottom 5 Volume Stocks**")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x='Ticker', y='volume', data=bottom_5_volume, ax=ax, palette='Reds_d', hue='Ticker')
        ax.set_title('Bottom 5 Volume Stocks')
        ax.set_xlabel('Ticker')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

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

except Exception as e:
    st.error(f"An error occurred: {e}")

# Footer
st.sidebar.markdown("---")
