# AIChatbotProject_kakao
AWS Lambda + S3 + KakaoTalk Chatbot for patient status monitoring

## Architecture

PDF Upload
→ S3
→ Lambda OCR
→ patients.json
→ Lambda chatbot
→ KakaoTalk