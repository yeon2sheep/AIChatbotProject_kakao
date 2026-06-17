import boto3
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_bucket = os.environ['S3_BUCKET_NAME']
s3_key = os.environ['S3_FILE_KEY']


def load_patient_data():
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=s3_bucket, Key=s3_key)
    return json.loads(obj['Body'].read().decode('utf-8'))


def make_card_message(name, data):
    """
    JSON에 맞춰 카드 메시지 생성 (인증 코드 제거 버전)
    """
    patient_info = data.get(name)

    if patient_info:
        return {
            "basicCard": {
                "title": f"{name}님의 상태 요약",
                "description": (
                    f"💊 복약 여부: {patient_info.get('medication', '정보 없음')}\n"
                    f"💟 상태: {patient_info.get('status', '정보 없음')}\n\n"
                    f"자세한 내용은 AI 챗봇에게 물어봐주세요! 😊"
                ),
                "buttons": [
                    {
                        "action": "webLink",
                        "label": "AI 챗봇 바로 가기",
                        "webLinkUrl": "https://cnrkddl.github.io/AIChatbotProject/"
                    }
                ]
            }
        }
    else:
        return {
            "simpleText": {
                "text": "입력하신 이름과 일치하는 환자를 찾을 수 없습니다. 😢"
            }
        }


def lambda_handler(event, context):
    logger.info("Received event: " + json.dumps(event, ensure_ascii=False))
    try:
        body = json.loads(event.get("body", "{}"))
        params = body.get("action", {}).get("params", {})
        name = params.get("patient_name")

        logger.info(f"Received params - Name: {name}")

        # 이름이 없으면 안내
        if not name:
            return {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "환자 이름을 입력해 주세요. ❤️‍🩹\n예) 김영애"
                            }
                        }
                    ]
                }
            }

        # 데이터 조회
        data = load_patient_data()
        response_card = make_card_message(name, data)

        return {"version": "2.0", "template": {"outputs": [response_card]}}

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return {
            "version": "2.0",
            "template": {"outputs": [{"simpleText": {"text": f"오류가 발생했습니다: {str(e)}"}}]}
        }