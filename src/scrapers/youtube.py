import feedparser
import re

class YouTubeScraper:
    def __init__(self):
        self.base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="

    def get_latest_video(self, channel_id, title_pattern=None):
        """
        Fetches the latest video from the RSS feed of the channel.
        If title_pattern is provided, it verifies if the title matches.
        """
        url = f"{self.base_url}{channel_id}"
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"No entries found for channel {channel_id}")
            return None

        # Get the latest entry
        entry = feed.entries[0]
        title = entry.title
        link = entry.link
        published = entry.published

        print(f"Found video: {title} ({link})")

        if title_pattern:
            if re.search(title_pattern, title, re.IGNORECASE):
                print(f"Video matches pattern '{title_pattern}'")
                return {"title": title, "link": link, "published": published}
            else:
                print(f"Video title '{title}' does not match pattern '{title_pattern}'")
                return None
        
        return {"title": title, "link": link, "published": published}
