# Taewojo(수요응답형 버스) 음성 챗봇 서버

유선전화를 통해 택시/버스를 호출할 수 있는 **음성 기반 AI 챗봇** 서버입니다.  
Twilio 음성 전화 → WebSocket 실시간 음성 스트리밍 → OpenAI GPT-4o-mini Realtime API를 통해 사용자와 대화를 수행합니다.

---

## 프로젝트 개요

- **목표:**  
  유선전화를 통해도 누구나 AI와 대화하여 **택시/버스 호출 요청**을 할 수 있는 시스템을 구현합니다.

- **주요 기능:**  
  1. 전화를 걸면 AI가 자동으로 “출발지”와 “도착지”를 자연스럽게 파악  
  2. AI 응답 중 사용자가 말을 시작하면 실시간으로 **발화 중단(Interrupt)** 감지 및 응답 취소  
  3. 출발지/도착지 파악 후 호출 배차 로직 연계 가능

- **적용 사례:**  
  - 고령자, 시각장애인 등 스마트폰이 어려운 사용자
  - 유선전화만 가능한 농촌 지역

---

## 시스템 아키텍처

```
[사용자 유선전화]
        │
        ▼
     Twilio
        │
        ▼
[FastAPI 서버 (media-stream WebSocket)]
        │
        ▼
OpenAI Realtime API (GPT-4o-mini)
        │
        ▼
   음성 ↔ 텍스트 ↔ 음성
```

---

## 기술 스택

| 구분          | 기술                                       |
| ------------- | ------------------------------------------ |
| 웹 프레임워크 | FastAPI                                    |
| 음성 입출력   | Twilio Programmable Voice                  |
| AI 모델       | OpenAI GPT-4o-mini (Realtime API)          |
| 스트리밍 처리 | WebSocket (asyncio + websockets)           |
| 음성 코덱     | g711_ulaw (Twilio ↔ OpenAI 동일 포맷 유지) |
| 배포 환경     | AWS EC2                                    |

---

## 대화 흐름 예시

```
AI: 안녕하세요! 택시 호출 서비스입니다. 먼저 출발지를 알려주시겠어요?
사용자: 수서역 1번 출구요.
AI: 네, 도착지는 어디로 가실 건가요?
사용자: 코엑스요.
AI: 이제 택시를 배차해드릴게요. 잠시만 기다려주세요.
```

- 사용자가 "여기요", "내 위치" 등 모호한 표현을 쓸 경우 AI는 다시 정중히 위치를 물어봅니다.
- AI 발화 중 사용자가 말을 시작하면 **즉시 응답을 중단**하고 사용자 발화를 수신합니다.

---

## 주요 모듈 구성

| 파일/함수               | 설명                                                         |
| ----------------------- | ------------------------------------------------------------ |
| `/incoming-call`        | Twilio에서 전화 수신 시 호출되는 엔드포인트<br>WebSocket 주소가 포함된 TwiML 응답 전송 |
| `/media-stream`         | Twilio ↔ OpenAI 간 음성 데이터 실시간 중계 WebSocket         |
| `send_session_update()` | OpenAI 세션 구성: 음성 설정, 프롬프트, 턴 감지 방식 등 설정  |
| `receive_from_twilio()` | Twilio로부터 사용자 음성(STT용) 수신                         |
| `send_to_twilio()`      | OpenAI 응답(TTS용)을 Twilio에 전송                           |
| `handle_interruption()` | 사용자 말 끊기 감지 및 AI 응답 중단                          |
| `.env`                  | 환경 변수 파일 (API 키, 도메인, 포트 등 설정)                |

---

## 실행 방법

1. `.env` 파일 생성  

   ```
   OPENAI_API_KEY=sk-xxxx...
   PUBLIC_DOMAIN=https://your-domain.com  # 또는 EC2 퍼블릭 IP
   PORT=5050
   ```

2. Python 패키지 설치  

   ```bash
   pip install -r requirements.txt
   ```

3. 서버 실행  

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 5050
   ```

4. Twilio Console에서 Voice Webhook을 다음과 같이 설정  

   - **Voice → Webhook URL**: `https://<PUBLIC_DOMAIN>/incoming-call`
