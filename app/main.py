import streamlit as st
import dashboard

# Global configuration initialization
st.set_page_config(layout="wide", page_title="Cash Flow & Budget Engine")

if __name__ == "__main__":
    dashboard.render_dashboard()