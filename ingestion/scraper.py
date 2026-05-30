# ============================================================
# ingestion/scraper.py
# Scrapes Naruto 
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import requests
import mwparserfromhell
import os 
import re
import time
from tqdm import tqdm
from config import RAW_DATA_DIR


# Media API endpoint for Naruto Fandom wiki
FANDOM_API_URL = "https://naruto.fandom.com/api.php"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}



def clean_text(text,title=None):
    """
    Helper function to clean the text
    """
    # Remove thumb image descriptions
    text = re.sub(r'thumb\|.*?\n', '\n', text)
    
    # Remove language links e.g. "es:Primer Raikage"
    text = re.sub(r'\n[a-z]{2,3}:[^\n]+', '', text)
    
    # Remove References section and everything after
    text = re.sub(r'\s*References\s*.*', '', text, flags=re.DOTALL)
    
    # Remove extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

    


def get_all_character_pages():  
    """
    Scrapes all character pages from the Naruto Fandom wiki.
    Returns a list of dictionaries containing page IDs and titles.
    """
    pages = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": "Category:Characters",
        "cmlimit": 500,
        "format": "json"
    }

    while True:  

        # Make request to Fandom API
        
        response = requests.get(FANDOM_API_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Error fetching pages: {response.status_code}")
            break


        data = response.json()
        items = data["query"]["categorymembers"]

        if not items:
            break

        for item in items:
            pages.append({"pages_id": item["pageid"], "title": item["title"]})

        if "continue" not in data:
            break

        params["cmcontinue"] = data["continue"]["cmcontinue"]
        time.sleep(0.3)

    return pages


def get_page_content(title):
    """
    Fetches the content of a page given its title.
    Returns the page content as a string.
    """

    try:
        params = {
            "action": "query",
            "prop": "revisions",
            "rvprop": "content", # Return the actual content
            "rvslots": "main", # Use the main content slot
            "titles": title, # Page to fetch
            "format": "json"
        }

        response = requests.get(FANDOM_API_URL, headers=HEADERS, params=params)

    

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            return None
        

        data = response.json()
        items = data["query"]["pages"]  
        page_content = list(items.values())[0]


        # Check if the page has content
        if "revisions" not in page_content:
            return None
        
        raw_text = page_content["revisions"][0]["slots"]["main"]["*"]
        parsed_text = mwparserfromhell.parse(raw_text) # Remove all the wiki markups
        cleaned_text = parsed_text.strip_code() 
        fully_cleaned_text = clean_text(cleaned_text, title=title)

        return fully_cleaned_text

    except Exception as e:
        print(f"Error fetching page '{title}': {e}")
        return None 


def save_content(title, text):
    """
    Save the cleaned text content to a text file named after the character's title in the data/raw folder.
    Return the filepath of the saved file.
    """
    clean_title = title.replace("/", "-").replace(" ", "_") # Replaces slashes and space for a safe filename
    url_title = title.replace(" ", "_") # For constructing the wiki URL
    
    wiki_url = f"https://naruto.fandom.com/wiki/{url_title}" 

    
    filepath = os.path.join(RAW_DATA_DIR, clean_title + ".txt")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Title: {title}\n")
        f.write(f"URL: {wiki_url}\n")
        f.write("-----------------------\n\n")
        f.write(text)
    
    return filepath


def run_scraper():
    """
    Main function to run the scraper.
    """
    pages = get_all_character_pages()

    saved = 0
    failed = 0

    for page in tqdm(pages, "Fetching Characters"):
        content = get_page_content(page["title"])

        if content is not None:
            save_content(page["title"], content)
            saved += 1
        else:
            failed += 1
            continue

    print(saved)
    print(failed)



if __name__ == "__main__":
    run_scraper()



