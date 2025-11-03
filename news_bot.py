import os
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from html import unescape
import re

# 환경 변수
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8545984954:AAEZZTPRzn3JMzXedm94WzgY-e6NLiD5D7U')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1003040543146')

# RSS 피드 설정
RSS_FEEDS = {
    "AI": {
        "feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
        ],
        "keywords": ["ai", "artificial intelligence", "machine learning", "deep learning", 
                    "neural network", "llm", "gpt", "gemini", "claude", "chatgpt", 
                    "openai", "anthropic", "google ai", "generative"]
    },
    "Stablecoin": {
        "feeds": [
            "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "https://cointelegraph.com/rss",
        ],
        "keywords": ["stablecoin", "usdt", "usdc", "tether", "circle", "dai", 
                    "busd", "stable coin", "fiat-backed", "algorithmic"]
    }
}

def fetch_rss(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Error fetching {url.split('/')[2]}: {e}")
        return None

def has_keyword(text, keywords):
    text = text.lower()
    return any(kw.lower() in text for kw in keywords)

def parse_rss(xml_content, keywords=None):
    try:
        root = ET.fromstring(xml_content)
        articles = []
        
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            
            if title_elem is not None and link_elem is not None:
                title = unescape(title_elem.text or '').strip()
                link = (link_elem.text or '').strip()
                
                if keywords and not has_keyword(title, keywords):
                    continue
                
                if title and link:
                    articles.append({'title': title, 'link': link})
        
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
            link_elem = entry.find('{http://www.w3.org/2005/Atom}link')
            
            if title_elem is not None and link_elem is not None:
                title = unescape(title_elem.text or '').strip()
                link = link_elem.get('href', '')
                
                if keywords and not has_keyword(title, keywords):
                    continue
                
                if title and link:
                    articles.append({'title': title, 'link': link})
        
        return articles[:10]
    except Exception as e:
        print(f"Parse error: {e}")
        return []

def get_news(topic, config, count=3):
    print(f"\n{topic} news collection...")
    
    all_articles = []
    keywords = config.get("keywords", None)
    
    for feed_url in config["feeds"]:
        source = feed_url.split('/')[2].replace('www.', '')
        print(f"  - Fetching {source}")
        
        xml = fetch_rss(feed_url)
        if xml:
            articles = parse_rss(xml, keywords)
            all_articles.extend(articles)
            print(f"    Found: {len(articles)}")
    
    seen = set()
    unique = []
    for article in all_articles:
        if article['link'] not in seen:
            seen.add(article['link'])
            unique.append(article)
    
    print(f"  Total unique: {len(unique)}")
    
    selected = unique[:count]
    
    if not selected:
        return None
    
    text = ""
    for article in selected:
        source = article['link'].split('/')[2].replace('www.', '')
        text += f"### {article['title']}\n"
        text += f"- **Source**: {source}\n"
        text += f"- **Link**: {article['link']}\n\n"
    
    return text

def collect_news():
    print("=" * 60)
    print("RSS News Bot Started")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    ai_news = get_news("AI", RSS_FEEDS["AI"], 3)
    stablecoin_news = get_news("Stablecoin", RSS_FEEDS["Stablecoin"], 3)
    
    if not ai_news and not stablecoin_news:
        print("No news found")
        return None
    
    result = f"**AI & Stablecoin Newsletter**\n{today}\n\n"
    
    if ai_news:
        result += "## 🤖 AI News\n\n" + ai_news + "\n"
    
    if stablecoin_news:
        result += "## 💰 Stablecoin News\n\n" + stablecoin_news + "\n"
    
    result += "---\n✅ Real RSS feeds only"
    
    return result

def send_telegram(message):
    print("\nSending to Telegram...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("✅ Sent!")
            return True
        else:
            print(f"Failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    news = collect_news()
    
    if news:
        print("\n" + "=" * 60)
        print("Collection complete!")
        print("=" * 60)
        print("\nPreview:")
        print(news[:300] + "...")
        
        success = send_telegram(news)
        
        if success:
            print("\n🎉 Done!")
        else:
            print("\nFailed to send")
    else:
        print("\nNo news collected")

if __name__ == "__main__":
    main()
