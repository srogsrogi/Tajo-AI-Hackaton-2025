#!/usr/bin/env python3
"""
Test module for running code without external API calls
This allows you to test your logic, data processing, and flow without network dependencies
"""

import os
import json
from unittest.mock import Mock, patch
from mock_responses import (
    MOCK_BUS_RESPONSE, 
    MOCK_NAVER_MAP_RESPONSE, 
    MOCK_TWILIO_RESPONSE,
    simulate_api_delay
)

class OfflineTestManager:
    """Manages offline testing by mocking external services"""
    
    def __init__(self):
        self.mock_mode = True
        
    def mock_bus_api(self, city_code=None, route_id=None):
        """Mock bus location API without external call"""
        if self.mock_mode:
            print("🚌 [MOCK MODE] Using mock bus location data")
            simulate_api_delay()
            return MOCK_BUS_RESPONSE
        else:
            # This would be your actual API call
            import requests
            # ... actual API call code
            pass
    
    def mock_naver_map_api(self, start=None, goal=None):
        """Mock Naver Map API without external call"""
        if self.mock_mode:
            print("🗺️ [MOCK MODE] Using mock map direction data")
            simulate_api_delay()
            return MOCK_NAVER_MAP_RESPONSE
        else:
            # This would be your actual API call
            import requests
            # ... actual API call code
            pass
    
    def mock_tts_generation(self, text, output_file=None):
        """Mock TTS generation without external call"""
        if self.mock_mode:
            print(f"🔊 [MOCK MODE] Would generate TTS for: '{text}'")
            print(f"📁 [MOCK MODE] Would save to: {output_file or 'default.mp3'}")
            return {"status": "success", "file": output_file or "mock_tts.mp3"}
        else:
            # This would be your actual gTTS call
            from gtts import gTTS
            # ... actual TTS generation code
            pass
    
    def mock_twilio_sms(self, to, body):
        """Mock Twilio SMS without external call"""
        if self.mock_mode:
            print(f"📱 [MOCK MODE] Would send SMS to {to}: '{body}'")
            simulate_api_delay()
            return MOCK_TWILIO_RESPONSE
        else:
            # This would be your actual Twilio call
            from twilio.rest import Client
            # ... actual SMS sending code
            pass
    
    def test_stt_with_local_files(self):
        """Test STT functionality using your existing audio files"""
        print("🎤 Testing STT with local files (NO external calls needed)")
        
        # This uses your existing test files and Whisper model locally
        test_files = [
            "test_files/강남역에가고싶어요.m4a",
            "test_files/노인남여_노인대화07_F_1522434093_60_경상_실내_08582.wav"
        ]
        
        try:
            import whisper
            model = whisper.load_model("base")  # Use smaller model for testing
            
            for file_path in test_files:
                if os.path.exists(file_path):
                    print(f"🔄 Processing: {file_path}")
                    result = model.transcribe(file_path, language="ko")
                    print(f"📝 Result: {result['text']}")
                    print()
                else:
                    print(f"❌ File not found: {file_path}")
                    
        except ImportError:
            print("⚠️ Whisper not installed. Install with: pip install openai-whisper")
            print("🔄 [MOCK MODE] STT would process audio files and return text")
            
    def test_full_pipeline_offline(self):
        """Test the complete pipeline without any external calls"""
        print("🔄 Testing complete pipeline in OFFLINE mode")
        print("=" * 50)
        
        # 1. Mock getting bus locations
        print("1️⃣ Getting bus locations...")
        bus_data = self.mock_bus_api(city_code="25", route_id="DJB30300052")
        print(f"   Found {len(bus_data['response']['body']['items']['item'])} buses")
        
        # 2. Mock getting directions
        print("\n2️⃣ Getting route directions...")
        route_data = self.mock_naver_map_api(
            start="127.259624, 36.264081",
            goal="127.299242, 36.279915"
        )
        print(f"   Route distance: {route_data['route']['traoptimal'][0]['summary']['distance']}m")
        
        # 3. Mock TTS generation
        print("\n3️⃣ Generating speech...")
        tts_result = self.mock_tts_generation("버스가 정림동에 도착했습니다")
        print(f"   TTS Status: {tts_result['status']}")
        
        # 4. Mock sending notification
        print("\n4️⃣ Sending notification...")
        sms_result = self.mock_twilio_sms("+1234567890", "버스 알림")
        print(f"   SMS Status: {sms_result['status']}")
        
        print("\n✅ Pipeline test completed successfully!")
        print("💡 All external calls were mocked - no network required!")

def run_offline_tests():
    """Run all offline tests"""
    print("🧪 OFFLINE TESTING MODE")
    print("=" * 50)
    
    tester = OfflineTestManager()
    
    # Test 1: STT with local files
    tester.test_stt_with_local_files()
    
    print("\n" + "=" * 50)
    
    # Test 2: Full pipeline
    tester.test_full_pipeline_offline()
    
    print("\n" + "=" * 50)
    print("✅ All offline tests completed!")
    print("💡 You can develop and test your logic without any external API calls!")

if __name__ == "__main__":
    run_offline_tests()