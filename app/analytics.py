import pandas as pd

def apply_pipeline_filters(df: pd.DataFrame, selected_categories: list, start_date, end_date):
    """Slices datasets by custom interactive selections and active timeframes."""
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    filtered_expenses = df[
        (~df["is_income"]) & 
        (df["category"].isin(selected_categories)) & 
        (df["date"] >= start_date) & 
        (df["date"] <= end_date)
    ]
    
    filtered_income = df[
        (df["is_income"]) & 
        (df["date"] >= start_date) & 
        (df["date"] <= end_date)
    ]
    
    combined_ledger = pd.concat([filtered_expenses, filtered_income]).sort_values("date", ascending=False)
    return filtered_expenses, filtered_income, combined_ledger


def calculate_financial_metrics(filtered_income: pd.DataFrame, filtered_expenses: pd.DataFrame, combined_ledger: pd.DataFrame):
    """Aggregates balances, run rates, and monthly average outlays."""
    total_income = filtered_income["amount"].sum()
    total_spent = filtered_expenses["amount"].sum()
    net_savings = total_income - total_spent
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
    
    num_months = combined_ledger["date"].dt.to_period("M").nunique() if not combined_ledger.empty else 0
    avg_monthly_expense = total_spent / num_months if num_months > 0 else 0
    
    return {
        "total_income": total_income,
        "total_spent": total_spent,
        "net_savings": net_savings,
        "savings_rate": savings_rate,
        "avg_monthly_expense": avg_monthly_expense
    }


def generate_behavioral_insights(filtered_expenses: pd.DataFrame, savings_rate: float, total_income: float) -> list:
    """Audits tracking data to string-format analytical outliers for the UI carousel."""
    if filtered_expenses.empty:
        return []
        
    category_totals = filtered_expenses.groupby("category", observed=False)["amount"].sum()
    top_category = category_totals.idxmax()
    top_cat_amount = category_totals.max()
    
    insights = [
        f"Your heaviest spending category in this selection is **{top_category}**, totaling **${top_cat_amount:,.2f}**.",
        f"The single largest expense transaction in this timeframe was **${filtered_expenses['amount'].max():,.2f}**.",
        f"You made a total of **{len(filtered_expenses)}** individual purchases across this period.",
        f"Your average individual swipe or purchase size was **${filtered_expenses['amount'].mean():,.2f}**."
    ]
    
    if total_income > 0:
        insights.append(f"You managed to save **{savings_rate:.1f}%** of your total incoming revenue during this window.")
        
    return insights


def calculate_financial_forecast(df: pd.DataFrame, months_to_project: int = 6) -> pd.DataFrame:
    """
    Traces true historical cumulative net worth progression and attaches
    a seamless, connected future projection runway.
    """
    if df.empty:
        return pd.DataFrame()
        
    temp_df = df.copy()
    temp_df["month_period"] = temp_df["date"].dt.to_period("M")
    
    # 1. Calculate historical metrics per month
    monthly_totals = temp_df.groupby(["month_period", "is_income"])["amount"].sum().unstack(fill_value=0)
    monthly_totals = monthly_totals.rename(columns={True: "Income", False: "Expense"})
    
    if "Income" not in monthly_totals.columns: monthly_totals["Income"] = 0
    if "Expense" not in monthly_totals.columns: monthly_totals["Expense"] = 0
    
    monthly_totals = monthly_totals.sort_index()
    monthly_totals["Net Savings"] = monthly_totals["Income"] - monthly_totals["Expense"]
    monthly_totals["Cumulative Savings"] = monthly_totals["Net Savings"].cumsum()
    
    forecast_records = []
    
    # 2. Append full historical curve
    for period, row in monthly_totals.iterrows():
        month_date = period.to_timestamp()
        forecast_records.append({
            "Month": month_date.strftime("%b %Y"),
            "Projected Balance ($)": row["Cumulative Savings"],
            "Type": "Historical Baseline"
        })
        
    # 3. Establish the bridge anchor point
    last_cumulative = monthly_totals["Cumulative Savings"].iloc[-1]
    last_period_date = monthly_totals.index[-1].to_timestamp()
    
    forecast_records.append({
        "Month": last_period_date.strftime("%b %Y"),
        "Projected Balance ($)": last_cumulative,
        "Type": "Algorithmic Forecast"
    })
    
    # 4. Project future steps smoothly from baseline metrics
    avg_monthly_savings = monthly_totals["Net Savings"].mean()
    running_balance = last_cumulative
    
    for i in range(1, months_to_project + 1):
        future_date = last_period_date + pd.DateOffset(months=i)
        running_balance += avg_monthly_savings
        
        forecast_records.append({
            "Month": future_date.strftime("%b %Y"),
            "Projected Balance ($)": running_balance,
            "Type": "Algorithmic Forecast"
        })
        
    return pd.DataFrame(forecast_records)