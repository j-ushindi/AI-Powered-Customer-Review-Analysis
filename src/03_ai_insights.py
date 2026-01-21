"""
AI Insights Generation (keyword matching used for portfolio purposes only. OpenAI API will be used in production)
Uses rule-based topic extraction 
"""

import pandas as pd
from collections import Counter
import re
import json

def extract_topics_rule_based(df_negative):
    """
    Extract topics using keyword matching 
    """
    
    # Define topic keywords
    topic_keywords = {
        'Product Quality': ['quality', 'defective', 'broke', 'broken', 'damaged', 'poor', 'cheap', 'terrible', 'awful', 'bad'],
        'Shipping/Delivery': ['shipping', 'delivery', 'arrived', 'package', 'late', 'delayed', 'never received', 'lost', 'weeks'],
        'Customer Service': ['customer service', 'support', 'refund', 'return', 'response', 'contact', 'help', 'customer'],
        'Price/Value': ['price', 'expensive', 'overpriced', 'cost', 'value', 'money', 'worth', 'waste'],
        'Packaging': ['packaging', 'box', 'wrapped', 'container', 'sealed', 'package', 'crushed'],
        'Taste/Flavor': ['taste', 'flavor', 'bland', 'bitter', 'sweet', 'salty', 'disgusting', 'delicious', 'stale'],
    }
    
    # Count mentions for each topic
    topic_counts = {topic: 0 for topic in topic_keywords.keys()}
    
    for text in df_negative['Text']:
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topic_counts[topic] += 1
    
    # Calculate percentages
    total = len(df_negative)
    topic_percentages = {
        topic: (count / total * 100) 
        for topic, count in topic_counts.items() 
        if count > 0
    }
    
    # Sort by frequency
    sorted_topics = sorted(topic_percentages.items(), key=lambda x: x[1], reverse=True)
    
    # Format output
    output = []
    for i, (topic, pct) in enumerate(sorted_topics[:5], 1):
        sentiment_desc = "Predominantly negative mentions"
        output.append(f"TOPIC {i}: {topic}")
        output.append(f"Description: {sentiment_desc} related to {topic.lower()}")
        output.append(f"Sentiment: Negative")
        output.append(f"Prevalence: {pct:.1f}%")
        output.append("")
    
    return "\n".join(output)

def categorize_review_rule_based(review_text):
    """
    Categorize review using keyword matching
    """
    
    text_lower = review_text.lower()
    
    # Priority order matters - check most specific first
    if any(word in text_lower for word in ['shipping', 'delivery', 'arrived', 'package', 'late', 'delayed', 'never received']):
        return 'Shipping/Delivery'
    elif any(word in text_lower for word in ['customer service', 'support', 'refund', 'return', 'customer']):
        return 'Customer Service'
    elif any(word in text_lower for word in ['quality', 'defective', 'broke', 'broken', 'damaged', 'poor']):
        return 'Product Quality'
    elif any(word in text_lower for word in ['taste', 'flavor', 'bland', 'bitter', 'delicious', 'disgusting', 'stale']):
        return 'Taste/Flavor'
    elif any(word in text_lower for word in ['price', 'expensive', 'overpriced', 'cost', 'waste', 'money']):
        return 'Price/Value'
    elif any(word in text_lower for word in ['packaging', 'box', 'wrapped', 'crushed']):
        return 'Packaging'
    else:
        return 'Other'

def generate_executive_summary_template(df):
    """
    Create executive summary using data-driven templates
    """
    
    total_reviews = len(df)
    sentiment_dist = df['sentiment_category'].value_counts(normalize=True)
    avg_rating = df['Score'].mean()
    
    # Get top categories
    if 'ai_category' in df.columns:
        neg_df = df[df['sentiment_category'] == 'Negative']
        if len(neg_df) > 0:
            top_issues = neg_df['ai_category'].value_counts().head(3)
            
            # Build issues text
            issues_list = []
            for cat, count in top_issues.items():
                pct = (count / len(neg_df)) * 100
                issues_list.append(f"{cat} ({pct:.0f}% of negative reviews)")
            issues_text = ", ".join(issues_list)
        else:
            issues_text = "product quality, shipping, and customer service"
    else:
        issues_text = "product quality, shipping, and customer service"
    
    # Generate summary paragraphs
    pos_pct = sentiment_dist.get('Positive', 0) * 100
    neg_pct = sentiment_dist.get('Negative', 0) * 100
    neu_pct = sentiment_dist.get('Neutral', 0) * 100
    
    para1 = f"Analysis of {total_reviews:,} customer reviews reveals a rating average of {avg_rating:.2f} out of 5 stars, with {pos_pct:.0f}% expressing positive sentiment, {neg_pct:.0f}% negative, and {neu_pct:.0f}% neutral. This distribution suggests that while the majority of customers are satisfied, there is a significant segment experiencing issues that require attention."
    
    para2 = f"The primary concerns identified in negative feedback center around {issues_text}. These recurring themes represent the most critical areas for improvement and offer clear opportunities to enhance customer satisfaction. Addressing these specific pain points could potentially convert a substantial portion of dissatisfied customers into brand advocates."
    
    para3 = f"Moving forward, we recommend prioritizing improvements in the areas with highest negative mention rates. Implementing targeted solutions for these top issues could result in measurable improvements to both customer satisfaction scores and repeat purchase rates. Regular monitoring of review sentiment will help track the effectiveness of any corrective measures implemented."
    
    summary = f"{para1}\n\n{para2}\n\n{para3}"
    
    return summary

def run_ai_analysis_free(input_file='data/reviews_with_sentiment.csv', output_file='data/reviews_final.csv'):
    """
    Run rule-based analysis (no API costs)
    """
    
    print("🤖 Loading data for analysis...")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} reviews")
    
    # === TOPIC EXTRACTION ===
    print("\n📋 Extracting topics from negative reviews...")
    negative_df = df[df['sentiment_category'] == 'Negative']
    
    if len(negative_df) > 0:
        topics = extract_topics_rule_based(negative_df)
        
        print("\n" + "="*50)
        print("DISCOVERED TOPICS:")
        print("="*50)
        print(topics)
        
        # Save topics to file
        with open('outputs/topics_analysis.txt', 'w') as f:
            f.write(topics)
        print("\n💾 Saved to: outputs/topics_analysis.txt")
    else:
        print("   ⚠️  No negative reviews found")
    
    # === CATEGORIZATION ===
    print("\n🏷️  Categorizing reviews...")
    print(f"   Processing {len(df)} reviews...")
    
    df['ai_category'] = df['Text'].apply(categorize_review_rule_based)
    
    print("\n✅ Categorization complete!")
    print("\n   Category Distribution:")
    cat_dist = df['ai_category'].value_counts()
    for cat, count in cat_dist.items():
        pct = (count / len(df)) * 100
        print(f"   {cat}: {count:,} ({pct:.1f}%)")
    
    # === EXECUTIVE SUMMARY ===
    print("\n📝 Generating executive summary...")
    summary = generate_executive_summary_template(df)
    
    print("\n" + "="*50)
    print("EXECUTIVE SUMMARY:")
    print("="*50)
    print(summary)
    
    # Save summary
    with open('outputs/executive_summary.txt', 'w') as f:
        f.write(summary)
    print("\n💾 Saved to: outputs/executive_summary.txt")
    
    # Save final dataset
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved final dataset to: {output_file}")
    
    return df


if __name__ == "__main__":
    df_final = run_ai_analysis_free(
        input_file='data/reviews_with_sentiment.csv',
        output_file='data/reviews_final.csv'
    )
    
    print("\n" + "="*50)
    print("✅ Analysis complete! No API costs incurred.")
    print("Next step: Run the dashboard!")
    print("Command: streamlit run src/04_dashboard.py")
    print("="*50)