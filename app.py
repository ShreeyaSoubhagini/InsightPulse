import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="InsightPulse",
    page_icon="📊",
    layout="wide"
)


# -----------------------------
# Load Data
# -----------------------------

conn = sqlite3.connect("notebook/ecommerce_reviews.db")

df = pd.read_sql_query(
    "SELECT * FROM reviews",
    conn
)

conn.close()


# -----------------------------
# Sidebar Filters
# -----------------------------

st.sidebar.header("Dashboard Filters")

departments = sorted(
    df["Department Name"].dropna().unique()
)

selected_department = st.sidebar.selectbox(
    "Department",
    ["All"] + departments
)

ratings = sorted(
    df["Rating"].dropna().unique()
)

selected_rating = st.sidebar.multiselect(
    "Rating",
    ratings,
    default=ratings
)


# -----------------------------
# Apply Filters
# -----------------------------

filtered_df = df.copy()

if selected_department != "All":
    filtered_df = filtered_df[
        filtered_df["Department Name"] == selected_department
    ]

if selected_rating:
    filtered_df = filtered_df[
        filtered_df["Rating"].isin(selected_rating)
    ]


# Prevent errors if no data is selected
if filtered_df.empty:
    st.warning("No reviews match the selected filters.")
    st.stop()


# -----------------------------
# Title
# -----------------------------

st.title("📊 InsightPulse")

st.subheader(
    "E-Commerce Customer Voice Analytics"
)

st.markdown(
    "Analyze customer reviews, ratings, recommendations, "
    "product performance, and customer pain points."
)


# -----------------------------
# KPI Metrics
# -----------------------------

total_reviews = len(filtered_df)

average_rating = filtered_df["Rating"].mean()

recommendation_rate = (
    filtered_df["Recommended IND"].mean() * 100
)

negative_rate = (
    (filtered_df["Rating"] < 3).mean() * 100
)


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Reviews",
        f"{total_reviews:,}"
    )


with col2:
    st.metric(
        "Average Rating",
        f"{average_rating:.2f} / 5"
    )


with col3:
    st.metric(
        "Recommendation Rate",
        f"{recommendation_rate:.2f}%"
    )


with col4:
    st.metric(
        "Negative Review Rate",
        f"{negative_rate:.2f}%"
    )


# -----------------------------
# Rating & Recommendation
# -----------------------------

st.divider()

st.header("Customer Review Overview")

col1, col2 = st.columns(2)


# -----------------------------
# Rating Distribution
# -----------------------------

with col1:

    st.subheader("Rating Distribution")

    rating_data = (
        filtered_df
        .groupby("Rating")
        .size()
        .reset_index(name="Review_Count")
    )

    fig_rating = px.bar(
        rating_data,
        x="Rating",
        y="Review_Count",
        text="Review_Count",
        title="Number of Reviews by Rating"
    )

    fig_rating.update_layout(
        xaxis_title="Rating",
        yaxis_title="Number of Reviews",
        showlegend=False
    )

    st.plotly_chart(
        fig_rating,
        use_container_width=True
    )


# -----------------------------
# Recommendation Distribution
# -----------------------------

with col2:

    st.subheader("Recommendation Distribution")

    recommendation_data = (
        filtered_df["Recommended IND"]
        .map({
            0: "Not Recommended",
            1: "Recommended"
        })
        .value_counts()
        .reset_index()
    )

    recommendation_data.columns = [
        "Recommendation",
        "Review_Count"
    ]

    fig_recommendation = px.bar(
        recommendation_data,
        x="Recommendation",
        y="Review_Count",
        text="Review_Count",
        title="Recommended vs Not Recommended"
    )

    fig_recommendation.update_layout(
        xaxis_title="Recommendation",
        yaxis_title="Number of Reviews",
        showlegend=False
    )

    st.plotly_chart(
        fig_recommendation,
        use_container_width=True
    )


# -----------------------------
# Department Performance
# -----------------------------

st.divider()

st.header("Department Performance")

department_data = (
    df[df["Department Name"] != "Unknown"]
    .groupby("Department Name")
    .agg(
        Review_Count=("Rating", "size"),
        Average_Rating=("Rating", "mean"),
        Recommendation_Rate=("Recommended IND", "mean")
    )
    .reset_index()
)

department_data["Average_Rating"] = (
    department_data["Average_Rating"].round(2)
)

department_data["Recommendation_Rate"] = (
    department_data["Recommendation_Rate"] * 100
).round(2)


col1, col2 = st.columns(2)


# Average Rating by Department
with col1:

    fig_department_rating = px.bar(
        department_data.sort_values(
            "Average_Rating",
            ascending=True
        ),
        x="Average_Rating",
        y="Department Name",
        orientation="h",
        text="Average_Rating",
        title="Average Rating by Department"
    )

    fig_department_rating.update_layout(
        xaxis_title="Average Rating",
        yaxis_title="",
        xaxis_range=[0, 5]
    )

    st.plotly_chart(
        fig_department_rating,
        use_container_width=True
    )


# Recommendation Rate by Department
with col2:

    fig_department_recommendation = px.bar(
        department_data.sort_values(
            "Recommendation_Rate",
            ascending=True
        ),
        x="Recommendation_Rate",
        y="Department Name",
        orientation="h",
        text="Recommendation_Rate",
        title="Recommendation Rate by Department"
    )

    fig_department_recommendation.update_layout(
        xaxis_title="Recommendation Rate (%)",
        yaxis_title="",
        xaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig_department_recommendation,
        use_container_width=True
    )


# -----------------------------
# Customer Pain Points
# -----------------------------

st.divider()

st.header("Customer Pain Points")

st.markdown(
    "Keyword-based analysis of common themes identified "
    "in negative customer reviews."
)


theme_data = pd.DataFrame({

    "Theme": [
        "Fit & Size",
        "Appearance & Style",
        "Fabric & Material",
        "Returns & Exchanges",
        "Quality & Durability",
        "Comfort"
    ],

    "Negative_Review_Count": [
        1459,
        1319,
        1226,
        506,
        371,
        288
    ],

    "Percentage_of_Negative_Reviews": [
        61.56,
        55.65,
        51.73,
        21.35,
        15.65,
        12.15
    ]
})


theme_data = theme_data.sort_values(
    "Percentage_of_Negative_Reviews",
    ascending=True
)


fig_themes = px.bar(
    theme_data,
    x="Percentage_of_Negative_Reviews",
    y="Theme",
    orientation="h",
    text="Percentage_of_Negative_Reviews",
    title="Common Themes in Negative Reviews"
)

fig_themes.update_layout(
    xaxis_title="Percentage of Negative Reviews (%)",
    yaxis_title="",
    xaxis_range=[0, 70]
)

st.plotly_chart(
    fig_themes,
    use_container_width=True
)


# -----------------------------
# Return-Related Analysis
# -----------------------------

st.divider()

st.header("Return-Related Customer Experience")


return_data = pd.DataFrame({

    "Review Type": [
        "No Return Mention",
        "Return Mention"
    ],

    "Review Count": [
        21633,
        1853
    ],

    "Average Rating": [
        4.28,
        3.23
    ],

    "Recommendation Rate": [
        84.83,
        51.92
    ]
})


col1, col2 = st.columns(2)


# Average Rating
with col1:

    fig_return_rating = px.bar(
        return_data,
        x="Review Type",
        y="Average Rating",
        text="Average Rating",
        title="Average Rating by Return Mention"
    )

    fig_return_rating.update_layout(
        yaxis_title="Average Rating",
        xaxis_title="",
        yaxis_range=[0, 5]
    )

    st.plotly_chart(
        fig_return_rating,
        use_container_width=True
    )


# Recommendation Rate
with col2:

    fig_return_recommendation = px.bar(
        return_data,
        x="Review Type",
        y="Recommendation Rate",
        text="Recommendation Rate",
        title="Recommendation Rate by Return Mention"
    )

    fig_return_recommendation.update_layout(
        yaxis_title="Recommendation Rate (%)",
        xaxis_title="",
        yaxis_range=[0, 100]
    )

    st.plotly_chart(
        fig_return_recommendation,
        use_container_width=True
    )


st.info(
    "Reviews containing return-related language had an average "
    "rating of 3.23 and a recommendation rate of 51.92%, "
    "compared with 4.28 and 84.83% for reviews without such mentions."
)


# -----------------------------
# Key Business Insights
# -----------------------------

st.divider()

st.header("💡 Key Business Insights")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Best Major Department",
        "Bottoms",
        "4.29 Avg Rating"
    )

    st.caption(
        "Bottoms has the strongest satisfaction among major "
        "departments, with an 85.13% recommendation rate."
    )


with col2:

    st.metric(
        "Largest Negative Volume",
        "Dresses",
        "689 Negative Reviews"
    )

    st.caption(
        "Dresses has the highest absolute number of negative "
        "reviews, making it an important area for improvement."
    )


with col3:

    st.metric(
        "Strongest Pain Point",
        "Fit & Size",
        "61.56% of Negative Reviews"
    )

    st.caption(
        "Fit and size-related issues appear most frequently "
        "among negative customer reviews."
    )


st.info(
    "💼 Business takeaway: Customer satisfaction is generally high, "
    "but fit and sizing, product appearance, fabric quality, and "
    "return-related experiences are important areas for improvement."
)