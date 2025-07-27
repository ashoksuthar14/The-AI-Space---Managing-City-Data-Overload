import json
from gnews import GNews
from datetime import datetime
import re

def get_traffic_news():
    """Get traffic-related news from Bangalore"""
    news = GNews(language='en', country='India')
    
    # Search for traffic-related news
    traffic_results = news.get_news('Bangalore traffic')
    
    news_data = []
    for article in traffic_results:
        news_item = {
            "publisher": article.get('publisher', {}).get('title', 'Unknown'),
            "date": article.get('published date', 'Unknown'),
            "title": article.get('title', ''),
            "about_the_article": article.get('description', 'No description available'),
            "url": article.get('url', ''),
            "source": "Traffic News"
        }
        news_data.append(news_item)
    
    return news_data

def get_event_news():
    """Get event-related news that might cause traffic and crowds in Bangalore"""
    news = GNews(language='en', country='India')
    
    # Search terms for events that typically cause traffic and crowds
    event_search_terms = [
        'Bangalore events traffic',
        'Bangalore festival crowd',
        'Bangalore concert traffic',
        'Bangalore protest march',
        'Bangalore rally crowd',
        'Bangalore exhibition traffic'
    ]
    
    events_data = []
    
    for search_term in event_search_terms:
        try:
            results = news.get_news(search_term)
            
            for article in results[:3]:  # Limit to 3 articles per search term
                # Extract event information from title and description
                title = article.get('title', '')
                description = article.get('description', '')
                
                # Try to determine event type from title/description
                event_type = determine_event_type(title + " " + description)
                
                # Try to extract crowd size information
                crowd_info = extract_crowd_info(title + " " + description)
                
                event_item = {
                    "name_of_event": extract_event_name(title),
                    "type": event_type,
                    "news_covered": {
                        "title": title,
                        "description": description,
                        "publisher": article.get('publisher', {}).get('title', 'Unknown'),
                        "date": article.get('published date', 'Unknown'),
                        "url": article.get('url', '')
                    },
                    "crowd_size": crowd_info,
                    "traffic_impact": "Potential traffic disruption expected",
                    "location": extract_location(title + " " + description),
                    "search_category": search_term
                }
                events_data.append(event_item)
                
        except Exception as e:
            print(f"Error fetching news for {search_term}: {e}")
            continue
    
    # Remove duplicates based on event name
    unique_events = []
    seen_titles = set()
    for event in events_data:
        if event['name_of_event'] not in seen_titles:
            unique_events.append(event)
            seen_titles.add(event['name_of_event'])
    
    return unique_events

def determine_event_type(text):
    """Determine event type from text content"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['concert', 'music', 'performance', 'show']):
        return 'Entertainment/Concert'
    elif any(word in text_lower for word in ['festival', 'celebration', 'cultural']):
        return 'Festival/Cultural Event'
    elif any(word in text_lower for word in ['protest', 'rally', 'march', 'demonstration']):
        return 'Political/Social Movement'
    elif any(word in text_lower for word in ['exhibition', 'expo', 'fair', 'trade show']):
        return 'Exhibition/Trade Show'
    elif any(word in text_lower for word in ['sports', 'match', 'game', 'tournament']):
        return 'Sports Event'
    elif any(word in text_lower for word in ['conference', 'summit', 'meeting']):
        return 'Conference/Business Event'
    else:
        return 'General Event'

def extract_crowd_info(text):
    """Extract crowd size information from text"""
    # Look for numbers followed by crowd-related words
    crowd_patterns = [
        r'(\d+(?:,\d+)*)\s*(?:people|persons|attendees|participants)',
        r'(\d+(?:,\d+)*)\s*(?:thousand|lakh|crore)',
        r'crowd of (\d+(?:,\d+)*)',
        r'(\d+(?:,\d+)*)\s*expected'
    ]
    
    for pattern in crowd_patterns:
        match = re.search(pattern, text.lower())
        if match:
            return f"Approximately {match.group(1)} people expected"
    
    # Look for qualitative crowd descriptions
    if any(word in text.lower() for word in ['massive crowd', 'huge crowd', 'large gathering']):
        return "Large crowd expected"
    elif any(word in text.lower() for word in ['crowd', 'gathering', 'attendees']):
        return "Crowd size not specified"
    
    return "No crowd information available"

def extract_event_name(title):
    """Extract event name from title"""
    # Remove common prefixes and clean up the title
    cleaned_title = re.sub(r'^(Bangalore|Bengaluru):\s*', '', title, flags=re.IGNORECASE)
    cleaned_title = re.sub(r'\s*-\s*.*$', '', cleaned_title)  # Remove everything after dash
    return cleaned_title.strip()

def extract_location(text):
    """Extract location information from text"""
    bangalore_areas = [
        'MG Road', 'Brigade Road', 'Commercial Street', 'Koramangala', 'Indiranagar',
        'Whitefield', 'Electronic City', 'Marathahalli', 'BTM Layout', 'Jayanagar',
        'Malleshwaram', 'Rajajinagar', 'Vijayanagar', 'Banashankari', 'JP Nagar',
        'HSR Layout', 'Sarjapur', 'Hebbal', 'Yeshwantpur', 'Majestic'
    ]
    
    text_lower = text.lower()
    for area in bangalore_areas:
        if area.lower() in text_lower:
            return area
    
    return "Bangalore (Location not specified)"

def save_to_json(news_data, events_data, filename='bangalore_news_events.json'):
    """Save all data to JSON file"""
    output_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "news": news_data,
        "events": events_data,
        "summary": {
            "total_news_articles": len(news_data),
            "total_events": len(events_data),
            "data_source": "GNews API"
        }
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")
        print(f"Total news articles: {len(news_data)}")
        print(f"Total events: {len(events_data)}")
    except Exception as e:
        print(f"Error saving to JSON: {e}")

def main():
    """Main function to run the scraper"""
    print("Fetching Bangalore traffic news...")
    news_data = get_traffic_news()
    
    print("Fetching Bangalore events that might cause traffic...")
    events_data = get_event_news()
    
    print("Saving data to JSON file...")
    save_to_json(news_data, events_data)
    
    # Print sample data
    print("\n--- Sample News Data ---")
    if news_data:
        print(f"Sample: {news_data[0]['title']}")
    
    print("\n--- Sample Events Data ---")
    if events_data:
        print(f"Sample: {events_data[0]['name_of_event']} - {events_data[0]['type']}")

if __name__ == "__main__":
    main()
