# Step 1: Basic Streamlit Setup
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="A/B Testing Dashboard", layout="wide")

# Dashboard Title
st.title("A/B Testing Analysis: Facebook vs AdWords")

# Load dataset
df = pd.read_csv("A_B_testing_dataset.csv")

# Show dataset preview
st.subheader("Dataset Preview")
st.dataframe(df.head())

# -----------------------------
# Step 2: Reshape Data
# -----------------------------

# Facebook data
facebook = df[[
    "date_of_campaign", "facebook_ad_views", "facebook_ad_clicks",
    "facebook_ad_conversions", "facebook_cost_per_ad",
    "facebook_ctr", "facebook_conversion_rate", "facebook_cost_per_click"
]].copy()
facebook["platform"] = "Facebook"
facebook.columns = [
    "date", "views", "clicks", "conversions", "cost_per_ad",
    "ctr", "conversion_rate", "cost_per_click", "platform"
]

# AdWords data
adwords = df[[
    "date_of_campaign", "adword_ad_views", "adword_ad_clicks",
    "adword_ad_conversions", "adword_cost_per_ad",
    "adword_ctr", "adword_conversion_rate", "adword_cost_per_click"
]].copy()
adwords["platform"] = "AdWords"
adwords.columns = facebook.columns

# Combine both platforms
df_long = pd.concat([facebook, adwords], ignore_index=True)

# Display reshaped data
st.subheader("Reshaped Dataset Preview")
st.dataframe(df_long.head())

# -----------------------------
# Step 3: Platform Summary Metrics
# -----------------------------

st.subheader("Platform Summary Metrics")
platform_summary = df_long.groupby("platform").agg({
    "views": ["sum", "mean"],
    "clicks": ["sum", "mean"],
    "conversions": ["sum", "mean"],
    "cost_per_ad": "mean",
    "ctr": "mean",
    "conversion_rate": "mean",
    "cost_per_click": "mean"
}).round(2)

platform_summary.columns = ['_'.join(col).strip() for col in platform_summary.columns.values]
platform_summary.reset_index(inplace=True)
st.dataframe(platform_summary)

# -----------------------------
# Step 4: Visualizations
# -----------------------------

st.subheader("Visual Comparison of Platforms")

st.write("### Total Views by Platform")
st.bar_chart(platform_summary.set_index("platform")["views_sum"])

st.write("### Total Clicks by Platform")
st.bar_chart(platform_summary.set_index("platform")["clicks_sum"])

st.write("### Average Conversion Rate by Platform")
st.bar_chart(platform_summary.set_index("platform")["conversion_rate_mean"])

st.write("### Average Click-Through Rate (CTR) by Platform")
st.bar_chart(platform_summary.set_index("platform")["ctr_mean"])

# Interactive time-series charts
st.subheader("Time-Series Metrics Comparison")
fig_views = px.line(df_long, x="date", y="views", color="platform",
                    title="Daily Views Over Time", markers=True)
st.plotly_chart(fig_views, use_container_width=True)

fig_clicks = px.line(df_long, x="date", y="clicks", color="platform",
                     title="Daily Clicks Over Time", markers=True)
st.plotly_chart(fig_clicks, use_container_width=True)

fig_conversion = px.line(df_long, x="date", y="conversion_rate", color="platform",
                         title="Daily Conversion Rate Over Time", markers=True)
st.plotly_chart(fig_conversion, use_container_width=True)

# -----------------------------
# Step 5: Filters
# -----------------------------

st.subheader("Filter Data")
df_long['date'] = pd.to_datetime(df_long['date'])

start_date = st.date_input("Start Date", df_long['date'].min())
end_date = st.date_input("End Date", df_long['date'].max())
platform_options = st.multiselect("Select Platform(s)", options=df_long['platform'].unique(),
                                  default=list(df_long['platform'].unique()))

filtered_data = df_long[
    (df_long['date'] >= pd.to_datetime(start_date)) &
    (df_long['date'] <= pd.to_datetime(end_date)) &
    (df_long['platform'].isin(platform_options))
]

st.write("### Filtered Data Preview")
st.dataframe(filtered_data.head())

# Update filtered charts
fig_views_filtered = px.line(filtered_data, x="date", y="views", color="platform",
                             title="Filtered Daily Views Over Time", markers=True)
st.plotly_chart(fig_views_filtered, use_container_width=True)

# -----------------------------
# Step 6: Key Insights
# -----------------------------

st.subheader("Key Insights")

total_views = filtered_data.groupby("platform")["views"].sum()
total_clicks = filtered_data.groupby("platform")["clicks"].sum()
total_conversions = filtered_data.groupby("platform")["conversions"].sum()
avg_ctr = filtered_data.groupby("platform")["ctr"].mean().round(2)
avg_conversion_rate = filtered_data.groupby("platform")["conversion_rate"].mean().round(2)
avg_cost_per_click = filtered_data.groupby("platform")["cost_per_click"].mean().round(2)

# Helper function to format numbers
def format_num(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)

# -----------------------------
# Step 7: Key Insights with Highlights
# -----------------------------

st.subheader("Key Insights with Highlights")

def highlight_metric(fb_val, aw_val, metric_type="higher_better"):
    if metric_type == "higher_better":
        if fb_val > aw_val:
            return f"**FB: {fb_val} ✅** | AW: {aw_val}"
        elif fb_val < aw_val:
            return f"FB: {fb_val} | **AW: {aw_val} ✅**"
    elif metric_type == "lower_better":
        if fb_val < aw_val:
            return f"**FB: {fb_val} ✅** | AW: {aw_val}"
        else:
            return f"FB: {fb_val} | **AW: {aw_val} ✅**"
    return f"FB: {fb_val} | AW: {aw_val}"

# Format metrics for display
total_views_fb = format_num(total_views.get("Facebook",0))
total_views_aw = format_num(total_views.get("AdWords",0))
total_clicks_fb = format_num(total_clicks.get("Facebook",0))
total_clicks_aw = format_num(total_clicks.get("AdWords",0))
total_conv_fb = format_num(total_conversions.get("Facebook",0))
total_conv_aw = format_num(total_conversions.get("AdWords",0))
avg_ctr_fb = f"{avg_ctr.get('Facebook',0)}%"
avg_ctr_aw = f"{avg_ctr.get('AdWords',0)}%"
avg_conv_fb = f"{avg_conversion_rate.get('Facebook',0)}%"
avg_conv_aw = f"{avg_conversion_rate.get('AdWords',0)}%"
avg_cpc_fb = f"${avg_cost_per_click.get('Facebook',0)}"
avg_cpc_aw = f"${avg_cost_per_click.get('AdWords',0)}"

# Display metrics with highlights
row1_col1, row1_col2, row1_col3 = st.columns(3)
row1_col1.markdown(f"**Views:** {highlight_metric(total_views_fb, total_views_aw)}")
row1_col2.markdown(f"**Clicks:** {highlight_metric(total_clicks_fb, total_clicks_aw)}")
row1_col3.markdown(f"**Conversions:** {highlight_metric(total_conv_fb, total_conv_aw)}")

row2_col1, row2_col2, row2_col3 = st.columns(3)
row2_col1.markdown(f"**Avg CTR:** {highlight_metric(avg_ctr_fb, avg_ctr_aw)}")
row2_col2.markdown(f"**Avg Conv Rate:** {highlight_metric(avg_conv_fb, avg_conv_aw)}")
row2_col3.markdown(f"**Avg CPC:** {highlight_metric(avg_cpc_fb, avg_cpc_aw, metric_type='lower_better')}")

# Overall best platform
best_platform = "Facebook" if avg_conversion_rate.get("Facebook",0) > avg_conversion_rate.get("AdWords",0) else "AdWords"
st.info(f"💡 Insight: Overall, **{best_platform}** is performing better in conversions.")
