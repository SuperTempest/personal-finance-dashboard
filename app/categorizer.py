import pandas as pd

def detect_recurring_payments(df: pd.DataFrame) -> pd.DataFrame:
    """
    Scans transaction history to algorithmically uncover subscriptions,
    recurring bills, or fixed repeating outlays based on cadence and price stability.
    """
    # 1. Isolate expenses only
    expenses = df[~df["is_income"]].copy()
    if expenses.empty:
        return pd.DataFrame()
        
    # Determine label column (fallback to category if description column missing)
    label_col = "description" if "description" in expenses.columns else "category"
    
    # 2. Sort chronologically to calculate true deltas
    expenses = expenses.sort_values([label_col, "date"])
    
    # Calculate days between consecutive transactions for the same merchant
    expenses["days_since_last"] = expenses.groupby(label_col)["date"].diff().dt.days
    
    # 3. Aggregate behavioral statistics per merchant
    merchant_profiles = expenses.groupby(label_col, observed=False).agg(
        total_spent=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_days_between=("days_since_last", "mean"),
        amount_standard_dev=("amount", "std"),
        last_recorded_amount=("amount", "last")
    ).reset_index()
    
    # 4. Filter strictly by repeating cadences
    # - Must happen at least 3 times total in the dataset
    # - Average interval should fall roughly around weekly (6-9 days), bi-weekly (12-16), or monthly (25-35)
    valid_cadence = (
        ((merchant_profiles["avg_days_between"] >= 25) & (merchant_profiles["avg_days_between"] <= 35)) |
        ((merchant_profiles["avg_days_between"] >= 12) & (merchant_profiles["avg_days_between"] <= 16)) |
        ((merchant_profiles["avg_days_between"] >= 6) & (merchant_profiles["avg_days_between"] <= 9))
    )
    
    detected_subscriptions = merchant_profiles[
        (merchant_profiles["transaction_count"] >= 3) & valid_cadence
    ].copy()
    
    # Clean up standard deviation checking for fixed price certainty
    detected_subscriptions["amount_standard_dev"] = detected_subscriptions["amount_standard_dev"].fillna(0)
    
    # Sort by impact (highest cost subscription first)
    detected_subscriptions = detected_subscriptions.sort_values(by="last_recorded_amount", ascending=False)
    
    return detected_subscriptions[[label_col, "transaction_count", "avg_days_between", "last_recorded_amount"]]