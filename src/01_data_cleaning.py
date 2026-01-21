"""
Data Cleaning Script
Takes raw review data and prepares it for analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path

def clean_reviews(input_file='data/reviews.csv', output_file='data/reviews_clean.csv', sample_size=5000):
    """
    Clean and prepare review dataset
    
    Args:
        input_file: Path to raw CSV file
        output_file: Path to save cleaned data
        sample_size: Number of reviews to sample (set to None for all data)
    """
    
    print("📂 Loading data...")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} reviews")
    
    # Take a sample if specified
    if sample_size and sample_size < len(df):
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"   Sampled {len(df_sample):,} reviews")
    else:
        df_sample = df
    
    print("\n🧹 Cleaning data...")
    
    # 1. Handle missing values
    initial_count = len(df_sample)
    df_clean = df_sample.dropna(subset=['Text', 'Score'])
    print(f"   Removed {initial_count - len(df_clean)} rows with missing text/score")
    
    # 2. Remove duplicates
    initial_count = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['Text'])
    print(f"   Removed {initial_count - len(df_clean)} duplicate reviews")
    
    # 3. Text preprocessing
    df_clean['Text'] = df_clean['Text'].str.lower()
    df_clean['Text'] = df_clean['Text'].str.strip()
    print(f"   Standardized text format")
    
    # 4. Filter out very short reviews (less signal)
    initial_count = len(df_clean)
    df_clean = df_clean[df_clean['Text'].str.len() > 20]
    print(f"   Removed {initial_count - len(df_clean)} reviews with <20 characters")
    
    # 5. Create time-based features if timestamp exists
    if 'Time' in df_clean.columns:
        df_clean['Date'] = pd.to_datetime(df_clean['Time'], unit='s')
        df_clean['Year'] = df_clean['Date'].dt.year
        df_clean['Month'] = df_clean['Date'].dt.month
        df_clean['YearMonth'] = df_clean['Date'].dt.to_period('M')
        print(f"   Created time-based features")
    
    # 6. Add review length feature
    df_clean['review_length'] = df_clean['Text'].str.len()
    df_clean['word_count'] = df_clean['Text'].str.split().str.len()
    
    print(f"\n✅ Cleaning complete!")
    print(f"   Final dataset: {len(df_clean):,} reviews")
    print(f"   Average review length: {df_clean['review_length'].mean():.0f} characters")
    print(f"   Rating distribution:\n{df_clean['Score'].value_counts().sort_index()}")
    
    # Save cleaned data
    df_clean.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    return df_clean


if __name__ == "__main__":
    # Run the cleaning process
    df_clean = clean_reviews(
        input_file='data/reviews.csv',
        output_file='data/reviews_clean.csv',
        sample_size=5000  # Change to None to process all reviews
    )
    
    print("\n" + "="*50)
    print("Next step: Run 02_sentiment_analysis.py")
    print("="*50)