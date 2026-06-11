def format_currency(val: float) -> str:
    """Standardizes string parsing format for currency data metrics."""
    return f"${val:,.2f}"