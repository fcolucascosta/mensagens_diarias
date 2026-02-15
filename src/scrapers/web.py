import requests
from bs4 import BeautifulSoup

class WebScraper:
    def extract_text(self, url, selector=None):
        """
        Extracts the Gospel (Evangelho) from the Canção Nova liturgy page.
        
        Args:
            url (str): The URL to scrape.
            selector (str): Ignored for this tailored implementation.
            
        Returns:
            str: The extracted Gospel name and text.
        """
        try:
            # Fake user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Logic for Canção Nova Liturgy
            # The structure often has "Evangelho (Ref...)" as a text inside a paragraph or header
            # followed by the text.
            
            content_div = soup.select_one('#content') or soup.body
            
            # Find the header for Evangelho
            # Examples: "Evangelho (Mc 8,1-10)", "Evangelho"
            evangelho_header = content_div.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'p', 'strong'] and 'Evangelho' in tag.get_text())
            
            if not evangelho_header:
                print("Could not find 'Evangelho' header.")
                return None

            # Collect text after the header until the next major section or end
            extracted_text = [evangelho_header.get_text(strip=True)]
            
            for sibling in evangelho_header.next_siblings:
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'hr']:
                    # Stop if we hit another header or horizontal rule (likely next section)
                    break
                if sibling.name == 'p':
                    text = sibling.get_text(strip=True)
                    if text:
                        extracted_text.append(text)
                elif isinstance(sibling, str):
                   text = sibling.strip()
                   if text:
                       extracted_text.append(text)

            return "\n\n".join(extracted_text)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None
        except Exception as e:
            print(f"Error scraping text: {e}")
            return None
