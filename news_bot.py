import os
import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from html import unescape
import re

# 환경 변수에서 설정 가져오기
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8545984954:AAEZZTPRzn3JMzXedm94WzgY-e6NLiD5D7U')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1003040543146')

# RSS 피드 URL 및 키워드 설정
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
                    "busd", "stable coin", "fiat-backed", "algorithmic stablecoin"]
    }
}

def fetch_rss_feed(url):
    """RSS 피드 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"  ⚠️ RSS 피드 가져오기 실패 ({url.split('/')[2]}): {e}")
        return None

def contains_keywords(text, keywords):
    """텍스트에 키워드가 포함되어 있는지 확인 (대소문자 무시)"""
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def parse_rss_feed(xml_content, keywords=None):
    """RSS 피드 파싱하여 최근 뉴스 추출 (키워드 필터링 포함)"""
    try:
        root = ET.fromstring(xml_content)
        articles = []
        
        # RSS 2.0 형식
        for item in root.findall('.//item'):
            title = item.find('title')
            link = item.find('link')
            pub_date = item.find('pubDate')
            description = item.find('description')
            
            if title is not None and link is not None:
                title_text = unescape(title.text.strip()) if title.text else ''
                desc_text = unescape(description.text.strip()) if description is not None and description.text else ''
                link_text = link.text.strip() if link.text else ''
                
                # 키워드 필터링
                if keywords:
                    combined_text = f"{title_text} {desc_text}"
                    if not contains_keywords(combined_text, keywords):
                        continue
                
                # HTML 태그 제거
                desc_text = re.sub('<[^<]+?>', '', desc_text)
                
                article = {
                    'tit
