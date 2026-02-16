import requests
from bs4 import BeautifulSoup
import re


class WebScraper:
    BASE_URL = "https://liturgia.cancaonova.com/pb/"

    def get_liturgy_url_for_date(self, day, month, year):
        """
        Finds the full URL for a specific date by parsing the calendar
        on the main Canção Nova liturgy page.
        
        Returns the full URL with slug, or None if not found.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.BASE_URL, headers=headers, params={
                'sMes': f'{month:02d}',
                'sAno': str(year)
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find calendar link matching the target day
            # Links look like: /pb/liturgia/{slug}/?sDia=17&sMes=02&sAno=2026
            target_param = f"sDia={day}"
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if target_param in href and '/liturgia/' in href:
                    # Ensure it's the right day (not just sDia=1 matching sDia=17)
                    if re.search(rf'sDia={day}(&|$)', href):
                        print(f"📅 URL encontrada para dia {day}: {href}")
                        return href

            print(f"⚠️ Não encontrou link para dia {day}/{month:02d}/{year}")
            return None

        except Exception as e:
            print(f"Erro ao buscar calendário: {e}")
            return None

    def extract_text(self, url, selector=None):
        """
        Extracts the Gospel (Evangelho) from the Canção Nova liturgy page.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            content_div = soup.select_one('#content') or soup.body

            # Find the Evangelho header
            evangelho_header = content_div.find(
                lambda tag: tag.name in ['h1', 'h2', 'h3', 'h4', 'p', 'strong']
                and 'Evangelho' in tag.get_text()
            )

            if not evangelho_header:
                print("Could not find 'Evangelho' header.")
                return None

            # Collect text after the header until the next section
            extracted_text = [evangelho_header.get_text(strip=True)]

            for sibling in evangelho_header.next_siblings:
                if sibling.name in ['h1', 'h2', 'h3', 'h4', 'hr']:
                    break
                if sibling.name == 'p':
                    text = sibling.get_text(strip=True)
                    if text:
                        extracted_text.append(text)
                elif isinstance(sibling, str):
                    text = sibling.strip()
                    if text:
                        extracted_text.append(text)

            raw_text = "\n\n".join(extracted_text)
            return self._format_evangelho(raw_text)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None
        except Exception as e:
            print(f"Error scraping text: {e}")
            return None

    def _format_evangelho(self, text):
        """
        Formats the Evangelho text:
        - Dashes touch the text (-Aleluia instead of - Aleluia)
        - No blank lines between Aleluia/Aclamação, Proclamação/Glória, Palavra/Glória
        - Spaces after verse numbers (14Os → 14 Os)
        """
        # Fix "- Text" → "-Text" (dash touching text)
        text = re.sub(r'^- ', '-', text, flags=re.MULTILINE)

        # Fix verse numbers: "14Os" → "14 Os" (number directly followed by capital letter)
        text = re.sub(r'(\d+)([A-ZÁÉÍÓÚÂÊÔÃÕÇ])', r'\1 \2', text)

        # Fix space before verse numbers: "pão.14" → "pão. 14"
        text = re.sub(r'([a-záéíóúâêôãõç.!?;:,"""\'])(\d+)', r'\1 \2', text)

        # Now handle blank lines between specific sections
        lines = text.split('\n')
        result = []
        i = 0
        while i < len(lines):
            line = lines[i]
            result.append(line)

            # Look ahead: if current line should be joined with next (no blank line)
            if i + 1 < len(lines):
                next_non_empty = None
                next_idx = i + 1
                while next_idx < len(lines) and lines[next_idx].strip() == '':
                    next_idx += 1
                if next_idx < len(lines):
                    next_non_empty = lines[next_idx].strip()

                current = line.strip()

                # Rules: remove blank line BETWEEN these pairs
                should_join = False

                # Aleluia → Aclamação (next line starts with -)
                if 'Aleluia' in current and next_non_empty and next_non_empty.startswith('-'):
                    should_join = True

                # Proclamação → Glória
                if 'Proclamação' in current and next_non_empty and 'Glória' in next_non_empty:
                    should_join = True

                # Palavra da Salvação → Glória
                if 'Palavra da Salvação' in current and next_non_empty and 'Glória' in next_non_empty:
                    should_join = True

                if should_join:
                    # Skip blank lines between these pairs
                    while i + 1 < len(lines) and lines[i + 1].strip() == '':
                        i += 1

            i += 1

        return '\n'.join(result)
