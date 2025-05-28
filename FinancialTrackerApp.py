import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

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

def edit_table(sheet_name):
    st.subheader(f"{sheet_name} Entry")
    df = st.session_state.data[sheet_name]
    edited = st.experimental_data_editor(df, num_rows="dynamic", key=sheet_name)
    st.session_state.data[sheet_name] = edited

# --- Home Page ---
if choice == '🏠 Home':
    st.title("💰 Overview")
    inc = st.session_state.data['Income'][
        st.session_state.data['Income']['Recurring']=='Yes']['Amount'].sum()
    emi = st.session_state.data['Credit Card EMI'][
        st.session_state.data['Credit Card EMI']['Active']=='Yes']['EMI Amount'].sum()
    fix = st.session_state.data['Fixed Expense']['Monthly Amount'].sum()
    leftover = inc - emi - fix

    cols = st.columns(4)
    cols[0].metric("Monthly Income", f"₹{inc:,.0f}")
    cols[1].metric("Active EMI", f"₹{emi:,.0f}")
    cols[2].metric("Fixed Expenses", f"₹{fix:,.0f}")
    cols[3].metric("Leftover", f"₹{leftover:,.0f}")

    st.markdown("---")
    st.subheader("Expense Breakdown")
    breakdown = pd.DataFrame({
        'Category': ['EMI', 'Fixed', 'Leftover'],
        'Amount': [emi, fix, max(leftover, 0)]
    })
    pie = alt.Chart(breakdown).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field='Amount', type='quantitative'),
        color=alt.Color(field='Category', type='nominal'),
        tooltip=[alt.Tooltip('Category'), alt.Tooltip('Amount', format='₹,.0f')]
    )
    st.altair_chart(pie, use_container_width=True)

# --- Data Entry Pages ---
elif choice == '💼 Data Entry':
    st.title("📝 Data Entry")
    selected = st.selectbox("Select Module", data_pages)
    edit_table(selected)
    if st.button("Save Data"):
        st.success(f"{selected} data saved.")

# --- Dashboards ---
elif choice == '📊 Dashboards':
    st.title("📈 Dashboards")
    tab1, tab2 = st.tabs(["Annual Overview", "Trends"])

    with tab1:
        st.subheader("Annual Overview")
        inc_df = st.session_state.data['Income']
        fix_df = st.session_state.data['Fixed Expense']
        emi_df = st.session_state.data['Credit Card EMI']
        exp_df = st.session_state.data['Monthly Expenses']
        loan_df = st.session_state.data['Loans']
        months = pd.date_range('2025-01-01', periods=12, freq='MS').strftime('%b')
        rows = []
        for m in months:
            mn = datetime.strptime(m, '%b').month
            rows.append({
                'Month': m,
                'Income': inc_df[inc_df['Recurring']=='Yes']['Amount'].sum(),
                'EMI': emi_df[emi_df['Active']=='Yes']['EMI Amount'].sum(),
                'Expenses': exp_df[exp_df['Date'].dt.month==mn]['Amount'].sum(),
                'Loan EMI': loan_df['EMI'].sum(),
                'Fixed': fix_df['Monthly Amount'].sum()
            })
        ann = pd.DataFrame(rows)
        ann['Leftover'] = ann['Income'] - ann['EMI'] - ann['Expenses'] - ann['Loan EMI'] - ann['Fixed']
        st.dataframe(ann.style.format({
            'Income':'₹{:,.0f}','EMI':'₹{:,.0f}','Expenses':'₹{:,.0f}',
            'Loan EMI':'₹{:,.0f}','Fixed':'₹{:,.0f}','Leftover':'₹{:,.0f}'
        }), use_container_width=True)

    with tab2:
        st.subheader("Last 6 Months Leftover Trend")
        last6 = ann.tail(6)
        line = alt.Chart(last6).mark_line(point=True).encode(
            x='Month:N',
            y=alt.Y('Leftover', title='Leftover (₹)'),
            tooltip=[alt.Tooltip('Month'), alt.Tooltip('Leftover', format='₹,.0f')]
        ).properties(width=600)
        st.altair_chart(line, use_container_width=True)

# --- Future Projections ---
elif choice == '🔮 Projections':
    st.title("🔮 Future Projections")
    st.info("Machine learning integration coming soon to forecast your net worth trajectory.")

# --- Footer ---
st.markdown("---")
st.caption("Built with ❤️ using Streamlit | © 2025 Financial Tracker")
