# Libraries
import pandas as pd
import streamlit as st
import plotly.express as px

# Data Cleaning
# Import CSV and drop redundant column
df = pd.read_csv("calories.csv")
df = df.drop(columns=['per100grams'])
df.drop_duplicates(inplace=True)

# Create cleaned dataframe
caldf = df.copy()

# Remove 'cal' and 'kJ' text, convert to numbers
caldf['Cals_per100grams'] = pd.to_numeric(
    caldf['Cals_per100grams'].astype(str).str.replace('cal', '', regex=False),
    errors='coerce'
)

caldf['KJ_per100grams'] = pd.to_numeric(
    caldf['KJ_per100grams'].astype(str).str.replace('kJ', '', regex=False),
    errors='coerce'
)

# Rename columns for readability
caldf.rename(columns={
    'Cals_per100grams': 'Calories per 100 grams',
    'KJ_per100grams': 'Kilojoules per 100 grams'
}, inplace=True)

# Remove any rows with NaN values (failed conversions)
caldf.dropna(
    subset=['Calories per 100 grams', 'Kilojoules per 100 grams'],
    inplace=True
)

# Save the CLEANED data (not the original df)
caldf.to_csv("cleaned_calories.csv", index=False)

# Dashboard
# Load the cleaned data for dashboard
df_clean = pd.read_csv("cleaned_calories.csv")

# Image for the dashboard
st.image('dietary.jpeg')

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Go to",
    ["Overview", "Objective 1", "Objective 2", "Objective 3"]
)

# Dashboard title shown on ALL pages
st.title("BSMS1306 Mini Project: Calories Dashboard")
st.subheader(
    "Prepared by: Adam Iman bin Mohd Abas (2519507) & "
    "Muhammad Thaqif Solihin bin Mohd Nawawi (2515501)"
)

# =========================
# PAGE 1: OVERVIEW
# =========================

if page == "Overview":

    # Metrics row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Number of Foods", len(df_clean))

    with col2:
        avg_calories = round(df_clean['Calories per 100 grams'].mean(), 2)
        st.metric("Average Calories", f"{avg_calories} cal")

    with col3:
        st.metric("Categories", df_clean['FoodCategory'].nunique())

    # =====================================
    # SCATTER PLOT (For the overview page)
    # =====================================

    selected_categories = st.multiselect(
        "Select Categories",
        sorted(df_clean['FoodCategory'].unique())
    )

    if selected_categories:

        category_df = df_clean[
            df_clean['FoodCategory'].isin(selected_categories)
        ]

        selected_foods = st.multiselect(
            "Select Food Items",
            sorted(category_df['FoodItem'].unique()),
            default=sorted(category_df['FoodItem'].unique())[:10]
        )

        if selected_foods:

            food_df = category_df[
                category_df['FoodItem'].isin(selected_foods)
            ]

            fig = px.scatter(
                food_df,
                x='FoodItem',
                y='Calories per 100 grams',
                color='FoodCategory',
                hover_data=['FoodItem']
            )

            fig.update_layout(
                xaxis_tickangle=-45
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(
                food_df[['FoodCategory', 'FoodItem', 'Calories per 100 grams']]
            )