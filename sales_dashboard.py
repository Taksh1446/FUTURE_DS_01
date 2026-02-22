import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

st.title("📊 Business Analytics Task 1 - Sales Dashboard")

st.info("""
📌 **Dataset Format Requirement**

Please make sure your dataset contains the following columns exactly:

InvoiceNo, StockCode, Description, Quantity,
InvoiceDate, UnitPrice, CustomerID, Country
""")

# ==========================
# Sidebar Upload
# ==========================

st.sidebar.header("Filter Options")
uploaded_file = st.sidebar.file_uploader("Upload Sales Dataset", type=["csv"])

required_columns = [
    'InvoiceNo', 'StockCode', 'Description',
    'Quantity', 'InvoiceDate', 'UnitPrice',
    'CustomerID', 'Country'
]

if uploaded_file:

    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        st.error("Error reading file. Please upload valid CSV.")
        st.stop()

    # ✅ Column Validation
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"Dataset missing required columns: {missing_cols}")
        st.stop()

    # ==========================
    # Cleaning
    # ==========================

    df = df.dropna()
    df = df[df["Quantity"] > 0]
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df = df.dropna(subset=["InvoiceDate"])

    if df.empty:
        st.warning("No data available after cleaning.")
        st.stop()

    # ==========================
    # Date Filter
    # ==========================

    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["InvoiceDate"].dt.date >= start_date) &
                (df["InvoiceDate"].dt.date <= end_date)]

    # ==========================
    # Country Filter
    # ==========================

    countries = sorted(df["Country"].unique())
    selected_country = st.sidebar.selectbox("Select Country", ["All"] + countries)

    if selected_country != "All":
        df = df[df["Country"] == selected_country]

    if df.empty:
        st.warning("No data available for selected filters.")
        st.stop()

    df["Month"] = df["InvoiceDate"].dt.to_period("M")

    # ==========================
    # KPI Section
    # ==========================

    st.subheader("🔹 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"${df['Revenue'].sum():,.2f}")
    col2.metric("Total Orders", df["InvoiceNo"].nunique())
    col3.metric("Total Customers", df["CustomerID"].nunique())

    # ==========================
    # Monthly Revenue Trend
    # ==========================

    st.subheader("📈 Monthly Revenue Trend")

    monthly_revenue = df.groupby("Month")["Revenue"].sum()

    fig1, ax1 = plt.subplots()
    monthly_revenue.plot(ax=ax1)
    ax1.set_ylabel("Revenue")
    ax1.set_xlabel("Month")
    st.pyplot(fig1)

    # ==========================
    # Top Products
    # ==========================

    st.subheader("🏆 Top 10 Products by Revenue")

    top_products = (
        df.groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig2, ax2 = plt.subplots()
    top_products.plot(kind="barh", ax=ax2)
    ax2.invert_yaxis()
    st.pyplot(fig2)

    # ==========================
    # Top Countries
    # ==========================

    st.subheader("🌍 Revenue by Country")

    country_revenue = (
        df.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    fig3, ax3 = plt.subplots()
    country_revenue.plot(kind="bar", ax=ax3)
    st.pyplot(fig3)

    # ==========================
    # Download Button
    # ==========================

    st.subheader("📥 Download Filtered Data")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv",
    )

    # ==========================
    # Business Insights
    # ==========================

    st.subheader("💡 Business Insights & Recommendations")

    st.markdown("""
    - Revenue trends reveal seasonal sales patterns.
    - A small number of products contribute significantly to revenue.
    - Revenue is concentrated in selected high-performing countries.
    - Customer base includes high-value repeat buyers.

    ### Recommendations:
    - Increase marketing spend on top-performing products.
    - Expand operations in high-revenue countries.
    - Develop loyalty programs for frequent customers.
    - Use historical trends for inventory planning.
    """)

else:
    st.warning("Please upload your sales dataset to begin analysis.")
