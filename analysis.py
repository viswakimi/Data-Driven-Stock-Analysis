import pandas as pd
from pathlib import Path
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import timedelta

# Step 1: Extract Data from YAML Files
def yaml_to_csv(input_folder, output_file):
    """Extract data from YAML files and save as a combined CSV."""
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    combined_data = []

    for month_path in Path(input_folder).iterdir():
        if not month_path.is_dir():
            continue

        for file_path in month_path.glob('*.yaml'):
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                if isinstance(data, list):
                    combined_data.append(pd.DataFrame(data))

    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)
        combined_df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
    else:
        print("No data found.")

# Step 2: Perform Data Analysis
def analyze_data(input_csv):
    """Analyze data for yearly returns, volatility, and market summary."""
    # Load the combined data
    df = pd.read_csv(input_csv)

    # Ensure 'date' is in datetime format
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Group by Ticker and year for yearly analysis
    yearly_data = df.groupby(['Ticker', 'year']).agg(
        first_open=('open', 'first'),
        last_close=('close', 'last')
    ).reset_index()

    # Calculate yearly return
    yearly_data['yearly_return'] = ((yearly_data['last_close'] - yearly_data['first_open']) / 
                                    yearly_data['first_open']) * 100

    # Identify top 10 green and red stocks
    top_10_green = yearly_data.nlargest(10, 'yearly_return')
    top_10_red = yearly_data.nsmallest(10, 'yearly_return')

    # Market summary
    green_stocks = (yearly_data['yearly_return'] > 0).sum()
    red_stocks = (yearly_data['yearly_return'] <= 0).sum()

    # Volatility analysis
    df['daily_return'] = df.groupby('Ticker')['close'].pct_change()
    volatility = df.groupby('Ticker')['daily_return'].std().nlargest(10)

    # Calculate cumulative return
    df['cumulative_return'] = df.groupby('Ticker')['daily_return'].cumsum()

    # Calculate monthly returns
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby(['Ticker', 'month']).agg(
        open=('open', 'first'),
        close=('close', 'last')
    ).reset_index()
    monthly_data['monthly_return'] = ((monthly_data['close'] - monthly_data['open']) / 
                                      monthly_data['open']) * 100

    # Save results to CSV
    top_10_green.to_csv('top_10_green_stocks.csv', index=False)
    top_10_red.to_csv('top_10_red_stocks.csv', index=False)
    print("Top 10 green and red stocks saved.")

    return df, yearly_data, top_10_green, top_10_red, volatility, monthly_data

# Step 3: Visualizations
def visualize_results(top_10_green, top_10_red, volatility, df, monthly_data):
    """Generate visualizations for analysis results."""
    # Top 10 Green Stocks
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Ticker', y='yearly_return', data=top_10_green)
    plt.title('Top 10 Green Stocks')
    plt.xlabel('Ticker')
    plt.ylabel('Yearly Return (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_10_green_stocks.png')
    plt.show()

    # Top 10 Red Stocks
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Ticker', y='yearly_return', data=top_10_red)
    plt.title('Top 10 Red Stocks')
    plt.xlabel('Ticker')
    plt.ylabel('Yearly Return (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_10_red_stocks.png')
    plt.show()

    # Volatility
    plt.figure(figsize=(10, 6))
    sns.barplot(x=volatility.index, y=volatility.values)
    plt.title('Top 10 Most Volatile Stocks')
    plt.xlabel('Ticker')
    plt.ylabel('Volatility (Standard Deviation)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('top_10_volatile_stocks.png')
    plt.show()

    # Cumulative Return for Top 5 Performing Stocks
    top_5_stocks = df.groupby('Ticker')['cumulative_return'].last().nlargest(5).index
    plt.figure(figsize=(12, 8))
    for ticker in top_5_stocks:
        stock_data = df[df['Ticker'] == ticker]
        plt.plot(stock_data['date'], stock_data['cumulative_return'], label=ticker)

    plt.title('Cumulative Return for Top 5 Performing Stocks')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.tight_layout()
    plt.savefig('top_5_cumulative_return.png')
    plt.show()

    # Sector-wise Performance
    if 'Sector' in df.columns:
        sector_performance = df.groupby('Sector')['yearly_return'].mean().sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=sector_performance.index, y=sector_performance.values)
        plt.title('Average Yearly Return by Sector')
        plt.xlabel('Sector')
        plt.ylabel('Average Yearly Return (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('sector_performance.png')
        plt.show()

    # Stock Price Correlation Heatmap
    stock_prices = df.pivot(index='date', columns='Ticker', values='close')
    correlation_matrix = stock_prices.corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', cbar=True)
    plt.title('Stock Price Correlation Heatmap')
    plt.tight_layout()
    plt.savefig('correlation_heatmap.png')
    plt.show()

    # Top 5 Gainers and Losers by Month
    months = monthly_data['month'].unique()
    for month in months:
        month_data = monthly_data[monthly_data['month'] == month]
        top_5_gainers = month_data.nlargest(5, 'monthly_return')
        top_5_losers = month_data.nsmallest(5, 'monthly_return')

        fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
        sns.barplot(x='Ticker', y='monthly_return', data=top_5_gainers, ax=axes[0],hue='Ticker', palette='Greens_d')
        axes[0].set_title(f'Top 5 Gainers - {month}')
        axes[0].set_xlabel('Ticker')
        axes[0].set_ylabel('Monthly Return (%)')
        axes[0].tick_params(axis='x', rotation=45)

        sns.barplot(x='Ticker', y='monthly_return', data=top_5_losers, ax=axes[1],hue='Ticker',palette='Reds_d')
        axes[1].set_title(f'Top 5 Losers - {month}')
        axes[1].set_xlabel('Ticker')
        axes[1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(f'gainers_losers_{month}.png')
        plt.show()

# Step 4: Streamlit Dashboard
def streamlit_dashboard(top_10_green, top_10_red, volatility, df, monthly_data):
    """Create an interactive dashboard using Streamlit."""
    st.title("Stock Analysis Dashboard")

    # Display Top 10 Green Stocks
    st.subheader("Top 10 Green Stocks")
    st.dataframe(top_10_green)

    # Display Top 10 Red Stocks
    st.subheader("Top 10 Red Stocks")
    st.dataframe(top_10_red)

    # Display Volatility
    st.subheader("Top 10 Most Volatile Stocks")
    st.bar_chart(volatility)

    # Cumulative Return
    st.subheader("Cumulative Return for Top 5 Performing Stocks")
    top_5_stocks = df.groupby('Ticker')['cumulative_return'].last().nlargest(5).index
    st.line_chart(df[df['Ticker'].isin(top_5_stocks)].pivot(index='date', columns='Ticker', values='cumulative_return'))

    # Sector-wise Performance
    if 'Sector' in df.columns:
        st.subheader("Average Yearly Return by Sector")
        sector_performance = df.groupby('Sector')['yearly_return'].mean().sort_values(ascending=False)
        st.bar_chart(sector_performance)

    # Correlation Heatmap
    st.subheader("Stock Price Correlation Heatmap")
    stock_prices = df.pivot(index='date', columns='Ticker', values='close')
    correlation_matrix = stock_prices.corr()
    st.write("Correlation Matrix:")
    st.dataframe(correlation_matrix)

    # Monthly Top 5 Gainers and Losers
    st.subheader("Monthly Top 5 Gainers and Losers")
    months = monthly_data['month'].unique()
    for month in months:
        st.write(f"### {month}")
        month_data = monthly_data[monthly_data['month'] == month]
        top_5_gainers = month_data.nlargest(5, 'monthly_return')
        top_5_losers = month_data.nsmallest(5, 'monthly_return')

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Top 5 Gainers")
            st.dataframe(top_5_gainers[['Ticker', 'monthly_return']])

        with col2:
            st.write("#### Top 5 Losers")
            st.dataframe(top_5_losers[['Ticker', 'monthly_return']])

# Execute the full workflow
if __name__ == "__main__":
    input_folder = "D:/projects/stock/data"
    output_file = "D:/projects/stock/outputvi/combined.csv"

    # Step 1: Extract data
    yaml_to_csv(input_folder, output_file)

    # Step 2: Analyze data
    df, yearly_data, top_10_green, top_10_red, volatility, monthly_data = analyze_data(output_file)

    # Step 3: Visualize results
    visualize_results(top_10_green, top_10_red, volatility, df, monthly_data)

    # Step 4: Launch Streamlit dashboard
    streamlit_dashboard(top_10_green, top_10_red, volatility, df, monthly_data)

