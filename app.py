import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="AI Sales Dashboard", page_icon=":bar_chart:", layout="wide")

# Load the dataset
df = pd.read_csv('Dataset.csv')

# Sidebar filters
st.sidebar.header("Please Filter Here:")
Region = st.sidebar.multiselect(
    "Select the Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)
Segment = st.sidebar.multiselect(
    "Select the Segment:",
    options=df["Segment"].unique(),
    default=df["Segment"].unique()
)
Ship_Mode = st.sidebar.multiselect(
    "Select the Ship Mode:",
    options=df["Ship_Mode"].unique(),
    default=df["Ship_Mode"].unique()
)

# Data selection based on filters
df_selection = df.query(
    "Region == @Region & Segment == @Segment & Ship_Mode == @Ship_Mode"
)

if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

# ---- MAINPAGE ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("#")

# TOP KPIs
total_sales = round(df_selection["Sales"].sum(), 2)  # Sum of all sales
total_profit = round(df_selection["Profit"].sum(), 2)  # Sum of all profit
average_discount = round(df_selection["Discount"].mean() * 100, 1)  # Average discount in percentage
total_orders = df_selection["Order ID"].nunique()  # Count of unique orders
average_sales_per_order = round(total_sales / total_orders, 2)  # Average sales per order

# Main KPIs
left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.markdown(
        "<h5 style='margin-bottom: 5px;'>Total Sales:</h5>"
        f"<h4 style='color: #0083B8;'>US $ {total_sales:,}</h4>",
        unsafe_allow_html=True,
    )

with middle_column:
    st.markdown(
        "<h5 style='margin-bottom: 5px;'>Total Profit:</h5>"
        f"<h4 style='color: #0083B8;'>US $ {total_profit:,}</h4>",
        unsafe_allow_html=True,
    )

with right_column:
    st.markdown(
        "<h5 style='margin-bottom: 5px;'>Avg Sales/Order:</h5>"
        f"<h4 style='color: #0083B8;'>US $ {average_sales_per_order:,}</h4>",
        unsafe_allow_html=True,
    )

st.markdown("""---""")

# SALES AND PROFIT BY PRODUCT LINE [STACKED AREA CHART]
sales_profit_by_product_line = df_selection.groupby(by=["Sub_Category"])[["Sales", "Profit"]].sum().sort_values(by="Sales", ascending=False)

fig_sales_profit_area = px.area(
    sales_profit_by_product_line,
    x=sales_profit_by_product_line.index,
    y=["Sales", "Profit"],
    title="<b>Sales and Profit by Product Line</b>",
    labels={"value": "Amount (USD)", "variable": "Metric"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set2
)

# Customize layout for area chart
fig_sales_profit_area.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, title="Product Line"),
    yaxis=dict(title="Amount (USD)", showgrid=True),
)

# Display the chart
st.plotly_chart(fig_sales_profit_area, use_container_width=True)

# Group data by Category and calculate Sales and Profit
sales_profit_by_category = df_selection.groupby("Category")[["Sales", "Profit"]].sum().reset_index()

# Create a grouped bar chart for sales and profit by category
fig_sales_profit = px.bar(
    sales_profit_by_category,
    x="Category",
    y=["Sales", "Profit"],
    title="<b>Sales and Profit by Category</b>",
    barmode="group",
    labels={"value": "Amount (USD)", "variable": "Metric"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set2
)

# Customize layout for the bar chart
fig_sales_profit.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

# Display the grouped bar chart with full width
st.plotly_chart(fig_sales_profit, use_container_width=True)

# Total Sales and Profit by Region
sales_profit_by_region = df_selection.groupby("Region")[["Sales", "Profit"]].sum().reset_index()

fig_sales_profit_region = px.pie(
    sales_profit_by_region,
    names="Region",
    values="Sales",
    title="Total Sales by Region",
    template="plotly_white"
)

fig_sales_profit_region.update_traces(textinfo="percent+label")
st.plotly_chart(fig_sales_profit_region, use_container_width=True)

