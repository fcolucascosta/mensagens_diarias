import sys
import os
sys.path.append(os.getcwd())
from src.scrapers.web import WebScraper

scraper = WebScraper()
text = scraper.extract_text("https://liturgia.cancaonova.com/pb/")
print("--- Extracted Text ---")
print(text)
print("----------------------")
