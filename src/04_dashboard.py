"""
Interactive Dashboard
Streamlit app for visualizing customer insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Customer Insights Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load the final processed dataset"""
    try:
        df = pd.read_csv('data/reviews_final.csv')
        # Convert date column if it exists
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Please run the analysis scripts first.")
        st.stop()

df = load_data()

# === HEADER ===
st.title("🔍 AI-Enhanced Customer Insights Dashboard")
st.markdown("**Combining traditional analytics with AI-powered topic extraction**")
st.markdown("---")

# === SIDEBAR FILTERS ===
st.sidebar.header("📊 Filters")

# Sentiment filter
sentiment_options = df['sentiment_category'].unique().tolist()
sentiment_filter = st.sidebar.multiselect(
    "Sentiment",
    options=sentiment_options,
    default=sentiment_options
)

# Rating filter
rating_filter = st.sidebar.slider(
    "Star Rating",
    min_value=int(df['Score'].min()),
    max_value=int(df['Score'].max()),
    value=(int(df['Score'].min()), int(df['Score'].max()))
)

# Date filter (if available)
if 'Date' in df.columns:
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(df['Date'].min(), df['Date'].max()),
        min_value=df['Date'].min(),
        max_value=df['Date'].max()
    )

# Apply filters
df_filtered = df[
    (df['sentiment_category'].isin(sentiment_filter)) &
    (df['Score'] >= rating_filter[0]) &
    (df['Score'] <= rating_filter[1])
]

if 'Date' in df.columns and len(date_range) == 2:
    df_filtered = df_filtered[
        (df_filtered['Date'] >= pd.to_datetime(date_range[0])) &
        (df_filtered['Date'] <= pd.to_datetime(date_range[1]))
    ]

# === KEY METRICS ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Reviews",
        f"{len(df_filtered):,}",
        delta=f"{len(df_filtered) - len(df):,} from total"
    )

with col2:
    avg_rating = df_filtered['Score'].mean()
    st.metric(
        "Average Rating",
        f"{avg_rating:.2f}/5",
        delta=f"{avg_rating - df['Score'].mean():.2f}"
    )

with col3:
    positive_pct = (df_filtered['sentiment_category'] == 'Positive').sum() / len(df_filtered) * 100
    st.metric(
        "Positive Sentiment",
        f"{positive_pct:.1f}%"
    )

with col4:
    negative_pct = (df_filtered['sentiment_category'] == 'Negative').sum() / len(df_filtered) * 100
    st.metric(
        "Negative Sentiment",
        f"{negative_pct:.1f}%",
        delta_color="inverse"
    )

st.markdown("---")

# === MAIN VISUALIZATIONS ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sentiment Distribution")
    sentiment_counts = df_filtered['sentiment_category'].value_counts()
    
    fig1 = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        color=sentiment_counts.index,
        color_discrete_map={
            'Positive': '#00CC66',
            'Negative': '#FF6B6B',
            'Neutral': '#FFD93D'
        },
        hole=0.4
    )
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("⭐ Rating Distribution")
    rating_counts = df_filtered['Score'].value_counts().sort_index()
    
    fig2 = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Star Rating', 'y': 'Number of Reviews'},
        color=rating_counts.values,
        color_continuous_scale='Blues'
    )
    fig2.update_layout(showlegend=False, xaxis_title="Star Rating", yaxis_title="Count")
    st.plotly_chart(fig2, use_container_width=True)

# === AI INSIGHTS SECTION ===
st.markdown("---")
st.header("🤖 AI-Powered Insights")

col1, col2 = st.columns([2, 1])

with col1:
    if 'ai_category' in df_filtered.columns and df_filtered['ai_category'].notna().any():
        st.subheader("Top Customer Topics")
        
        category_counts = df_filtered['ai_category'].value_counts().head(6)
        
        fig3 = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            labels={'x': 'Number of Mentions', 'y': 'Topic Category'},
            color=category_counts.values,
            color_continuous_scale='Viridis'
        )
        fig3.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("ℹ️ AI categorization not available for filtered data")

with col2:
    st.subheader("Quick Stats")
    
    if 'word_count' in df_filtered.columns:
        avg_words = df_filtered['word_count'].mean()
        st.metric("Avg Words/Review", f"{avg_words:.0f}")
    
    if 'vader_compound' in df_filtered.columns:
        avg_sentiment = df_filtered['vader_compound'].mean()
        st.metric("Avg Sentiment Score", f"{avg_sentiment:.2f}")
    
    most_common_rating = df_filtered['Score'].mode()[0]
    st.metric("Most Common Rating", f"{most_common_rating}/5")

# === EXECUTIVE SUMMARY ===
st.markdown("---")
st.subheader("📝 AI-Generated Executive Summary")

try:
    with open('outputs/executive_summary.txt', 'r') as f:
        summary = f.read()
    st.info(summary)
except FileNotFoundError:
    st.warning("⚠️ Executive summary not yet generated. Run 03_ai_insights.py first.")

# === TREND OVER TIME ===
if 'Date' in df_filtered.columns:
    st.markdown("---")
    st.subheader("📈 Sentiment Trend Over Time")
    
    # Group by month and sentiment
    df_time = df_filtered.groupby([
        df_filtered['Date'].dt.to_period('M'),
        'sentiment_category'
    ]).size().reset_index(name='count')
    
    df_time['Date'] = df_time['Date'].dt.to_timestamp()
    
    fig4 = px.line(
        df_time,
        x='Date',
        y='count',
        color='sentiment_category',
        labels={'count': 'Number of Reviews', 'Date': 'Month'},
        color_discrete_map={
            'Positive': '#00CC66',
            'Negative': '#FF6B6B',
            'Neutral': '#FFD93D'
        }
    )
    fig4.update_layout(hovermode='x unified', height=400)
    st.plotly_chart(fig4, use_container_width=True)

# === SAMPLE REVIEWS ===
st.markdown("---")
st.subheader("📄 Sample Reviews")

# Add a selectbox for filtering sample reviews
review_type = st.selectbox(
    "Show reviews:",
    ["All", "Positive Only", "Negative Only", "Neutral Only"]
)

if review_type != "All":
    sentiment_map = {
        "Positive Only": "Positive",
        "Negative Only": "Negative",
        "Neutral Only": "Neutral"
    }
    sample_df = df_filtered[df_filtered['sentiment_category'] == sentiment_map[review_type]]
else:
    sample_df = df_filtered

# Show random sample
num_samples = min(5, len(sample_df))
if num_samples > 0:
    sample_reviews = sample_df.sample(n=num_samples)
    
    for idx, row in sample_reviews.iterrows():
        sentiment_color = {
            'Positive': '🟢',
            'Negative': '🔴',
            'Neutral': '🟡'
        }
        
        col1, col2 = st.columns([1, 6])
        with col1:
            st.markdown(f"### {sentiment_color[row['sentiment_category']]}")
            st.markdown(f"**{row['Score']}/5**")
        
        with col2:
            st.markdown(f"**{row['sentiment_category']}** Review")
            review_text = row['Text']
            if len(review_text) > 300:
                st.markdown(f"_{review_text[:300]}..._")
            else:
                st.markdown(f"_{review_text}_")
            
            if 'ai_category' in row and pd.notna(row['ai_category']):
                st.caption(f"Category: {row['ai_category']}")
        
        st.markdown("---")
else:
    st.info("No reviews match the current filters")
st.markdown("---")
st.caption("Built with ❤️ using Python, OpenAI, and Streamlit | Data source: Customer Reviews Dataset")