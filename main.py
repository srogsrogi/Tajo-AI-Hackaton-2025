# app.py
import os, json, base64, asyncio, websockets, logging
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect
from dotenv import load_dotenv

# 로깅 설정 추가
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 5050))
# EC2 공개 IP 또는 도메인 설정
PUBLIC_DOMAIN = os.getenv("PUBLIC_DOMAIN")  # 예: "http://your-ec2-ip:5050" 또는 "https://your-domain.com"

VOICE = "alloy"
SYSTEM_MESSAGE = """
당신은 호출형 택시 서비스의 음성 안내 챗봇입니다. 

대화 시작 시 반드시 다음과 같이 인사하세요:
"안녕하세요! 택시 호출 서비스입니다. 먼저 출발지를 알려주시겠어요?"

그 다음 목표는 사용자의 "출발지"와 "도착지" 정보를 자연스럽고 정확하게 파악하는 것입니다.

규칙:
- 사용자가 명확히 대답하지 않으면 다시 한번 친절하게 질문하세요.
- 지명, 건물 이름, 병원, 역, 아파트, 회사 등 어떤 표현도 이해하고 받아들이세요.
- 사용자가 "여기" 또는 "내 위치"라고 말하면 "정확한 위치를 알기 위해 주소나 근처 건물 이름을 알려달라"고 답하세요.
- 출발지와 도착지를 모두 확인하면 "이제 택시를 배차해드릴게요. 잠시만 기다려주세요."라고 마무리하세요.
- 한 번에 하나의 질문만 하세요.
- 톤은 공손하고 자연스러우며 부담스럽지 않게 유지하세요.
- 항상 한국어로 대답하세요.
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return "<h1>gpt-4o-mini Realtime Test Server Running</h1>"


@app.get("/health")
async def health_check():
    return {"status": "healthy", "domain": PUBLIC_DOMAIN}


@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    print(f"=== INCOMING CALL DEBUG INFO ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {dict(request.headers)}")

    # POST 데이터 확인
    if request.method == "POST":
        try:
            form_data = await request.form()
            print(f"Form data: {dict(form_data)}")
        except Exception as e:
            print(f"Error reading form data: {e}")

    # Query parameters 확인
    print(f"Query params: {dict(request.query_params)}")

    # PUBLIC_DOMAIN 확인
    print(f"PUBLIC_DOMAIN env var: {PUBLIC_DOMAIN}")

    response = VoiceResponse()

    # PUBLIC_DOMAIN 사용 (환경변수에서 설정)
    if PUBLIC_DOMAIN:
        base_url = PUBLIC_DOMAIN
        print(f"Using PUBLIC_DOMAIN: {base_url}")
    else:
        # fallback: request에서 추출
        scheme = "https" if request.url.scheme == "https" else "http"
        host = request.headers.get("host", request.url.netloc)
        base_url = f"{scheme}://{host}"
        print(f"Using fallback URL: {base_url}")

    # WebSocket URL 생성
    websocket_url = base_url.replace("http://", "ws://").replace("https://", "wss://") + "/media-stream"
    print(f"Generated WebSocket URL: {websocket_url}")

    connect = Connect()
    connect.stream(url=websocket_url)
    response.append(connect)

    twiml_response = str(response)
    print(f"Generated TwiML Response: {twiml_response}")
    print(f"=== END DEBUG INFO ===")

    return HTMLResponse(content=twiml_response, media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    logger.info("=== WEBSOCKET CONNECTION ATTEMPT ===")
    logger.info(f"Client headers: {websocket.headers}")
    logger.info(f"Client query params: {websocket.query_params}")

    try:
        await websocket.accept()
        logger.info("WebSocket connection established successfully")
    except Exception as e:
        logger.error(f"Failed to accept WebSocket connection: {e}")
        return

    logger.info("Attempting to connect to OpenAI WebSocket...")

    try:
        async with websockets.connect(
                'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview',
                additional_headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "OpenAI-Beta": "realtime=v1"
                }
        ) as openai_ws:
            logger.info("Successfully connected to OpenAI WebSocket")
            await send_session_update(openai_ws)
            stream_sid = None
            mark_queue = []
            latest_media_timestamp = 0
            last_assistant_item = None
            response_start_timestamp_twilio = None

            async def receive_from_twilio():
                nonlocal stream_sid, latest_media_timestamp
                try:
                    async for msg in websocket.iter_text():
                        data = json.loads(msg)
                        logger.debug(f"🔵 Received from Twilio: {data['event']}")

                        if data['event'] == 'media' and openai_ws.open:
                            latest_media_timestamp = int(data['media']['timestamp'])
                            logger.debug(f"📤 Sending audio data to OpenAI (timestamp: {latest_media_timestamp})")
                            await openai_ws.send(json.dumps({
                                "type": "input_audio_buffer.append",
                                "audio": data['media']['payload']
                            }))
                        elif data['event'] == 'start':
                            stream_sid = data['start']['streamSid']
                            logger.info(f"🟢 Stream started with SID: {stream_sid}")
                        elif data['event'] == 'mark' and mark_queue:
                            logger.debug(f"✅ Mark received, removing from queue")
                            mark_queue.pop(0)
                        elif data['event'] == 'stop':
                            logger.info("🔴 Stream stopped")
                            break
                except WebSocketDisconnect:
                    logger.warning("🔌 Twilio WebSocket disconnected")
                    if openai_ws.open:
                        await openai_ws.close()
                except Exception as e:
                    logger.error(f"❌ Error in receive_from_twilio: {e}")

            async def send_to_twilio():
                nonlocal last_assistant_item, response_start_timestamp_twilio
                try:
                    async for msg in openai_ws:
                        res = json.loads(msg)
                        event_type = res.get('type', 'unknown')
                        logger.debug(f"🟡 Received from OpenAI: {event_type}")
                        
                        # 전체 메시지 내용 로깅 (민감한 정보 제외)
                        if event_type not in ['response.audio.delta']:  # 오디오 데이터는 너무 길어서 제외
                            logger.debug(f"📋 OpenAI message details: {json.dumps(res, indent=2, ensure_ascii=False)}")

                        if res.get('type') == 'response.audio.delta' and 'delta' in res:
                            payload = base64.b64encode(base64.b64decode(res['delta'])).decode()
                            await websocket.send_json({
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {"payload": payload}
                            })
                            logger.debug(f"🔊 Sent audio delta to Twilio")

                            if response_start_timestamp_twilio is None:
                                response_start_timestamp_twilio = latest_media_timestamp
                                logger.info("🎵 Started sending audio response to Twilio")

                            if res.get('item_id'):
                                last_assistant_item = res['item_id']
                            await send_mark(websocket, stream_sid)

                        elif res.get('type') == 'input_audio_buffer.speech_stopped':
                            logger.info("🤐 User speech stopped detected")

                        elif res.get('type') == 'input_audio_buffer.committed':
                            logger.info("💾 User audio committed to conversation")
                            # 사용자 음성이 커밋된 후 응답 생성 트리거
                            logger.info("🎯 Triggering response generation after user input")
                            await openai_ws.send(json.dumps({
                                "type": "response.create",
                                "response": {
                                    "modalities": ["text", "audio"]
                                }
                            }))

                        elif res.get('type') == 'conversation.item.created':
                            logger.info(f"💬 Conversation item created: {res.get('item', {}).get('type', 'unknown')}")
                            if res.get('item', {}).get('type') == 'message':
                                role = res.get('item', {}).get('role', 'unknown')
                                content = res.get('item', {}).get('content', [])
                                logger.info(f"📝 Message from {role}: {content}")
                                
                                # 사용자 메시지인 경우 특별히 로깅
                                if role == 'user':
                                    logger.info(f"👤 USER INPUT DETECTED: {content}")

                        elif res.get('type') == 'conversation.item.input_audio_transcription.completed':
                            transcript = res.get('transcript', '')
                            logger.info(f"🎤 User speech transcribed: '{transcript}'")

                        elif res.get('type') == 'response.created':
                            logger.info("🚀 OpenAI response created")

                        elif res.get('type') == 'response.output_item.added':
                            logger.info("➕ Response output item added")

                        elif res.get('type') == 'response.content_part.added':
                            logger.info("📄 Response content part added")

                        elif res.get('type') == 'response.audio_transcript.delta':
                            transcript = res.get('delta', '')
                            logger.info(f"📝 AI transcript delta: '{transcript}'")

                        elif res.get('type') == 'response.audio_transcript.done':
                            transcript = res.get('transcript', '')
                            logger.info(f"✅ AI final transcript: '{transcript}'")

                        elif res.get('type') == 'response.done':
                            logger.info("🏁 OpenAI response completed")
                            response_start_timestamp_twilio = None

                        elif res.get('type') == 'error':
                            logger.error(f"❌ OpenAI Error: {res}")

                        elif res.get('type') == 'session.created':
                            logger.info("🎯 OpenAI session created successfully")

                        elif res.get('type') == 'session.updated':
                            logger.info("🔄 OpenAI session updated")

                        elif res.get('type') == 'input_audio_buffer.speech_started':
                            logger.info("🗣️ User speech started detected")
                            if last_assistant_item:
                                logger.info("⚠️ Speech interruption detected - handling interruption")
                                await handle_interruption()

                        elif res.get('type') == 'rate_limits.updated':
                            logger.debug(f"📊 Rate limits updated: {res.get('rate_limits', {})}")

                        else:
                            logger.debug(f"❓ Unhandled OpenAI event type: {event_type}")
                            # 알려지지 않은 이벤트의 전체 내용도 로깅
                            logger.debug(f"🔍 Full unknown event: {json.dumps(res, indent=2, ensure_ascii=False)}")

                except Exception as e:
                    logger.error(f"❌ Error in send_to_twilio: {e}")
                    import traceback
                    traceback.print_exc()

            async def handle_interruption():
                nonlocal last_assistant_item, response_start_timestamp_twilio
                logger.info("🛑 Handling speech interruption")
                elapsed = latest_media_timestamp - response_start_timestamp_twilio
                logger.debug(f"⏱️ Elapsed time for truncation: {elapsed}ms")
                await openai_ws.send(json.dumps({
                    "type": "conversation.item.truncate",
                    "item_id": last_assistant_item,
                    "content_index": 0,
                    "audio_end_ms": elapsed
                }))
                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })
                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None
                logger.info("✂️ Interruption handled - audio truncated and cleared")

            async def send_mark(ws, sid):
                if sid:
                    await ws.send_json({
                        "event": "mark",
                        "streamSid": sid,
                        "mark": {"name": "responsePart"}
                    })
                    mark_queue.append("responsePart")
                    logger.debug(f"🏷️ Sent mark to Twilio")

            logger.info("🔄 Starting main communication loops...")
            await asyncio.gather(receive_from_twilio(), send_to_twilio())

    except Exception as e:
        logger.error(f"❌ Error in media stream: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("🔌 WebSocket connection closed")


async def send_session_update(openai_ws):
    logger.info("📤 Sending session update to OpenAI...")
    # 세션 설정
    await openai_ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["audio", "text"],
            "temperature": 0.6
        }
    }))
    logger.info("⚙️ Session configuration sent")

    # 시스템이 먼저 인사하도록 설정
    logger.info("💬 Creating initial greeting message...")
    await openai_ws.send(json.dumps({
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "assistant",
            "content": [{
                "type": "text",
                "text": "안녕하세요! 택시 호출 서비스입니다. 먼저 출발지를 알려주시겠어요?"
            }]
        }
    }))
    logger.info("📝 Initial greeting message created")

    # AI가 응답을 생성하도록 트리거
    logger.info("🚀 Triggering initial response creation...")
    await openai_ws.send(json.dumps({
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"]
        }
    }))
    logger.info("✅ Initial response creation triggered")


# Run server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=PORT)