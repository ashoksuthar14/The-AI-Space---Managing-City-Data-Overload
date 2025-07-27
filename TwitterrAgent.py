import json
import google.generativeai as genai
from typing import Dict, List, Any
import os

class TweetAnalysisAgent:
    def __init__(self, api_key: str):
        """
        Initialize the Tweet Analysis Agent with Gemini API
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze_tweets(self, tweets: List[str]) -> Dict[str, Any]:
        """
        Analyze a list of tweets and return summary, sentiment, priority, and alert
        
        Args:
            tweets (List[str]): List of tweet texts
            
        Returns:
            Dict containing analysis results
        """
        if not tweets:
            return {
                "summary": "No tweets available for analysis",
                "sentiment": "neutral",
                "priority": "low",
                "alert": "No activity detected in this area"
            }
        
        # Combine all tweets into a single text
        combined_tweets = "\n".join([f"- {tweet}" for tweet in tweets])
        
        # Create a comprehensive prompt for analysis
        prompt = f"""
        Analyze the following tweets from a specific geographical area and provide:

        Tweets to analyze:
        {combined_tweets}

        Please provide your analysis in the following format:
        SUMMARY: [One line summary describing the overall situation]
        SENTIMENT: [positive/negative/neutral]
        PRIORITY: [high/moderate/low] (high if dangerous/emergency, moderate if concerning, low if normal)
        ALERT: [One line alert message for public notification]

        Guidelines:
        - Summary should capture the main theme/situation in one sentence
        - Sentiment should reflect the overall emotional tone
        - Priority should be HIGH for emergencies, dangers, or urgent situations
        - Alert should be actionable and informative for the public
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            print(f"Error analyzing tweets: {e}")
            return {
                "summary": "Error analyzing tweets",
                "sentiment": "neutral",
                "priority": "low",
                "alert": "Unable to analyze current situation"
            }
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the Gemini response and extract structured data
        
        Args:
            response_text (str): Raw response from Gemini
            
        Returns:
            Dict containing parsed analysis results
        """
        lines = response_text.strip().split('\n')
        result = {
            "summary": "",
            "sentiment": "neutral",
            "priority": "low",
            "alert": ""
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('SUMMARY:'):
                result["summary"] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('SENTIMENT:'):
                sentiment = line.replace('SENTIMENT:', '').strip().lower()
                if sentiment in ['positive', 'negative', 'neutral']:
                    result["sentiment"] = sentiment
            elif line.startswith('PRIORITY:'):
                priority = line.replace('PRIORITY:', '').strip().lower()
                if priority in ['high', 'moderate', 'low']:
                    result["priority"] = priority
            elif line.startswith('ALERT:'):
                result["alert"] = line.replace('ALERT:', '').strip()
        
        return result
    
    def process_areas(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process all areas in the input JSON and analyze their tweets
        
        Args:
            input_data (Dict): Input JSON data with areas and tweets
            
        Returns:
            Dict: Processed output with analysis results
        """
        output = {"twitter": {}}
        
        for area_name, area_data in input_data.items():
            if isinstance(area_data, dict) and "tweets" in area_data:
                print(f"Processing area: {area_name}")
                
                # Extract coordinates and tweets
                coordinates = area_data.get("coordinates", {})
                tweets = area_data.get("tweets", [])
                
                # Analyze tweets
                analysis = self.analyze_tweets(tweets)
                
                # Structure output
                output["twitter"][area_name] = {
                    "coordinates": coordinates,
                    "summary": analysis["summary"],
                    "sentimental_analysis": analysis["sentiment"],
                    "priority": analysis["priority"],
                    "alert": analysis["alert"]
                }
        
        return output
    
    def process_json_file(self, input_file_path: str, output_file_path: str):
        """
        Process a JSON file and save the results
        
        Args:
            input_file_path (str): Path to input JSON file
            output_file_path (str): Path to save output JSON file
        """
        try:
            # Read input JSON
            with open(input_file_path, 'r', encoding='utf-8') as file:
                input_data = json.load(file)
            
            # Process the data
            output_data = self.process_areas(input_data)
            
            # Save output JSON
            with open(output_file_path, 'w', encoding='utf-8') as file:
                json.dump(output_data, file, indent=2, ensure_ascii=False)
            
            print(f"Analysis complete! Output saved to {output_file_path}")
            return output_data
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file_path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in '{input_file_path}'.")
        except Exception as e:
            print(f"Error processing file: {e}")

def main():
    """
    Main function to run the tweet analysis agent
    """
    # Set your Gemini API key here
    API_KEY = ""  # Replace with your actual API key
    
    # Initialize the agent
    agent = TweetAnalysisAgent(API_KEY)
    
    # Example usage with file processing
    input_file = "enriched_area_tweets.json"
    output_file = "analyzed_tweets.json"
    
    # Process the JSON file
    result = agent.process_json_file(input_file, output_file)
    
    # Print results
    if result:
        print("\nAnalysis Results:")
        print(json.dumps(result, indent=2))



if __name__ == "__main__":
    main()
