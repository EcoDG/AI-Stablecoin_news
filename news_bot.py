import os
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from html import unescape
import re
import time

# 환경 변수
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDzyAdb1L5cJSk4QjIUmJ0PqCrUEOIbfx4')
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

def translate_title(title, max_retries=3):
    """Gemini로 제목만 번역 (재시도 로직 포함)"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""다음 뉴스 제목을 한국어로 번역해주세요.
반드시 번역된 제목만 출력하고, 다른 설명이나 링크는 절대 추가하지 마세요.

제목: {title}

번역:"""
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    translated = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    # 불필요한 접두사 제거
                    translated = re.sub(r'^(번역:|제목:)\s*', '', translated, flags=re.IGNORECASE)
                    translated = re.sub(r'^["\'](.*)["\']$', r'\1', translated)
                    
                    # 번역이 제대로 되었는지 확인 (영문 그대로면 재시도)
                    if translated and translated != title:
                        return translated
                    else:
                        print(f"      ⚠️ 번역 결과가 원문과 동일, 재시도 중... ({attempt + 1}/{max_retries})")
                        time.sleep(2)
                        continue
            else:
                print(f"      ⚠️ API 오류 ({response.status_code}), 재시도 중... ({attempt + 1}/{max_retries})")
                time.sleep(2)
                continue
                
        except requests.exceptions.Timeout:
            print(f"      ⏱️ 타임아웃, 재시도 중... ({attempt + 1}/{max_retries})")
            time.sleep(2)
            continue
            
        except Exception as e:
            print(f"      ❌ 오류: {e}, 재시도 중... ({attempt + 1}/{max_retries})")
            time.sleep(2)
            continue
    
    # 모든 재시도 실패시 원문 반환
    print(f"      ⚠️ 번역 실패 (3회 시도), 원문 사용")
    return title

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
    
    # 제목 번역 (재시도 로직 포함)
    print(f"  Translating {len(selected)} titles (최대 3회 재시도)...")
    text = ""
    for i, article in enumerate(selected, 1):
        print(f"    [{i}/{len(selected)}] 번역 중...")
        
        # 제목만 번역 (재시도 로직 포함)
        translated_title = translate_title(article['title'])
        
        source = article['link'].split('/')[2].replace('www.', '')
        
        text += f"### {translated_title}\n"
        text += f"- **출처**: {source}\n"
        text += f"- **링크**: {article['link']}\n\n"
    
    return text

def collect_news():
    print("=" * 60)
    print("RSS News Bot with Korean Translation (재시도 로직)")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    ai_news = get_news("AI", RSS_FEEDS["AI"], 3)
    stablecoin_news = get_news("Stablecoin", RSS_FEEDS["Stablecoin"], 3)
    
    if not ai_news and not stablecoin_news:
        print("No news found")
        return None
    
    result = f"📰 **AI & 스테이블코인 뉴스레터**\n📅 {today}\n\n"
    
    if ai_news:
        result += "## 🤖 AI 뉴스\n\n" + ai_news + "\n"
    
    if stablecoin_news:
        result += "## 💰 스테이블코인 뉴스\n\n" + stablecoin_news + "\n"
    
    result += "---\n✅ 실제 RSS 피드에서 가져온 뉴스입니다."
    
    return result

def send_telegram(message):
    print("\nSending to Telegram...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 메시지가 길면 분할
    max_length = 4000
    
    if len(message) > max_length:
        parts = []
        current = ""
        
        for line in message.split('\n'):
            if len(current) + len(line) + 1 < max_length:
                current += line + '\n'
            else:
                parts.append(current)
                current = line + '\n'
        
        if current:
            parts.append(current)
        
        for i, part in enumerate(parts):
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": part,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print(f"  ✅ Part {i+1}/{len(parts)} sent")
                else:
                    print(f"  Failed part {i+1}: {response.text}")
            except Exception as e:
                print(f"  Error part {i+1}: {e}")
        
        return True
    else:
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
        print(news[:400] + "...")
        
        success = send_telegram(news)
        
        if success:
            print("\n🎉 Done!")
        else:
            print("\nFailed to send")
    else:
        print("\nNo news collected")

if __name__ == "__main__":
    main()
