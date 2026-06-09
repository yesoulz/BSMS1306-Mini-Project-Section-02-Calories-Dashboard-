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
caldf.dropna(subset=['Calories per 100 grams', 'Kilojoules per 100 grams'], inplace=True)

# Save the CLEANED data (not the original df)
caldf.to_csv("cleaned_calories.csv", index=False)

# Dashboard
df_clean = pd.read_csv("cleaned_calories.csv")

# Image for the dashboard
st.image('dietary.jpeg')

# =========================
# Sidebar Navigation
# =========================

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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Number of Foods", len(df_clean))

    with col2:
        avg_calories = round(df_clean['Calories per 100 grams'].mean(), 2)
        st.metric("Average Calories", f"{avg_calories} cal")

    with col3:
        st.metric("Categories", df_clean['FoodCategory'].nunique())

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

# =========================
# PAGE 2: OBJECTIVE 1
# =========================

elif page == "Objective 1":

    st.subheader("Objective 1: Identify High-Calorie Foods")
    st.markdown("*This allows users to avoid calorie-dense options when dieting*")

    top_high = df_clean.nlargest(10, 'Calories per 100 grams')

    fig = px.bar(
        top_high,
        x='FoodItem',
        y='Calories per 100 grams',
        color='Calories per 100 grams',
        color_continuous_scale='Reds',
        title="⚠️ HIGHEST CALORIE FOODS (per 100g)"
    )

    st.plotly_chart(fig)

# =========================
# PAGE 3: OBJECTIVE 2
# =========================

elif page == "Objective 2":

    st.subheader("Objective 2: Compare Calories Across Food Categories")
    st.markdown("*Helps users identify which food groups are typically higher or lower in calories*")

    category_comparison = df_clean.groupby('FoodCategory')['Calories per 100 grams'].mean().sort_values().reset_index()

    fig = px.bar(
        category_comparison,
        x='Calories per 100 grams',
        y='FoodCategory',
        orientation='h',
        color='Calories per 100 grams',
        color_continuous_scale='RdYlGn_r',
        title="Average Calories by Food Category"
    )

    st.plotly_chart(fig)

    lowest_cat = category_comparison.iloc[0]['FoodCategory']
    highest_cat = category_comparison.iloc[-1]['FoodCategory']

    st.info(f"Insight: {lowest_cat} has the lowest average calories, while {highest_cat} has the highest.")

# =========================
# PAGE 4: OBJECTIVE 3
# =========================

elif page == "Objective 3":

    st.subheader("Objective 3: Find Foods Within Your Calorie Budget")
    st.markdown("*Interactive filters help users discover suitable foods for their diet*")

    calorie_budget = st.slider(
        "Your Daily Calorie Budget (per 100g serving)",
        0, 800, 200,
        help="Find foods under this calorie limit"
    )

    budget_foods = df_clean[df_clean['Calories per 100 grams'] <= calorie_budget]

    col1, col2, col3 = st.columns(3)

    col1.metric("Foods within budget", len(budget_foods))
    col2.metric("% of all foods", f"{len(budget_foods)/len(df_clean)*100:.1f}%")

    if len(budget_foods) > 0:
        best_food = budget_foods.nsmallest(1, 'Calories per 100 grams')['FoodItem'].values[0]
    else:
        best_food = "No matching foods"

    col3.metric("Best low-cal option", best_food)

    st.dataframe(budget_foods[['FoodCategory', 'FoodItem', 'Calories per 100 grams']])