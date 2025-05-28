import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import numpy_financial as npf

# --- App Configuration ---
st.set_page_config(
    page_title="Financial Tracker", 
    page_icon="💰", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- Custom CSS for UI ---
st.markdown(
    """
    <style>
    .reportview-container .main .block-container { padding:1rem 2rem; }
    .sidebar .sidebar-content { background-color: #f0f2f6; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; padding:10px; }
    </style>
    """, 
    unsafe_allow_html=True
)

# --- Session State Initialization ---
if 'data' not in st.session_state:
    st.session_state.data = {
        'Income': pd.DataFrame(columns=['Type', 'Recurring', 'Amount']),
        'Fixed Expense': pd.DataFrame(columns=['Category', 'Monthly Amount']),
        'Credit Cards': pd.DataFrame(columns=['Name', 'Billing Date', 'Period Start', 'Period End', 'Due Date']),
        'Credit Card EMI': pd.DataFrame(columns=[
            'Card Name', 'EMI Amount', 'Interest %', 'Start Date', 'End Date',
            'Duration', 'Paid', 'Current Principal', 'Current Interest',
            'Foreclosure Charge', 'Foreclosure Amount', 'Active'
        ]),
        'Monthly Expenses': pd.DataFrame(columns=['Category', 'Payment Type', 'Amount', 'Date']),
        'Loans': pd.DataFrame(columns=['Type', 'Total', 'Interest %', 'Duration', 'EMI', 'EMI Date']),
        'Savings': pd.DataFrame(columns=['Month', 'Target Savings', 'Actual Savings', 'Notes'])
    }

# --- Sidebar Navigation ---
st.sidebar.image(
    "https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png", width=120
)
st.sidebar.title("Financial Tracker")
st.sidebar.markdown(
    """
    **Monitor. Analyze. Achieve.**

    Navigate modules to track and optimize your finances.
    """
)
menu = ['🏠 Home', '💼 Data Entry', '📊 Dashboards', '🔮 Projections']
choice = st.sidebar.radio("Go to", menu)

data_pages = ['Income', 'Fixed Expense', 'Credit Cards', 'Credit Card EMI', 'Monthly Expenses', 'Loans', 'Savings']

# --- Data Entry Utility ---
def edit_table(sheet_name):
    st.subheader(f"{sheet_name} Entry")
    df = st.session_state.data[sheet_name]

    # Auto-calculate formulas for Credit Card EMI
    if sheet_name == 'Credit Card EMI' and not df.empty:
        df['Duration'] = df.apply(lambda row: (pd.to_datetime(row['End Date']) - pd.to_datetime(row['Start Date'])).days // 30 if pd.notnull(row['Start Date']) and pd.notnull(row['End Date']) else None, axis=1)
        df['Current Principal'] = df.apply(
            lambda row: npf.ppmt(rate=row['Interest %']/1200, nper=row['Duration'], per=row['Paid']+1, pv=row['EMI Amount']) if pd.notnull(row['Interest %']) and pd.notnull(row['Duration']) and pd.notnull(row['Paid']) and pd.notnull(row['EMI Amount']) else None,
            axis=1
        )
        df['Current Interest'] = df.apply(
            lambda row: npf.ipmt(rate=row['Interest %']/1200, nper=row['Duration'], per=row['Paid']+1, pv=row['EMI Amount']) if pd.notnull(row['Interest %']) and pd.notnull(row['Duration']) and pd.notnull(row['Paid']) and pd.notnull(row['EMI Amount']) else None,
            axis=1
        )
        df['Foreclosure Charge'] = df.apply(
            lambda row: abs(npf.fv(rate=row['Interest %']/1200, nper=row['Paid'], pmt=row['EMI Amount'], pv=0)) * 0.02 if pd.notnull(row['Interest %']) and pd.notnull(row['Paid']) and pd.notnull(row['EMI Amount']) else None,
            axis=1
        )
        df['Foreclosure Amount'] = df.apply(
            lambda row: abs(npf.fv(rate=row['Interest %']/1200, nper=row['Paid'], pmt=row['EMI Amount'], pv=0)) + row['Foreclosure Charge'] if pd.notnull(row['Interest %']) and pd.notnull(row['Paid']) and pd.notnull(row['EMI Amount']) and pd.notnull(row['Foreclosure Charge']) else None,
            axis=1
        )
        df['Active'] = df.apply(lambda row: "No" if row['Paid'] >= row['Duration'] else "Yes" if pd.notnull(row['Paid']) and pd.notnull(row['Duration']) else None, axis=1)

    try:
        edited = st.data_editor(df, num_rows="dynamic", key=sheet_name)
    except AttributeError:
        edited = st.experimental_data_editor(df, num_rows="dynamic", key=sheet_name)
    st.session_state.data[sheet_name] = edited

# [Remaining home page, dashboards, and footer remain unchanged]
