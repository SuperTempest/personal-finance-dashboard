# 💸 Cash Flow & Financial Analytics Dashboard

A modular financial analytics platform built with Python, Streamlit, Pandas, and Plotly for analyzing transaction-level banking data.

The system supports cash flow tracking, income-expense classification, budget monitoring, recurring payment detection, and financial forecasting through an interactive analytics dashboard.


🔗 **Live demo:** [personal-finance-dashboard-uswkgh6uex9kyxpz5hgffi.streamlit.app](https://personal-finance-dashboard-uswkgh6uex9kyxpz5hgffi.streamlit.app/)

---

## ✨ Features

- **CSV Upload** – Drop in your own bank export (`date`, `amount`, `category`, optional `description`) or use the bundled sample data.
- **Interactive Filters** – Filter by expense category and time range (All Time, YTD, Last 3/6 Months, or a custom date range).
- **Key Metrics** – At-a-glance totals for income, expenses, net savings, and savings rate.
- **Monthly Budget Tracker** – Set a monthly spending target and see how your average outlay compares.
- **Behavioral Insights** – Rotating carousel of auto-generated insights (top spending category, largest purchase, average transaction size, etc.).
- **Spending Breakdown** – Interactive pie chart of expenses by category.
- **Unified Ledger** – Combined, sortable view of income and expense transactions.
- **Monthly Cash Flow Trend** – Grouped bar chart comparing income vs. expenses over time.
- **6-Month Forecast** – Projects future net worth based on historical average savings.
- **Recurring Payment Detector** – Automatically identifies likely subscriptions and recurring bills based on transaction cadence.
- **Category Deep-Dive** – Drill into any category to see totals, transaction counts, and spending over time.

---

## 🧠 System Architecture

The application follows a modular analytics pipeline architecture:

```text
CSV Ingestion
      ↓
Data Cleaning & Normalization
      ↓
Income / Expense Classification
      ↓
Filtering & Aggregation Engine
      ↓
Forecasting & Insight Generation
      ↓
Interactive Visualization Layer
```

### Core Components

| Module           | Responsibility                                                   |
| ---------------- | ---------------------------------------------------------------- |
| `data_loader.py` | CSV ingestion, schema validation, data normalization             |
| `analytics.py`   | KPI computation, filtering logic, trend aggregation, forecasting |
| `categorizer.py` | Recurring transaction and subscription detection                 |
| `dashboard.py`   | Streamlit layout, visualizations, and UI orchestration           |
| `helpers.py`     | Shared utility and formatting functions                          |

The system separates data ingestion, analytics, and presentation layers to improve maintainability and scalability as new financial analysis features are added.

---

## 📁 Project Structure

```
personal-finance-dashboard/
├── app/
│   ├── analytics.py       # Filtering, metrics, insights, and forecasting logic
│   ├── categorizer.py      # Recurring payment / subscription detection
│   ├── dashboard.py         # Main Streamlit UI and layout
│   ├── data_loader.py       # CSV ingestion and data cleaning
│   └── main.py               # App entry point
├── assets/                    # Static assets
├── data/
│   ├── sample_data.csv
│   ├── sample_data2.csv
│   └── sample_data3.csv
├── utils/
│   └── helpers.py            # Shared formatting helpers
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+

### Installation

```bash
git clone https://github.com/<your-username>/personal-finance-dashboard.git
cd personal-finance-dashboard
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 📊 CSV Format

Your CSV should include at least the following columns (column names are case-insensitive):

| Column        | Description                                              |
|---------------|-----------------------------------------------------------|
| `date`        | Transaction date (e.g., `2026-01-15`)                     |
| `amount`      | Transaction amount. Negative values are treated as expenses, positive as income |
| `category`    | Spending category (e.g., Groceries, Rent, Income)          |
| `description` | *(Optional)* Merchant or transaction description          |

If your CSV doesn't use negative values to mark income, transactions are classified as income based on keywords in the category (e.g., "income", "salary", "deposit", "paycheck", "dividend", "grant", "refund").

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) – App framework
- [Pandas](https://pandas.pydata.org/) – Data processing
- [Plotly](https://plotly.com/python/) – Interactive charts

---

## 📌 Notes

- The 6-month forecast is a simple linear projection based on historical average monthly savings and is intended for illustrative purposes only.
- Recurring payment detection uses transaction frequency and cadence heuristics (weekly, bi-weekly, monthly) and may not catch all subscriptions.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
