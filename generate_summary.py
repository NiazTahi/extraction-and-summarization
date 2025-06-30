import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY=os.environ.get("GOOGLE_API_KEY")

def load_json_data():
    """Load the extracted data from output.json"""
    try:
        with open('output2.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: output.json not found. Please run extractor.py first.")
        return None

def generate_ai_summary(data):
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        return None
    
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Based on this Form ADT-1 data, write a 3-5 line summary in the exact format shown in this example:
        
        Example: "XYZ Pvt Ltd has appointed M/s Rao & Associates as its statutory auditor for FY 2023–24, effective from 1 July 2023. The appointment has been disclosed via Form ADT-1, with all supporting documents submitted."
        
        Data: {json.dumps(data, indent=2)}
        
        Write a similar summary using the actual company name, auditor name, and dates from the data.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def main():
    # Load the data
    data = load_json_data()
    if not data:
        return
    
    print("Generating AI-style summary...")
    
    # Try Google's Generative AI first, fall back to template
    summary = generate_ai_summary(data)
    
    # Save the summary
    if summary:
        with open('summary.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("Generated Summary:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        print("\nSummary saved to summary.txt")
    else:
        print("Failed to generate summary. Please check your Google API key.")

if __name__ == "__main__":
    main() 