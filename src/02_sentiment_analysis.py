"""
Sentiment Analysis Script
Analyzes sentiment using VADER and TextBlob
"""

import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import json
import re

def get_sentiment_scores(text):
    """Calculate sentiment scores using VADER and TextBlob"""
    vader = SentimentIntensityAnalyzer()
    
    # VADER sentiment
    vader_scores = vader.polarity_scores(text)
    
    # TextBlob sentiment
    blob = TextBlob(text)
    
    return {
        'vader_compound': vader_scores['compound'],
        'vader_pos': vader_scores['pos'],
        'vader_neg': vader_scores['neg'],
        'vader_neu': vader_scores['neu'],
        'textblob_polarity': blob.sentiment.polarity,
        'textblob_subjectivity': blob.sentiment.subjectivity
    }

def categorize_sentiment(score):
    """Categorize sentiment based on compound score"""
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def analyze_sentiment(input_file='data/reviews_clean.csv', output_file='data/reviews_with_sentiment.csv'):
    """
    Add sentiment analysis to cleaned reviews
    """
    
    print("📊 Loading cleaned data...")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} reviews")
    
    print("\n🔍 Calculating sentiment scores...")
    
    # Apply sentiment analysis
    df['sentiment_scores'] = df['Text'].apply(get_sentiment_scores)
    
    # Expand sentiment dict into columns
    sentiment_df = df['sentiment_scores'].apply(pd.Series)
    df = pd.concat([df, sentiment_df], axis=1)
    df = df.drop('sentiment_scores', axis=1)
    
    # Create sentiment categories
    df['sentiment_category'] = df['vader_compound'].apply(categorize_sentiment)
    
    print("   ✓ Sentiment scores calculated")
    
    # Generate insights
    print("\n📈 Sentiment Distribution:")
    sentiment_dist = df['sentiment_category'].value_counts()
    for category, count in sentiment_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {category}: {count:,} ({pct:.1f}%)")
    
    print("\n⭐ Average Rating by Sentiment:")
    avg_by_sentiment = df.groupby('sentiment_category')['Score'].mean()
    for category, avg in avg_by_sentiment.items():
        print(f"   {category}: {avg:.2f}/5")
    
    # Word frequency analysis for negative reviews
    print("\n🔴 Top words in negative reviews:")
    negative_reviews = df[df['sentiment_category'] == 'Negative']['Text']
    
    # Combine all negative reviews
    all_text = ' '.join(negative_reviews)
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'it', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{4,}\b', all_text)  # Only words 4+ chars
    words_filtered = [w for w in words if w not in stop_words]
    word_freq = Counter(words_filtered).most_common(20)
    
    for word, count in word_freq[:10]:
        print(f"   '{word}': {count} mentions")
    
    # Save stats to JSON
    stats = {
        'total_reviews': len(df),
        'sentiment_distribution': {
            category: {
                'count': int(count),
                'percentage': float((count / len(df)) * 100)
            }
            for category, count in sentiment_dist.items()
        },
        'average_rating': float(df['Score'].mean()),
        'top_negative_words': [
            {'word': word, 'count': count} 
            for word, count in word_freq[:20]
        ]
    }
    
    with open('outputs/sentiment_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    print("\n💾 Saved statistics to: outputs/sentiment_stats.json")
    
    # Save enhanced dataset
    df.to_csv(output_file, index=False)
    print(f"💾 Saved sentiment-enhanced data to: {output_file}")
    
    return df


if __name__ == "__main__":
    df_with_sentiment = analyze_sentiment(
        input_file='data/reviews_clean.csv',
        output_file='data/reviews_with_sentiment.csv'
    )
    
    print("\n" + "="*50)
    print("Next step: Run 03_ai_insights.py")
    print("="*50)