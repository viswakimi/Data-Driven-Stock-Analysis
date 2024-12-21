# Data-Driven Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends

## **Overview**
This GitHub repository contains the source code, documentation, and deliverables for the "Data-Driven Stock Analysis" project. The project focuses on analyzing and visualizing the performance of Nifty 50 stocks over the past year, providing actionable insights for investors and market analysts.

---

## **Features**
- **Data Transformation**: Convert raw YAML stock data into structured CSV files.
- **Stock Performance Metrics**:
  - Identify top-performing (green) and worst-performing (red) stocks.
  - Measure volatility and cumulative returns.
  - Sector-wise performance analysis.
- **Interactive Dashboards**:
  - Streamlit-based real-time dashboards.
  - Power BI visualizations for comprehensive insights.
- **Stock Price Correlation Heatmap**: Visualize relationships between different stocks.

---

## **Technologies Used**
- **Programming Language**: Python
- **Database**: MySQL/PostgreSQL
- **Visualization Tools**: Streamlit, Power BI
- **Python Libraries**: Pandas, Matplotlib, SQLAlchemy

---

## **Project Structure**
```
📁 project-root
├── 📁 data
│   ├── raw_data (YAML files)
│   └── processed_data (CSV files)
├── 📁 scripts
│   ├── data_transformation.py
│   ├── analysis.py
│   ├── visualization.py
│   └── streamlit_app.py
├── 📁 dashboards
│   ├── PowerBI_Dashboard.pbix
├── README.md
├── requirements.txt
└── LICENSE
```

---

## **Installation Instructions**
1. Clone the repository:
   ```bash
   git clone https://github.com/username/data-driven-stock-analysis.git
   cd data-driven-stock-analysis
   ```
2. Install required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the database:
   - Use MySQL or PostgreSQL to create a database.
   - Run the SQL schema file (provided in the `scripts` folder) to initialize the database.

4. Transform YAML data into CSV format:
   ```bash
   python scripts/data_transformation.py
   ```

5. Launch the Streamlit dashboard:
   ```bash
   streamlit run scripts/streamlit_app.py
   ```

---

## **Usage**
### **Streamlit Application**
- Run the application locally to interact with stock performance dashboards in real time.
- Features include:
  - Top-performing and worst-performing stocks.
  - Volatility and cumulative return analysis.
  - Sector-wise performance insights.

### **Power BI Dashboard**
- Import the provided `.pbix` file into Power BI to access detailed visualizations.

---

## **Data Analysis Highlights**
- **Top 10 Green Stocks**: Highest yearly returns.
- **Top 10 Red Stocks**: Lowest yearly returns.
- **Volatility Insights**: Top 10 most volatile stocks.
- **Sector-wise Analysis**: Average returns by sector.
- **Correlation Heatmap**: Stock price correlations.

---

## **References**
- [Streamlit Documentation](https://docs.streamlit.io/library/api-reference)
- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)

---


