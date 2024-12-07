import pandas as pd
import plotly.express as px
import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set Streamlit page configuration
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

# ---- MAIN PAGE ----
st.header(":bar_chart: Sales Dashboard")
st.markdown("### Key Metrics")

# Key Performance Indicators (KPIs)
total_sales = round(df_selection["Sales"].sum(), 2)  # Total Sales
total_profit = round(df_selection["Profit"].sum(), 2)  # Total Profit
average_discount = round(df_selection["Discount"].mean() * 100, 1)  # Average Discount in %
total_orders = df_selection["Order ID"].nunique()  # Total Unique Orders
average_sales_per_order = round(total_sales / total_orders, 2)  # Avg Sales/Order

# Displaying KPIs
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.markdown(f"### Total Sales\n**${total_sales:,}**")
with middle_column:
    st.markdown(f"### Total Profit\n**${total_profit:,}**")
with right_column:
    st.markdown(f"### Avg Sales/Order\n**${average_sales_per_order:,}**")

st.markdown("---")

# Sales and Profit by Product Line [Stacked Area Chart]
sales_profit_by_product_line = (
    df_selection.groupby(by=["Sub_Category"])[["Sales", "Profit"]]
    .sum()
    .sort_values(by="Sales", ascending=False)
)

fig_sales_profit_area = px.area(
    sales_profit_by_product_line,
    x=sales_profit_by_product_line.index,
    y=["Sales", "Profit"],
    title="Sales and Profit by Product Line",
    labels={"value": "Amount (USD)", "variable": "Metric"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_sales_profit_area.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False, title="Product Line"),
    yaxis=dict(title="Amount (USD)", showgrid=True),
)

st.plotly_chart(fig_sales_profit_area, use_container_width=True)

# Sales and Profit by Category [Bar Chart]
sales_profit_by_category = (
    df_selection.groupby("Category")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)

fig_sales_profit = px.bar(
    sales_profit_by_category,
    x="Category",
    y=["Sales", "Profit"],
    title="Sales and Profit by Category",
    barmode="group",
    labels={"value": "Amount (USD)", "variable": "Metric"},
    template="plotly_white",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_sales_profit.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig_sales_profit, use_container_width=True)

# Sales by Region [Pie Chart]
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

# ---- AI-GENERATED INSIGHTS ----
st.markdown("### AI-Generated Insights")

# Prepare data summary for OpenAI
data_summary = (
    f"Dataset contains {len(df_selection)} records after filtering.\n"
    f"Total Sales: ${total_sales:,}\n"
    f"Total Profit: ${total_profit:,}\n"
    f"Average Discount: {average_discount}%\n"
    f"Average Sales per Order: ${average_sales_per_order:,}\n\n"
    f"Generate detailed insights and actionable recommendations based on this data."
)

# Button to trigger insights generation
if st.button("Generate Insights"):
    with st.spinner("Generating insights..."):
        try:
            # Get OpenAI insights
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert data analyst."},
                    {"role": "user", "content": data_summary},
                ],
                max_tokens=500,
                temperature=0.7,
            )

            # Extract and display AI-generated insights
            ai_insights = response["choices"][0]["message"]["content"].strip()
            st.subheader("AI-Generated Insights")
            st.write(ai_insights)

        except Exception as e:
            st.error(f"Error generating insights: {e}")
