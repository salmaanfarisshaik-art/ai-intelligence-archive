import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from scripts.lib.api_client import api_client
from scripts.lib.logger import setup_logger

logger = setup_logger("rss_fetcher")

RSS_FEEDS = [
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml"},
    {"name": "BAIR Blog", "url": "https://bair.berkeley.edu/blog/feed.xml"}
]

def fetch_rss_feeds() -> List[Dict[Any, Any]]:
    """Fetches latest AI news from configured RSS feeds."""
    entries = []
    
    for feed in RSS_FEEDS:
        response = api_client.get("rss", feed["url"], ttl_seconds=14400)
        raw_text = response.get("raw_text", "")
        if not raw_text:
            continue
            
        try:
            root = ET.fromstring(raw_text)
            
            # Basic RSS 2.0 parsing
            channel = root.find("channel")
            if channel is not None:
                for item in channel.findall("item"):
                    entries.append({
                        "title": item.find("title").text if item.find("title") is not None else "",
                        "link": item.find("link").text if item.find("link") is not None else "",
                        "published": item.find("pubDate").text if item.find("pubDate") is not None else "",
                        "description": item.find("description").text if item.find("description") is not None else "",
                        "source_feed_name": feed["name"]
                    })
                    
            # Basic Atom parsing
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            if root.tag.endswith("feed"):
                for entry in root.findall("atom:entry", ns):
                    link_elem = entry.find("atom:link", ns)
                    link = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    entries.append({
                        "title": entry.find("atom:title", ns).text if entry.find("atom:title", ns) is not None else "",
                        "link": link,
                        "published": entry.find("atom:published", ns).text if entry.find("atom:published", ns) is not None else "",
                        "description": entry.find("atom:summary", ns).text if entry.find("atom:summary", ns) is not None else "",
                        "source_feed_name": feed["name"]
                    })
        except Exception as e:
            logger.error(f"Failed to parse RSS XML for {feed['name']}: {e}")
            
    return entries
