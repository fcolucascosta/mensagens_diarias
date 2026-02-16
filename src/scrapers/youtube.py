import feedparser
import re
import datetime


class YouTubeScraper:
    def __init__(self):
        self.base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="

    def get_latest_video(self, channel_id, title_pattern=None, check_today=True, max_results=10):
        """
        Fetches the latest videos from the RSS feed and searches for a match.

        Args:
            channel_id: YouTube channel ID.
            title_pattern: Regex pattern to match in the title (e.g., "homilia").
            check_today: If True, only returns videos published TODAY.
            max_results: Number of recent videos to check (default 10).

        Returns:
            dict with title, link, published, or None if not found.
        """
        url = f"{self.base_url}{channel_id}"
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"Nenhum vídeo encontrado no canal {channel_id}")
            return None

        # Get today's date (Brazil time)
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        br_tz = datetime.timezone(datetime.timedelta(hours=-3))
        today_br = utc_now.astimezone(br_tz).date()

        # Check up to max_results entries
        entries_to_check = feed.entries[:max_results]

        for entry in entries_to_check:
            title = entry.title
            link = entry.link
            published = entry.published

            # Check title pattern
            if title_pattern and not re.search(title_pattern, title, re.IGNORECASE):
                continue

            # Check if published today
            if check_today:
                try:
                    pub_date = datetime.datetime.strptime(
                        entry.published, "%Y-%m-%dT%H:%M:%S+00:00"
                    ).date()
                    if pub_date != today_br:
                        print(f"  ⏭️ '{title}' — publicado em {pub_date}, pulando (não é de hoje)")
                        continue
                except (ValueError, AttributeError):
                    # If we can't parse the date, accept the video anyway
                    pass

            print(f"✅ Vídeo encontrado: {title} ({link})")
            return {"title": title, "link": link, "published": published}

        # If we get here, no matching video was found
        if title_pattern:
            print(f"⚠️ Nenhum vídeo com '{title_pattern}' de hoje encontrado (verificou {len(entries_to_check)} vídeos)")
        return None
