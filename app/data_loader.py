import pandas as pd

def load_and_clean_data(file_source) -> pd.DataFrame:
    """
    Ingests transaction CSV data, sanitizes schemas, maps automated sign splits,
    and returns a normalized operational tracking dataset.
    """
    df = pd.read_csv(file_source)
    df.columns = df.columns.str.lower()
    
    required_columns = ["date", "amount", "category"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV must contain these core columns: {required_columns}")
        
    df["date"] = pd.to_datetime(df["date"])
    df["category"] = df["category"].astype("str")
    
    # Sign-Based Income Split Engine
    has_negatives = (df["amount"] < 0).any()
    if has_negatives:
        df["is_income"] = df["amount"] > 0
    else:
        # Keyword tracking fallback if files lack negative symbols
        keyword_pattern = "income|salary|deposit|paycheck|dividend|grant|refund"
        df["is_income"] = df["category"].str.lower().str.contains(keyword_pattern, na=False)
        
    # Standardize out relative values for uniform computation
    df["amount"] = df["amount"].abs()
    df["category"] = df["category"].astype("category")
    
    return df