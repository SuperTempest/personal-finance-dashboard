import streamlit as st
import pandas as pd
import plotly.express as px
import data_loader
import analytics
import categorizer

def render_dashboard():
    st.title("💸 Personal Finance & Cash Flow Dashboard")
    st.markdown("---")

    # File Selection Sidebar Ingestion
    st.sidebar.header("📁 Data Source")
    uploaded_file = st.sidebar.file_uploader("Upload your bank CSV:", type=["csv"])

    try:
        if uploaded_file is not None:
            df = data_loader.load_and_clean_data(uploaded_file)
            st.sidebar.success("Custom data loaded successfully!")
        else:
            df = data_loader.load_and_clean_data("data/sample_data.csv")
            st.sidebar.info("Showing sample data. Upload your own CSV above!")
            
    except Exception as e:
        st.sidebar.error(f"⚠️ {e}")
        st.stop()

    # Interactive Filter Construction
    st.sidebar.header("Dashboard Filters")
    expense_categories = df[~df["is_income"]]["category"].unique()
    selected_categories = st.sidebar.multiselect(
        "Filter Expenses by Category:",
        options=expense_categories,
        default=expense_categories
    )

    st.sidebar.markdown("---")
    date_option = st.sidebar.selectbox(
        "Choose Timeframe:",
        ["All Time", "Year to Date", "Last 6 Months", "Last 3 Months", "Custom Range"]
    )

    min_date, max_date = df["date"].min(), df["date"].max()
    if date_option == "All Time":
        start_date, end_date = min_date, max_date
    elif date_option == "Year to Date":
        start_date, end_date = pd.to_datetime(f"{max_date.year}-01-01"), max_date
    elif date_option == "Last 6 Months":
        start_date, end_date = max_date - pd.Timedelta(days=180), max_date
    elif date_option == "Last 3 Months":
        start_date, end_date = max_date - pd.Timedelta(days=90), max_date
    elif date_option == "Custom Range":
        col_start, col_end = st.sidebar.columns(2)
        with col_start:
            start_val = st.date_input("Start:", min_date, min_value=min_date, max_value=max_date)
        with col_end:
            end_val = st.date_input("End:", max_date, min_value=min_date, max_value=max_date)
        start_date, end_date = pd.to_datetime(start_val), pd.to_datetime(end_val)

    # Execute Data Split Processing Pipeline
    filtered_expenses, filtered_income, filtered_df = analytics.apply_pipeline_filters(
        df, selected_categories, start_date, end_date
    )

    # Extract core balance metrics
    metrics = analytics.calculate_financial_metrics(filtered_income, filtered_expenses, filtered_df)

    # Render Metric Display Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Income", f"${metrics['total_income']:,.2f}")
    with col2:
        st.metric("Total Expenses", f"${metrics['total_spent']:,.2f}") 
    with col3:
        st.metric(
            "Net Savings Balance", 
            f"${metrics['net_savings']:,.2f}", 
            delta=f"{metrics['savings_rate']:.1f}% Savings Rate", 
            delta_color="normal" if metrics['net_savings'] >= 0 else "inverse"
        )

    # Interactive Budget Monitor
    st.markdown("### 🎯 Monthly Budget Progress")
    budget_target = st.number_input("Set your monthly spending target ($):", value=2000, step=100)

    if budget_target > 0:
        pct_used = min(metrics['avg_monthly_expense'] / budget_target, 1.0)
        if metrics['avg_monthly_expense'] > budget_target:
            st.error(f"⚠️ You are exceeding your monthly target by **${(metrics['avg_monthly_expense'] - budget_target):,.2f}** per month!")
        else:
            st.success(f"✅ Your average monthly outlay (${metrics['avg_monthly_expense']:,.2f}/mo) is pacing safely under budget targets.")
        st.progress(pct_used)

    # Interactive Insight Carousel
    insights_pool = analytics.generate_behavioral_insights(filtered_expenses, metrics['savings_rate'], metrics['total_income'])
    if insights_pool:
        if "insight_index" not in st.session_state:
            st.session_state.insight_index = 0
        if st.session_state.insight_index >= len(insights_pool):
            st.session_state.insight_index = 0

        col_title, col_prev, col_next, col_filler = st.columns([2.5, 0.3, 0.3, 16], vertical_alignment="center")
        with col_title:
            st.markdown("### 💡 Quick Insights")
        with col_prev:
            if st.button("◀", key="prev_btn"):
                st.session_state.insight_index = (st.session_state.insight_index - 1) % len(insights_pool)
                st.rerun()
        with col_next:
            if st.button("▶", key="next_btn"):
                st.session_state.insight_index = (st.session_state.insight_index + 1) % len(insights_pool)
                st.rerun()

        st.info(insights_pool[st.session_state.insight_index])
        st.caption(f"Insight {st.session_state.insight_index + 1} of {len(insights_pool)}")

    st.markdown("---")

    # Render Core Financial Charts
    chart_col, table_col = st.columns([1, 1])

    with chart_col:
        st.subheader("Spending Breakdown")
        if not filtered_expenses.empty:
            category_summary = filtered_expenses.groupby("category", observed=False)["amount"].sum().reset_index()
            fig = px.pie(category_summary, values="amount", names="category", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            fig.update_traces(hovertemplate="<b>%{label}</b><br>Total Spent: $%{value:,.2f}<br>Share: %{percent}<extra></extra>")
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("No expense records match selected criteria.")

    with table_col:
        st.subheader("Unified Ledger (Income & Expenses)")
        display_df = filtered_df.copy()
        if not display_df.empty:
            display_df["date"] = display_df["date"].dt.strftime('%Y-%m-%d')
            display_df["type"] = display_df["is_income"].map({True: "🟢 Income", False: "🔴 Expense"})
            
            label_col = "description" if "description" in display_df.columns else "category"
            st.dataframe(display_df[["date", label_col, "category", "type", "amount"]], width="stretch", hide_index=True)

    # Render Cash Flow Trends Timeline Component
    st.markdown("---")
    st.subheader("📊 Monthly Cash Flow Trend (Income vs. Expenses)")

    if not filtered_df.empty:
        trend_df = filtered_df.copy()
        trend_df["month"] = trend_df["date"].dt.strftime("%Y-%m")
        trend_df["Type"] = trend_df["is_income"].map({True: "Income", False: "Expense"})
        
        monthly_trend = trend_df.groupby(["month", "Type"], observed=False)["amount"].sum().reset_index().sort_values("month")
        
        fig_trend = px.bar(
            monthly_trend, 
            x="month", 
            y="amount", 
            color="Type", 
            barmode="group",
            labels={"month": "Billing Period", "amount": "Total Value ($)"},
            color_discrete_map={"Income": "#2e7d32", "Expense": "#c62828"}
        )
        fig_trend.update_layout(margin=dict(t=20, b=20, l=0, r=0), legend_title=None)
        st.plotly_chart(fig_trend, width="stretch")

    # ==========================================
    # 🔮 LINEAR FINANCIAL FORECASTING ENGINE
    # ==========================================
    st.markdown("---")
    st.subheader("🔮 6-Month Cash Flow & Net Wealth Forecast")
    
    forecast_df = analytics.calculate_financial_forecast(df, months_to_project=6)
    
    if not forecast_df.empty:
        f_rows = forecast_df[forecast_df["Type"] == "Algorithmic Forecast"]
        net_delta = f_rows.iloc[-1]["Projected Balance ($)"] - f_rows.iloc[0]["Projected Balance ($)"]
        
        color_theme = "#059669" if net_delta >= 0 else "#dc2626"
        fill_theme = "rgba(5, 150, 105, 0.04)" if net_delta >= 0 else "rgba(220, 38, 38, 0.04)"
        
        fig_forecast = px.line(
            forecast_df,
            x="Month",
            y="Projected Balance ($)",
            color="Type",
            markers=True,
            color_discrete_map={"Historical Baseline": "#475569", "Algorithmic Forecast": color_theme}
        )
        
        fig_forecast.update_traces(line=dict(width=3, shape="spline"), marker=dict(size=6))
        
        for trace in fig_forecast.data:
            if "Forecast" in trace.name:
                trace.line.dash = "dash"
                trace.fill = "tozeroy"
                trace.fillcolor = fill_theme
                
        fig_forecast.update_layout(
            margin=dict(t=20, b=20, l=0, r=0),
            xaxis_title=None,
            yaxis_title="Cumulative Balance ($)",
            legend_title=None,
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="rgba(0,0,0,0.06)"),
            xaxis=dict(gridcolor="rgba(0,0,0,0.06)")
        )
        
        st.plotly_chart(fig_forecast, width="stretch")
        
        if net_delta >= 0:
            st.success(f"📈 **Positive Growth Vector:** At your current rate, you are on pace to accumulate an additional **${net_delta:,.2f}** in net savings over the next 6 months!")
        else:
            st.error(f"⚠️ **Cash Burn Warning:** Deficit trajectory. Pacing to drop your capital reserves by **${abs(net_delta):,.2f}** over the next 6 months if habits aren't adjusted.")

    # ==========================================
    # 🔁 RECURRING PAYMENT DETECTOR
    # ==========================================
    st.markdown("---")
    st.subheader("🔁 Detected Recurring Commitments & Subscriptions")
    
    subscriptions_df = categorizer.detect_recurring_payments(df)
    if not subscriptions_df.empty:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            st.metric("Total Monthly Commitment", f"${subscriptions_df['last_recorded_amount'].sum():,.2f}")
        with sub_col2:
            st.metric("Active Subscriptions Found", f"{len(subscriptions_df)} items")
            
        label_col = "description" if "description" in subscriptions_df.columns else "category"
        display_subs = subscriptions_df.copy()
        display_subs["Estimated Frequency"] = display_subs["avg_days_between"].apply(
            lambda x: "Monthly" if 25 <= x <= 35 else ("Bi-Weekly" if 12 <= x <= 16 else "Weekly")
        )
        display_subs = display_subs.rename(columns={label_col: "Merchant", "transaction_count": "Swipes", "last_recorded_amount": "Cost"})
        st.dataframe(display_subs[["Merchant", "Estimated Frequency", "Swipes", "Cost"]], width="stretch", hide_index=True)
    else:
        st.info("No clear subscription intervals detected within this dataset.")

    # Interactive Category Deep-Dive Explorer
    st.markdown("---")
    st.subheader("🔍 Category Deep-Dive Explorer")

    dive_category = st.selectbox("Select any category to audit closely:", options=df["category"].unique())
    dive_df = filtered_df[filtered_df["category"] == dive_category]

    if not dive_df.empty:
        dive_df = dive_df.sort_values("date")
        
        cat_col1, cat_col2, cat_col3 = st.columns(3)
        with cat_col1:
            st.metric(f"Total {dive_category} Volume", f"${dive_df['amount'].sum():,.2f}")
        with cat_col2:
            st.metric("Activity Count", f"{len(dive_df)} records")
        with cat_col3:
            st.metric("Average Purchase Size", f"${dive_df['amount'].mean():,.2f}")
            
        daily_dive = dive_df.groupby("date")["amount"].sum().reset_index()
        fig_area = px.area(daily_dive, x="date", y="amount", color_discrete_sequence=["#2b5c8f"])
        fig_area.update_layout(margin=dict(t=20, b=20, l=0, r=0), xaxis_title=None)
        st.plotly_chart(fig_area, width="stretch")