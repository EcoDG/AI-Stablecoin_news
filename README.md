# 🤖 AI & 스테이블코인 뉴스봇

자동으로 AI와 스테이블코인 관련 최신 뉴스를 수집하여 텔레그램으로 발송하는 봇입니다.

## ✨ 주요 기능

- 🔍 Claude API로 최신 뉴스 자동 검색
- 🌏 영문 뉴스를 한글로 자동 번역
- 📱 텔레그램 채널로 자동 발송
- ⏰ 3일마다 자동 실행 (GitHub Actions)
- 💰 **완전 무료!** (Claude API 매월 $5 무료 크레딧)

## 📋 뉴스 주제

1. **AI (인공지능)** - 최신 AI 기술, 모델, 산업 동향
2. **스테이블코인** - 암호화폐, 규제, 시장 동향

## 🚀 설치 방법

### 1. GitHub 저장소 생성

1. GitHub에 새 저장소 생성 (Public/Private 모두 가능)
2. 다음 파일들을 저장소에 업로드:
   - `news_bot.py`
   - `requirements.txt`
   - `.github/workflows/news_bot.yml`

### 2. GitHub Secrets 설정

저장소 → Settings → Secrets and variables → Actions → New repository secret

다음 3개의 시크릿 추가:

| 이름 | 값 |
|------|-----|
| `ANTHROPIC_API_KEY` | Claude API 키 (https://console.anthropic.com 에서 발급) |
| `TELEGRAM_TOKEN` | `6003611602:AAFIlK1gAYRTh-IqSqrKLDnV6706Pd9D5RI` |
| `TELEGRAM_CHAT_ID` | `@emartbossblog` |

#### Claude API 키 발급 방법
1. https://console.anthropic.com 접속
2. 회원가입/로그인
3. API Keys → Create Key
4. 생성된 키를 복사하여 GitHub Secrets에 추가

### 3. GitHub Actions 활성화

1. 저장소 → Actions 탭
2. "I understand my workflows, go ahead and enable them" 클릭

## ⚙️ 실행 방법

### 자동 실행
- **3일마다** 자동으로 실행됩니다
- GitHub Actions가 알아서 처리합니다

### 수동 실행 (테스트용)
1. 저장소 → Actions 탭
2. "뉴스봇 자동 실행" 워크플로우 선택
3. "Run workflow" → "Run workflow" 클릭

## 🧪 로컬 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export ANTHROPIC_API_KEY="your-claude-api-key"
export TELEGRAM_TOKEN="6003611602:AAFIlK1gAYRTh-IqSqrKLDnV6706Pd9D5RI"
export TELEGRAM_CHAT_ID="@emartbossblog"

# 실행
python news_bot.py
```

## 📅 실행 주기 변경

`.github/workflows/news_bot.yml` 파일의 cron 설정 수정:

```yaml
# 매일 오전 9시
- cron: '0 0 * * *'

# 매주 월요일 오전 9시
- cron: '0 0 * * 1'

# 3일마다 (현재 설정)
- cron: '0 0 */3 * *'
```

## 🎨 커스터마이징

### 뉴스 주제 변경

`news_bot.py`의 `prompt` 부분 수정:

```python
prompt = f"""
다음 주제에 대한 최신 뉴스를 검색하고 한글로 번역해주세요:
1. AI (인공지능)
2. 스테이블코인
3. 블록체인  # 새 주제 추가
4. 메타버스  # 새 주제 추가
"""
```

### 뉴스 개수 변경

```python
# "각 주제당 3개씩" → "각 주제당 5개씩"으로 변경
각 주제당 최근 3일 이내의 중요한 뉴스 5개씩 찾아서
```

## 📊 예상 결과 샘플

```
## 🤖 AI 뉴스

### OpenAI, GPT-5 개발 중단 발표
- **출처**: TechCrunch
- **날짜**: 2024-11-01
- **요약**: OpenAI가 GPT-5 개발을 일시 중단하고 안전성 검증에 집중한다고 발표...
- **링크**: https://techcrunch.com/...

## 💰 스테이블코인 뉴스

### 테더, 10억 달러 추가 발행
- **출처**: CoinDesk
- **날짜**: 2024-11-02
- **요약**: 테더가 이더리움 네트워크에서 10억 USDT를 추가 발행...
- **링크**: https://coindesk.com/...
```

## 🔧 트러블슈팅

### Claude API 오류
- API 키가 올바른지 확인
- API 할당량 초과 여부 확인: https://console.anthropic.com
- 매월 $5 무료 크레딧 제공 (충분히 사용 가능)

### 텔레그램 발송 실패
- 봇이 채널의 관리자인지 확인
- CHAT_ID가 `@`로 시작하는지 확인 (채널의 경우)
- 또는 숫자 ID 사용 가능 (개인/그룹 채팅)

### GitHub Actions 실행 안 됨
- Actions 탭에서 활성화 여부 확인
- Secrets가 올바르게 설정되었는지 확인
- 워크플로우 파일 경로 확인: `.github/workflows/news_bot.yml`

## 💡 향후 추가 가능 기능

- [ ] 이메일 발송 기능
- [ ] 더 많은 뉴스 주제 추가
- [ ] 감정 분석 및 중요도 점수
- [ ] 주간 요약 리포트
- [ ] Slack 연동

## 📞 문의

문제가 있거나 개선 아이디어가 있다면 GitHub Issues에 등록해주세요!

---

**Made with ❤️ using Claude AI & GitHub Actions**
