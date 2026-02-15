import requests
import re

def get_channel_id(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        
        # Look for "channelId":"UC..." or <meta itemprop="channelId" content="UC...">
        # Check for externalId which is often the channel ID in JSON configs embedded in the page
        match = re.search(r'"channelId":"(UC[\w-]+)"', res.text)
        if match:
            return match.group(1)
            
        match = re.search(r'"externalId":"(UC[\w-]+)"', res.text)
        if match:
            return match.group(1)
            
        match = re.search(r'<meta itemprop="channelId" content="(UC[\w-]+)">', res.text)
        if match:
            return match.group(1)
            
        return "Not Found"
    except Exception as e:
        return f"Error: {e}"

print("Padre Mario:", get_channel_id("https://www.youtube.com/@PadreMarioSartori"))
print("Padre Paulo:", get_channel_id("https://www.youtube.com/@padrepauloricardo"))
