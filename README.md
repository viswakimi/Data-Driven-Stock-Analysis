Data-Driven Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends

Project Overview

The Stock Performance Dashboard provides a comprehensive visualization and analysis of Nifty 50 stocks' performance over the past year. This project processes daily stock data (open, close, high, low, and volume values), cleans it, and generates insights. Using Streamlit and Power BI, it creates interactive dashboards for investors, analysts, and enthusiasts to make informed decisions based on market trends.


Approach

Data Extraction and Transformation
Data provided in YAML format, organized by months.
Extract and transform YAML data into CSV format (50 CSV files, one per stock).



Business Use Cases

Stock Performance Ranking: Identify top 10 best-performing and worst-performing stocks.
Market Overview: Summarize overall market trends with green vs. red stocks.
Investment Insights: Highlight consistently growing and declining stocks.
Decision Support: Provide average prices, volatility, and behavior insights for retail and institutional traders.


Data Analysis and Visualization Requirements

Python DataFrame Analysis
Top 10 Green Stocks: Sort yearly returns to find top 10 gainers.
Top 10 Loss Stocks: Sort yearly returns to find top 10 losers.

Market Summary:
Count green vs. red stocks.
Calculate average stock price and volume.

Volatility Analysis

Metric: Standard deviation of daily returns.
Visualization: Bar chart of top 10 most volatile stocks.

Cumulative Return Over Time

Metric: Cumulative return for top 5 performing stocks.
Visualization: Line chart of cumulative returns.

Sector-wise Performance

Metric: Average yearly return by sector.
Visualization: Bar chart of sector performance.

Stock Price Correlation

Metric: Correlation matrix of closing prices.
Visualization: Heatmap of stock correlations.

Top Gainers and Losers (Month-wise)

Metric: Monthly percentage change for top 5 gainers and losers.
Visualization: 12 bar charts (one per month).

Dataset:
Data is provided in YAML format, organized by months and dates. Additional sector data in CSV format is used for sector-wise performance.

Deliverables

SQL Database: Cleaned and processed data.
Python Scripts: For data cleaning, analysis, and database interaction.
Power BI Dashboard: For stock performance visualizations.
Streamlit Application: Interactive real-time analysis dashboard.
