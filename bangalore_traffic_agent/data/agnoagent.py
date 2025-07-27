import json
import os
from typing import Dict, List, Any, Tuple
from agno.agent import Agent
from agno.models.google import Gemini

class BangaloreDataAnalyzer:
    def __init__(self, gemini_api_key: str = None):
        """
        Initialize the Bangalore Data Analyzer with Gemini AI agent
        
        Args:
            gemini_api_key: Your Gemini API key (optional if set as environment variable)
        """
        if gemini_api_key:
            os.environ["GOOGLE_API_KEY"] = gemini_api_key
            
        # Initialize the Agno agent with Gemini model
        self.agent = Agent(
            model=Gemini(id="gemini-2.5-flash"),
            markdown=True,
        )
    
    def load_json_file(self, file_path: str) -> Dict:
        """Load JSON data from file with detailed error reporting"""
        try:
            print(f"📂 Attempting to load: {file_path}")
            if not os.path.exists(file_path):
                print(f"❌ File does not exist: {file_path}")
                return {}
                
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"✅ Successfully loaded {file_path}")
                print(f"   📊 File size: {os.path.getsize(file_path)} bytes")
                
                if isinstance(data, dict):
                    print(f"   🔑 Data keys: {list(data.keys())}")
                    # Show structure details
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"      - {key}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"      - {key}: {len(value)} locations")
                        else:
                            print(f"      - {key}: {type(value).__name__}")
                else:
                    print(f"   ⚠️  Data is not a dictionary: {type(data).__name__}")
                return data
        except FileNotFoundError:
            print(f"❌ Error: File {file_path} not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON format in {file_path}: {e}")
            return {}
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return {}
    
    def extract_traffic_data(self, data: Dict) -> Dict[str, Dict]:
        """
        Extract traffic data from Twitter format:
        {"twitter": {"Location": {"coordinates": {...}, "summary": ..., "sentimental_analysis": ...}}}
        """
        places_data = {}
        print("🚗 Extracting traffic data from Twitter format...")
        
        if not data:
            print("   ❌ No data found")
            return places_data
        
        # Handle your Twitter traffic data structure
        if 'twitter' in data:
            twitter_data = data['twitter']
            print(f"   📍 Found Twitter data with {len(twitter_data)} locations")
            
            for place_name, place_info in twitter_data.items():
                if not isinstance(place_info, dict):
                    continue
                
                place_key = place_name.lower().strip()
                coordinates = place_info.get('coordinates', {})
                
                places_data[place_key] = {
                    'type': 'traffic',
                    'place_name': place_name,
                    'coordinates': {
                        'lat': coordinates.get('latitude', 0),
                        'lng': coordinates.get('longitude', 0),
                        'source': 'twitter_data'
                    },
                    'summary': place_info.get('summary', ''),
                    'sentiment': place_info.get('sentimental_analysis', 'neutral'),
                    'priority': place_info.get('priority', 'unknown'),
                    'alert': place_info.get('alert', ''),
                    'raw_data': place_info
                }
                print(f"      ✅ {place_name}: {coordinates.get('latitude', 'N/A')}, {coordinates.get('longitude', 'N/A')}")
        
        print(f"   📊 Extracted traffic data for {len(places_data)} places")
        return places_data
    
    def extract_news_data(self, data: Dict) -> Dict[str, Dict]:
        """
        Extract news data from your format:
        {"news": [{"publisher": ..., "title": ..., "about_the_article": ..., "source": ...}]}
        """
        places_data = {}
        print("📰 Extracting news data...")
        
        if not data:
            print("   ❌ No data found")
            return places_data
        
        if 'news' in data:
            news_articles = data['news']
            print(f"   📄 Found {len(news_articles)} news articles")
            
            # Extract location names from titles and articles
            for i, article in enumerate(news_articles):
                if not isinstance(article, dict):
                    continue
                
                # Extract locations from title and content
                title = article.get('title', '').lower()
                about = article.get('about_the_article', '').lower()
                source = article.get('source', '')
                
                # Look for Bangalore location names in the text
                detected_locations = self.extract_locations_from_text(title + ' ' + about)
                
                # If no specific location found, categorize as general Bangalore news
                if not detected_locations:
                    detected_locations = ['bangalore_general']
                
                for location in detected_locations:
                    location_key = location.lower().strip()
                    
                    if location_key not in places_data:
                        places_data[location_key] = {
                            'type': 'news',
                            'place_name': location.title(),
                            'articles': [],
                            'article_count': 0,
                            'sentiment_scores': [],
                            'sources': set()
                        }
                    
                    # Analyze sentiment of this article
                    article_sentiment = self.analyze_article_sentiment(title + ' ' + about)
                    
                    places_data[location_key]['articles'].append({
                        'title': article.get('title', ''),
                        'about': article.get('about_the_article', ''),
                        'publisher': article.get('publisher', ''),
                        'date': article.get('date', ''),
                        'url': article.get('url', ''),
                        'source': source,
                        'sentiment': article_sentiment,
                        'article_index': i
                    })
                    
                    places_data[location_key]['article_count'] += 1
                    places_data[location_key]['sentiment_scores'].append(article_sentiment)
                    places_data[location_key]['sources'].add(article.get('publisher', 'Unknown'))
            
            # Calculate overall sentiment for each location
            for location_key, location_data in places_data.items():
                sentiments = location_data['sentiment_scores']
                if sentiments:
                    positive_count = sentiments.count('positive')
                    negative_count = sentiments.count('negative')
                    neutral_count = sentiments.count('neutral')
                    
                    if positive_count > negative_count and positive_count > neutral_count:
                        overall_sentiment = 'positive'
                    elif negative_count > positive_count and negative_count > neutral_count:
                        overall_sentiment = 'negative'
                    else:
                        overall_sentiment = 'neutral'
                    
                    location_data['overall_sentiment'] = overall_sentiment
                    location_data['sentiment_breakdown'] = {
                        'positive': positive_count,
                        'negative': negative_count,
                        'neutral': neutral_count
                    }
                
                # Convert sources set to list for JSON serialization
                location_data['sources'] = list(location_data['sources'])
        
        print(f"   📊 Extracted news data for {len(places_data)} locations")
        return places_data
    
    def extract_locations_from_text(self, text: str) -> List[str]:
        """Extract Bangalore location names from text"""
        # Common Bangalore locations
        bangalore_locations = [
            'koramangala', 'whitefield', 'electronic city', 'marathahalli', 'btm layout',
            'indiranagar', 'mg road', 'brigade road', 'jayanagar', 'rajajinagar',
            'banashankari', 'jp nagar', 'hebbal', 'yeshwantpur', 'malleshwaram',
            'silk board', 'hosur road', 'sarjapur road', 'outer ring road', 'airport road',
            'ulsoor', 'frazer town', 'commercial street', 'cubbon park', 'lalbagh',
            'vijayanagar', 'basavanagudi', 'gandhinagar', 'chickpet', 'majestic',
            'kr puram', 'hsr layout', 'bellandur', 'sarjapur', 'bommanahalli',
            'yelahanka', 'rt nagar', 'sadashivanagar', 'dollar colony', 'lavelle road'
        ]
        
        found_locations = []
        text_lower = text.lower()
        
        for location in bangalore_locations:
            if location in text_lower:
                found_locations.append(location)
        
        # Also check for "bengaluru" or "bangalore" for general city news
        if 'bengaluru' in text_lower or 'bangalore' in text_lower:
            if not found_locations:  # Only add if no specific location found
                found_locations.append('bangalore_general')
        
        return found_locations
    
    def analyze_article_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keywords"""
        text_lower = text.lower()
        
        positive_keywords = [
            'improve', 'better', 'good', 'excellent', 'success', 'growth', 'development',
            'new', 'opens', 'launch', 'expansion', 'upgrade', 'enhanced', 'modern',
            'efficient', 'fast', 'convenient', 'boost', 'progress', 'achievement'
        ]
        
        negative_keywords = [
            'traffic', 'congestion', 'delay', 'problem', 'issue', 'accident', 'jam',
            'slow', 'blocked', 'closure', 'disruption', 'complaint', 'pollution',
            'protest', 'strike', 'breakdown', 'poor', 'bad', 'worst', 'crisis'
        ]
        
        positive_score = sum(1 for word in positive_keywords if word in text_lower)
        negative_score = sum(1 for word in negative_keywords if word in text_lower)
        
        if positive_score > negative_score:
            return 'positive'
        elif negative_score > positive_score:
            return 'negative'
        else:
            return 'neutral'
    
    def analyze_combined_data_with_ai(self, traffic_data: Dict, news_data: Dict, place: str) -> Dict:
        """
        Use Gemini AI to analyze combined sentiment for a place with structured output
        """
        prompt = f"""
        Analyze the comprehensive data for {place.title()} in Bangalore and provide structured insights.

        TRAFFIC DATA (from Twitter):
        {json.dumps(traffic_data, indent=2) if traffic_data else "No traffic data available"}

        NEWS DATA (from News Articles):
        {json.dumps(news_data, indent=2) if news_data else "No news data available"}

        Please provide a structured analysis in the following format:

        ## LOCATION OVERVIEW
        - **Place**: {place.title()}
        - **Coordinates**: [If available from traffic data]
        - **Overall Assessment**: [One sentence summary]

        ## SENTIMENT ANALYSIS
        - **Overall Sentiment**: [Positive/Negative/Neutral]
        - **Sentiment Score**: [1-10 scale]
        - **Traffic Sentiment**: [Based on Twitter data]
        - **News Sentiment**: [Based on news articles]

        ## KEY INSIGHTS
        - **Traffic Situation**: [Summary of traffic conditions]
        - **News Highlights**: [Key news points]
        - **Priority Level**: [High/Medium/Low concern]

        ## RECOMMENDATIONS
        - **For Commuters**: [Practical advice]
        - **For Residents**: [Living considerations]
        - **Best Times to Travel**: [If applicable]

        ## RISK ASSESSMENT
        - **Traffic Risk**: [Low/Medium/High]
        - **Overall Livability**: [Rating and reasoning]
        """
        
        try:
            response = self.agent.run(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            return {
                'ai_comprehensive_analysis': content,
                'analysis_timestamp': 'generated',
                'data_sources_used': {
                    'has_traffic_data': bool(traffic_data),
                    'has_news_data': bool(news_data)
                }
            }
        except Exception as e:
            return {
                'ai_comprehensive_analysis': f"Error analyzing data: {str(e)}",
                'error': True
            }
    
    def compare_and_analyze(self, traffic_file: str, news_file: str, output_file: str = None) -> Dict:
        """
        Main method to compare traffic and news data and generate final analysis
        """
        print("="*70)
        print("🚀 BANGALORE DATA ANALYSIS - CUSTOM FORMAT")
        print("="*70)
        
        print("\n📁 Loading data files...")
        traffic_data = self.load_json_file(traffic_file)
        news_data = self.load_json_file(news_file)
        
        if not traffic_data and not news_data:
            print("❌ Error: No valid data found in either file")
            return {}
        
        print("\n🔍 Extracting and processing data...")
        traffic_places = self.extract_traffic_data(traffic_data)
        news_places = self.extract_news_data(news_data)
        
        # Get all unique places from both datasets
        all_places = set(traffic_places.keys()) | set(news_places.keys())
        
        if not all_places:
            print("❌ No places found in the data!")
            return {}
        
        final_analysis = {
            "analysis_metadata": {
                "timestamp": "generated",
                "total_places_analyzed": len(all_places),
                "data_sources": {
                    "traffic_file": traffic_file,
                    "news_file": news_file,
                    "traffic_locations_found": len(traffic_places),
                    "news_locations_found": len(news_places)
                }
            },
            "places_analysis": {},
            "summary_statistics": {
                "total_news_articles": len(news_data.get('news', [])) if news_data else 0,
                "total_traffic_locations": len(traffic_places),
                "analysis_coverage": f"{len(all_places)} unique locations analyzed"
            }
        }
        
        print(f"\n🏙️ Analyzing {len(all_places)} places...")
        places_list = sorted(list(all_places))
        print(f"📍 Locations: {', '.join([p.title() for p in places_list])}")
        
        for i, place in enumerate(places_list, 1):
            print(f"\n📊 [{i}/{len(all_places)}] Analyzing {place.title()}...")
            
            traffic_info = traffic_places.get(place, {})
            news_info = news_places.get(place, {})
            
            # Use AI to analyze combined data
            print(f"   🤖 Running AI analysis...")
            ai_analysis = self.analyze_combined_data_with_ai(traffic_info, news_info, place)
            
            # Compile comprehensive analysis
            analysis_result = {
                "place_name": place.title(),
                "coordinates": traffic_info.get('coordinates', {'lat': 'N/A', 'lng': 'N/A'}),
                "data_availability": {
                    "has_traffic_data": bool(traffic_info),
                    "has_news_data": bool(news_info),
                    "traffic_source": "Twitter Data" if traffic_info else "None",
                    "news_articles_count": news_info.get('article_count', 0)
                },
                "traffic_analysis": {
                    "summary": traffic_info.get('summary', 'No traffic data available'),
                    "sentiment": traffic_info.get('sentiment', 'unknown'),
                    "priority": traffic_info.get('priority', 'unknown'),
                    "alert": traffic_info.get('alert', 'No alerts')
                } if traffic_info else {"status": "No traffic data available"},
                "news_analysis": {
                    "article_count": news_info.get('article_count', 0),
                    "overall_sentiment": news_info.get('overall_sentiment', 'unknown'),
                    "sentiment_breakdown": news_info.get('sentiment_breakdown', {}),
                    "sources": news_info.get('sources', []),
                    "recent_articles": news_info.get('articles', [])[:3]  # Show first 3 articles
                } if news_info else {"status": "No news data available"},
                "ai_comprehensive_analysis": ai_analysis,
                "raw_data": {
                    "traffic": traffic_info,
                    "news": news_info
                }
            }
            
            final_analysis["places_analysis"][place] = analysis_result
            print(f"   ✅ Completed analysis for {place.title()}")
        
        # Generate overall city analysis
        print(f"\n🌆 Generating overall Bangalore analysis...")
        overall_prompt = f"""
        Based on comprehensive analysis of {len(all_places)} locations in Bangalore, provide an executive summary.
        
        DATA SUMMARY:
        - Total locations analyzed: {len(all_places)}
        - Traffic data sources: Twitter monitoring
        - News articles analyzed: {final_analysis['summary_statistics']['total_news_articles']}
        
        LOCATIONS COVERED: {', '.join([p.title() for p in places_list])}
        
        Please provide:
        1. **CITY OVERVIEW**: Overall state of Bangalore based on this data
        2. **TRAFFIC INSIGHTS**: Key patterns from Twitter traffic data  
        3. **NEWS TRENDS**: Major themes from news coverage
        4. **TOP CONCERNS**: Most problematic areas
        5. **POSITIVE DEVELOPMENTS**: Areas showing improvement
        6. **RECOMMENDATIONS**: For city planning and commuters
        7. **FUTURE OUTLOOK**: Based on current trends
        """
        
        try:
            overall_analysis = self.agent.run(overall_prompt)
            final_analysis["overall_city_analysis"] = overall_analysis.content if hasattr(overall_analysis, 'content') else str(overall_analysis)
        except Exception as e:
            final_analysis["overall_city_analysis"] = f"Error generating overall analysis: {str(e)}"
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(final_analysis, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Analysis saved to {output_file}")
            except Exception as e:
                print(f"❌ Error saving to file: {str(e)}")
        
        return final_analysis

def main():
    """
    Main execution function for Bangalore Data Analyzer
    """
    print("🚀 Initializing Bangalore Data Analyzer (Custom Format)...")
    
    # Initialize the analyzer
    analyzer = BangaloreDataAnalyzer()
    
    # Define file paths (adjust these to match your actual file names)
    traffic_file = "bangalore_traffic.json"  # Your Twitter traffic data
    news_file = "bangalore_news.json"       # Your news data
    output_file = "bangalore_analyzes.json"
    
    # Run the analysis
    try:
        results = analyzer.compare_and_analyze(traffic_file, news_file, output_file)
        
        if results and results.get('places_analysis'):
            # Print comprehensive summary
            print("\n" + "="*70)
            print("✅ ANALYSIS COMPLETED SUCCESSFULLY!")
            print("="*70)
            
            metadata = results.get('analysis_metadata', {})
            stats = results.get('summary_statistics', {})
            
            print(f"📊 **ANALYSIS SUMMARY**")
            print(f"   📍 Total places analyzed: {metadata.get('total_places_analyzed', 0)}")
            print(f"   🚗 Traffic locations: {metadata.get('data_sources', {}).get('traffic_locations_found', 0)}")
            print(f"   📰 News articles processed: {stats.get('total_news_articles', 0)}")
            print(f"   💾 Results saved to: {output_file}")
            
            # Display detailed summary for each place
            places_analysis = results.get('places_analysis', {})
            print(f"\n📍 **DETAILED LOCATION ANALYSIS**:")
            print("-" * 50)
            
            for place_name, analysis in places_analysis.items():
                coords = analysis.get('coordinates', {})
                data_avail = analysis['data_availability']
                traffic_analysis = analysis['traffic_analysis']
                news_analysis = analysis['news_analysis']
                
                print(f"\n🏢 **{place_name.upper()}**")
                print(f"   📍 Coordinates: {coords.get('lat', 'N/A')}, {coords.get('lng', 'N/A')}")
                print(f"   🚗 Traffic Status: {'✅' if data_avail['has_traffic_data'] else '❌'}")
                if data_avail['has_traffic_data']:
                    print(f"      - Sentiment: {traffic_analysis.get('sentiment', 'N/A')}")
                    print(f"      - Priority: {traffic_analysis.get('priority', 'N/A')}")
                print(f"   📰 News Coverage: {'✅' if data_avail['has_news_data'] else '❌'}")
                if data_avail['has_news_data']:
                    print(f"      - Articles: {news_analysis.get('article_count', 0)}")
                    print(f"      - Sentiment: {news_analysis.get('overall_sentiment', 'N/A')}")
                    print(f"      - Sources: {', '.join(news_analysis.get('sources', [])[:2])}")
                
            print(f"\n🔍 **Check {output_file} for complete AI analysis and recommendations!**")
            
        else:
            print("\n❌ No analysis results generated. Check your data files format!")
    
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()