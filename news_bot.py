import os
import requests
import json
from datetime import datetime

# 환경 변수에서 설정 가져오기
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDzyAdb1L5cJSk4QjIUmJ0PqCrUEOIbfx4')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8545984954:AAEZZTPRzn3JMzXedm94WzgY-e6NLiD5D7U')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '-1003040543146')

def search_news_with_gemini(topic, num_results=3):
    """Gemini를 사용하여 특정 주제의 뉴스 검색"""
    
    # 올바른 API 엔드포인트: v1beta + gemini-2.0-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""오늘은 {today}입니다.

"{topic}" 주제에 대한 최근 3일 이내의 최신 뉴스 {num_results}개를 찾아서 다음 형식으로 한글로 정리해주세요:

### [뉴스 제목 한글]
- **출처**: [뉴스 사이트명]
- **날짜**: [발행일]
- **요약**: [2-3문장으로 핵심 내용 요약]
- **링크**: [원문 URL]

주의사항:
- 신뢰할 수 있는 뉴스 소스만 사용하세요 (TechCrunch, The Verge, Bloomberg, CoinDesk, Wired 등)
- 실제로 존재하는 최신 뉴스만 포함하세요
- 한글 번역은 자연스럽게 해주세요
- 각 뉴스마다 반드시 원문 링크를 포함해주세요"""
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"⚠️ Gemini 응답에 내용이 없습니다: {result}")
                return None
        else:
            print(f"❌ Gemini API 오류 ({response.status_code}): {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Gemini API 요청 실패: {e}")
        return None

def get_latest_news():
    """AI와 스테이블코인 뉴스 수집"""
    
    print("🔍 Gemini로 최신 뉴스 검색 중...")
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
        return None
    
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # AI 뉴스 검색
    print("  → AI 뉴스 검색 중...")
    ai_news = search_news_with_gemini("AI 인공지능 (Artificial Intelligence)", 3)
    
    # 스테이블코인 뉴스 검색
    print("  → 스테이블코인 뉴스 검색 중...")
    stablecoin_news = search_news_with_gemini("스테이블코인 (Stablecoin)", 3)
    
    if not ai_news and not stablecoin_news:
        print("❌ 뉴스를 가져오지 못했습니다.")
        return None
    
    # 결과 조합
    result = f"""📰 **AI & 스테이블코인 뉴스레터**
📅 {today}

---

"""
    
    if ai_news:
        result += "## 🤖 AI 뉴스\n\n" + ai_news + "\n\n---\n\n"
    
    if stablecoin_news:
        result += "## 💰 스테이블코인 뉴스\n\n" + stablecoin_news + "\n\n---\n\n"
    
    result += f"📅 발행일: {today}"
    
    return result

def send_telegram_message(message):
    """텔레그램으로 메시지 발송"""
    
    print("📱 텔레그램 발송 중...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # 메시지가 너무 길면 분할 (텔레그램 제한: 4096자)
    max_length = 4000
    
    if len(message) > max_length:
        # 메시지를 여러 부분으로 나누기
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
        
        # 각 부분 전송
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
                    print(f"  ✅ 파트 {i+1}/{len(parts)} 발송 완료")
                    success_count += 1
                else:
                    print(f"  ⚠️ 파트 {i+1}/{len(parts)} 발송 실패: {response.text}")
            except Exception as e:
                print(f"  ❌ 파트 {i+1}/{len(parts)} 발송 오류: {e}")
        
        return success_count == len(parts)
    else:
        # 한 번에 전송
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("✅ 텔레그램 발송 성공!")
                return True
            else:
                print(f"⚠️ 텔레그램 발송 실패: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 텔레그램 발송 오류: {e}")
            return False

def main():
    """메인 실행 함수"""
    
    print("=" * 50)
    print("🚀 AI & 스테이블코인 뉴스봇 시작")
    print("=" * 50)
    
    # 1. 뉴스 수집 및 번역
    news_content = get_latest_news()
    
    if news_content:
        print("\n✅ 뉴스 수집 완료!")
        print("-" * 50)
        print(news_content[:500] + "..." if len(news_content) > 500 else news_content)
        print("-" * 50)
        
        # 2. 텔레그램 발송
        success = send_telegram_message(news_content)
        
        if success:
            print("\n🎉 모든 작업 완료!")
        else:
            print("\n⚠️ 일부 작업 실패")
    else:
        print("\n❌ 뉴스 수집 실패")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
