# Mock responses for testing without external API calls

# Mock Bus Location API Response
MOCK_BUS_RESPONSE = {
    "response": {
        "body": {
            "items": {
                "item": [
                    {
                        "vehicleno": "대전75자2322",
                        "gpslong": "127.364896",
                        "gpslati": "36.307911",
                        "nodenm": "정림동"
                    },
                    {
                        "vehicleno": "대전75자2329", 
                        "gpslong": "127.258867",
                        "gpslati": "36.26744",
                        "nodenm": "신성2차아파트"
                    },
                    {
                        "vehicleno": "대전75자2323",
                        "gpslong": "127.243192", 
                        "gpslati": "36.290569",
                        "nodenm": "엄사입구"
                    }
                ]
            }
        }
    }
}

# Mock Naver Map API Response
MOCK_NAVER_MAP_RESPONSE = {
    "code": 0,
    "message": "길찾기를 성공하였습니다.",
    "currentDateTime": "2025-01-27T10:00:00",
    "route": {
        "traoptimal": [{
            "guide": [
                {
                    "distance": 36,
                    "duration": 5980,
                    "instructions": "우회전",
                    "pointIndex": 3,
                    "type": 3
                },
                {
                    "distance": 234,
                    "duration": 62275,
                    "instructions": "'농소로' 방면으로 좌회전",
                    "pointIndex": 24,
                    "type": 2
                }
            ],
            "path": [
                [127.259626, 36.2640773],
                [127.2596026, 36.2640646],
                [127.2595293, 36.2640212]
            ],
            "summary": {
                "distance": 6029,
                "duration": 631887,
                "fuelPrice": 0,
                "taxiFare": 0,
                "tollFare": 0
            }
        }]
    }
}

# Mock TTS Response (for testing without actual audio generation)
MOCK_TTS_FILE = "test_files/mock_tts_output.mp3"

# Mock Twilio Response
MOCK_TWILIO_RESPONSE = {
    "sid": "mock_message_sid_123",
    "status": "sent",
    "to": "+1234567890",
    "from": "+0987654321",
    "body": "Test message"
}

# Helper function to simulate API delay
import time
import random

def simulate_api_delay(min_delay=0.1, max_delay=0.5):
    """Simulate realistic API response time"""
    time.sleep(random.uniform(min_delay, max_delay))