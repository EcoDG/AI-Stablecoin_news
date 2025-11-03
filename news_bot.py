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
                    'title': title_text,
                    'link': link_text,
                    'pub_date': pub_date.text if pub_date is not None else '',
                    'description': desc_text[:150]
                }
                
                articles.append(article)
        
        # Atom 형식도 지원
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title')
            link = entry.find('{http://www.w3.org/2005/Atom}link')
            published = entry.find('{http://www.w3.org/2005/Atom}published')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            
            if title is not None and link is not None:
                title_text = unescape(title.text.strip()) if title.text else ''
                summary_text = unescape(summary.text.strip()) if summary is not None and summary.text else ''
                link_href = link.get('href', '') if link is not None else ''
                
                # 키워드 필터링
                if keywords:
                    combined_text = f"{title_text} {summary_text}"
                    if not contains_keywords(combined_text, keywords):
                        continue
                
                # HTML 태그 제거
                summary_text = re.sub('<[^<]+?>', '', summary_text)
                
                article = {
                    'title': title_text,
                    'link': link_href,
                    'pub_date': published.text if published is not None else '',
                    'description': summary_text[:150]
                }
                
                articles.append(article)
        
        return articles[:10]
        
    except Exception as e:
        print(f"  ⚠️ RSS 파싱 실패: {e}")
        return []

def get_news_from_rss(topic, config, num_articles=3):
    """RSS 피드에서 뉴스 가져오기 (키워드 필터링 적용)"""
    print(f"\n  📰 {topic} 뉴스 수집 중...")
    
    feed_urls = config["feeds"]
    keywords = config.get("keywords", None)
    
    if keywords:
        print(f"    🔍 키워드: {', '.join(keywords[:3])}...")
    
    all_articles = []
    
    for feed_url in feed_urls:
        source_name = feed_url.split('/')[2].replace('www.', '')
        print(f"    • {source_name} 확인 중...")
        
        xml_content = fetch_rss_feed(feed_url)
        
        if xml_content:
            articles = parse_rss_feed(xml_content, keywords=keywords)
            all_articles.extend(articles)
            print(f"      ✓ {len(articles)}개 발견")
    
    # 중복 제거 (같은 링크)
    seen_links = set()
    unique_articles = []
    for article in all_articles:
        if article['link'] and article['link'] not in seen_links:
            seen_links.add(article['link'])
            unique_articles.append(article)
    
    print(f"    ✅ 총 {len(unique_articles)}개 고유 뉴스")
    
    # 상위 N개 선택
    selected_articles = unique_articles[:num_articles]
    
    if not selected_articles:
        print(f"    ⚠️ 키워드와 일치하는 뉴스 없음")
        return None
    
    # 뉴스 포맷팅 (영문, 실제 링크만 사용)
    news_text = ""
    for i, article in enumerate(selected_articles, 1):
        source = article['link'].split('/')[2].replace('www.', '') if article['link'] else 'Unknown'
        
        news_text += f"""### {article['title']}
- **Source**: {source}
- **Link**: {article['link']}

"""
    
    return news_text

def get_latest_news():
    """RSS 피드에서 최신 뉴스 수집"""
    
    print("=" * 60)
    print("🚀 RSS News Collection Started")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # AI 뉴스
    ai_news = get_news_from_rss("AI", RSS_FEEDS["AI"], 3)
    
    # 스테이블코인 뉴스
    stablecoin_news = get_news_from_rss("Stablecoin", RSS_FEEDS["Stablecoin"], 3)
    
    if not ai_news and not stablecoin_news:
        print("\n❌ 뉴스를 가져오지 못했습니다.")
        return None
    
    # 결과 조합
    result = f"""📰 **AI & Stablecoin Newsletter**
📅 {today}

"""
    
    if ai_news:
        result += "---\n\n## 🤖 AI News\n\n" + ai_news
    
    if stablecoin_news:
        result += "---\n\n## 💰 Stablecoin News\n\n" + stablecoin_news
    
    result += "---\n\n"
    result += f"✅ All links are real articles from RSS feeds.\n"
    result += f"🔍 Filtered by keywords: AI & Stablecoin related topics."
    
    return result

def send_telegram_message(message):
    """텔레그램으로 메시지 발송"""
    
    print("\n📱 텔레그램 발송 중...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 메시지가 너무 길면 분할 (텔레그램 제한: 4096자)
    max_length = 4000
    
    if len(message) > max_length:
        parts = []
        current_part = ""
        
        for line in message.split('\n'):
            if len(current_part) + len(line) + 1 < max_length:
                current_part += line + '\n'
            else:
                parts.append(current_part)
                current_part = line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        success_count = 0
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
                    success_count += 1
                else:
                    print(f"  ⚠️ Part {i+1} failed: {response.text}")
            except Exception as e:
                print(f"  ❌ Part {i+1} error: {e}")
        
        return success_count == len(parts)
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
                print("  ✅ 발송 완료!")
                return True
            else:
                print(f"  ⚠️ 발송 실패: {response.text}")
                return False
        except Exception as e:
            print(f"  ❌ 발송 오류: {e}")
            return False

def main():
    """메인 실행 함수"""
    
    # 뉴스 수집
    news_content = get_latest_news()
    
    if news_content:
        print("\n" + "=" * 60)
        print("✅ 뉴스 수집 완료!")
        print("=" * 60)
        print("\n미리보기:")
        print(news_content[:400] + "...")
        print("=" * 60)
        
        # 텔레그램 발송
        success = send_telegram_message(news_content)
        
        if success:
            print("\n🎉 모든 작업 완료!")
        else:
            print("\n⚠️ 발송 실패")
    else:
        print("\n❌ 뉴스 수집 실패")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
