import json
import os
import google.generativeai as genai
from google.adk.tools import tool

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@tool
def analyze_traffic() -> list:
    """
    Analyze traffic data by matching Twitter alerts with news reports 
    and provide location-based traffic insights with coordinates.
    
    Returns:
        list: Traffic analysis results with verdicts and coordinates
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Load data files
    try:
        with open("data/bangalore_tweets.json", "r") as f:
            tweet_data = json.load(f)
        with open("data/bangalore_news.json", "r") as f:
            news_data = json.load(f)
    except FileNotFoundError as e:
        return [{"error": f"Data file not found: {str(e)}"}]
    except json.JSONDecodeError as e:
        return [{"error": f"Invalid JSON format: {str(e)}"}]
    
    twitter_areas = tweet_data.get("twitter", {})
    results = []
    
    for area_name, tweet_info in twitter_areas.items():
        if not tweet_info.get("summary"):
            continue
        
        summary = tweet_info.get("summary", "")
        sentiment = tweet_info.get("sentimental_analysis", "")
        priority = tweet_info.get("priority", "")
        coords = tweet_info.get("coordinates", [])
        
        # Find matching news for this area
        matching_news = []
        for news in news_data:
            news_text = f"{news.get('description', '')} {news.get('news', '')}".lower()
            if area_name.lower() in news_text:
                matching_news.append(news)
        
        # Generate verdict using Gemini
        if matching_news:
            news_info = matching_news[0]  # Use the first matching news
            prompt = f"""
Compare traffic tweet and news for Bangalore's {area_name}:

Tweet Information:
- Summary: {summary}
- Sentiment: {sentiment}
- Priority: {priority}

News Information:
- Description: {news_info.get("description", "")}
- News: {news_info.get("news", "")}
- Date: {news_info.get("date", "")}

Based on both sources, provide a final traffic verdict for {area_name}. 
Should this area be avoided? Provide a brief and clear recommendation.
"""
        else:
            prompt = f"""
Analyze traffic situation for Bangalore's {area_name} based on Twitter data:

Tweet Information:
- Summary: {summary}
- Sentiment: {sentiment}
- Priority: {priority}

Provide a traffic recommendation for this area. Be brief and clear.
"""
        
        try:
            response = model.generate_content(prompt)
            verdict = response.text.strip()
        except Exception as e:
            verdict = f"Unable to generate verdict: {str(e)}"
        
        results.append({
            "location": area_name,
            "coordinates": coords,
            "tweet_summary": summary,
            "sentiment": sentiment,
            "priority": priority,
            "news_matched": len(matching_news) > 0,
            "verdict": verdict
        })
    
    return results