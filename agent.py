import pandas as pd
from ddgs import DDGS
from time import sleep
from difflib import SequenceMatcher
from datetime import datetime
import os

def search_product(title, brand, model):
    query = f"{brand} {model} {title} amazon OR flipkart"
    best_link = None
    best_score = 0.0
    
    try:
        results = DDGS().text(query, max_results=10)
        for r in results:
            link = r.get('href', '')
            if 'amazon.in' in link or 'flipkart.com' in link:
                result_title = r.get('title', '')
                target_text = f"{brand} {model} {title}".lower()
                
                # Compute similarity score
                score = SequenceMatcher(None, target_text, result_title.lower()).ratio()
                
                if score > best_score:
                    best_score = score
                    best_link = link
                    
        return best_link, best_score
    except Exception as e:
        print(f"Error searching for {query}: {e}")
    return None, 0.0

def process_excel(input_file):
    print(f"Reading {input_file}...")
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error reading file {input_file}: {e}")
        return None
    
    links = []
    found_status = []
    similarity_scores = []
    
    for index, row in df.iterrows():
        title = str(row.get('GeM Title', ''))
        brand = str(row.get('GeM Brand', ''))
        model = str(row.get('GeM Model', ''))
        
        print(f"Searching: {brand} - {model} - {title[:30]}...")
        # A simple delay to avoid rate limiting
        sleep(2)
        
        link, score = search_product(title, brand, model)
        if link:
            links.append(link)
            similarity_scores.append(round(score, 2))
            
            # Use thresholds to determine review status
            if score >= 0.45:
                status = "Found, no need for human review"
            elif score >= 0.20:
                status = "Needs human review"
            else:
                status = "Item not found"
            
            found_status.append(status)
            print(f" Score: {score:.2f} | Status: {status} | Link: {link}")
        else:
            links.append("N/A")
            similarity_scores.append(0.0)
            found_status.append("Item not found")
            print(" Not found.")

    df['Amazon/Flipkart Link'] = links
    df['Similarity Score'] = similarity_scores
    df['Review Status'] = found_status
    
    # Create unique output file based on time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'search_results_{timestamp}.xlsx'
    
    try:
        df.to_excel(output_file, index=False)
        print(f"Saved results to {output_file}")
        return output_file
    except Exception as e:
        print(f"Failed to save results: {e}")
        return None

def main():
    print("=== Product Search Agent ===")
    input_file = input("Enter the path to your input Excel file (e.g., sample_products.xlsx) [Press Enter for default]: ").strip()
    
    if not input_file:
        input_file = 'sample_products.xlsx'
        
    if not os.path.exists(input_file):
        print(f"Error: Could not find the file '{input_file}'. Please check the path and try again.")
        return
        
    process_excel(input_file)

if __name__ == "__main__":
    main()
