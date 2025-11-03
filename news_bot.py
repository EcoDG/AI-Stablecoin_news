import os
import requests
import json
from datetime import datetime
import anthropic

# 환경 변수에서 설정 가져오기
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')  # GitHub Secrets에서 설정
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '6003611602:AAFIlK1gAYRTh-IqSqrKLDnV6706Pd9D5RI')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '@emartbossblog')

def get_latest_news():
    """Claude를 사용하여 최신 AI 및 스테이블코인 뉴스를 검색하고 한글로 번역"""
    
    print("🔍 Claude로 최신 뉴스 검색 중...")
    
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        return None
    
    # 현재 날짜
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    prompt = f"""오늘은 {today}입니다.

다음 주제에 대한 최신 뉴스를 웹에서 검색하고 한글로 번역해주세요:
1. AI (인공지능)
2. 스테이블코인 (Stablecoin)

각 주제당 최근 3일 이내의 중요한 뉴스를 3개씩 찾아서 다음 형식으로 정리해주세요:

## 🤖 AI 뉴스

### [뉴스 제목 한글]
- **출처**: [뉴스 사이트명]
- **날짜**: [발행일]
- **요약**: [2-3문장으로 핵심 내용 요약]
- **링크**: [원문 URL]

(3개 반복)

## 💰 스테이블코인 뉴스

### [뉴스 제목 한글]
- **출처**: [뉴스 사이트명]
- **날짜**: [발행일]
- **요약**: [2-3문장으로 핵심 내용 요약]
- **링크**: [원문 URL]

(3개 반복)

---
📅 발행일: {today}

주의사항:
- 신뢰할 수 있는 뉴스 소스만 사용하세요 (TechCrunch, The Verge, Bloomberg, CoinDesk 등)
- 최신 뉴스 위주로 선별하세요
- 한글 번역은 자연스럽게 해주세요
- 실제 존재하는 뉴스만 포함하세요"""
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    except Exception as e:
        print(f"❌ Claude API 오류: {e}")
        return None

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
        for i, part in enumerate(parts):
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": part,
                "parse_mode": "Markdown"
            }
            
            try:
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    print(f"✅ 텔레그램 발송 성공 (파트 {i+1}/{len(parts)})")
                else:
                    print(f"⚠️ 텔레그램 발송 실패 (파트 {i+1}): {response.text}")
            except Exception as e:
                print(f"❌ 텔레그램 발송 오류 (파트 {i+1}): {e}")
    else:
        # 한 번에 전송
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
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
            print("\n✅ 모든 작업 완료!")
        else:
            print("\n⚠️ 일부 작업 실패")
    else:
        print("\n❌ 뉴스 수집 실패")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
