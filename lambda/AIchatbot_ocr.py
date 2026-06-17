import json
import boto3
import re
from io import BytesIO
from PyPDF2 import PdfReader

s3 = boto3.client('s3')

PDF_BUCKET = 'patient-data-pdf'
JSON_BUCKET = 'chatbot-patient-data'
JSON_KEY = 'patients.json'

PATIENT_CODES = {
    "김영애": "3d35fr",
    "장민규": "7x92ab"
}


def extract_text_from_pdf_s3(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)

    pdf_stream = BytesIO(obj['Body'].read())
    pdf = PdfReader(pdf_stream)

    text = ''

    for page in pdf.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + '\n'

    return text


def parse_medication(text):
    if '내복' in text:
        return '복약 완료'

    return '정보 없음'


def parse_status(text, patient_name):

    sentences = re.split(r'[\n\.]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if patient_name == '김영애':
        for s in sentences:
            if '큐로켈' in s:
                return s

    elif patient_name == '장민규':
        for s in sentences:
            if '점심은 계속 skip되는' in s:
                return s

    return '정보 없음'


def update_json(patient_name, medication=None, status=None):

    try:
        obj = s3.get_object(
            Bucket=JSON_BUCKET,
            Key=JSON_KEY
        )

        patients = json.loads(
            obj['Body'].read().decode('utf-8')
        )

    except:
        patients = {}

    if patient_name not in patients:
        patients[patient_name] = {}

    patients[patient_name]['code'] = PATIENT_CODES.get(
        patient_name,
        'unknown'
    )

    if medication:
        patients[patient_name]['medication'] = medication

    if status:
        patients[patient_name]['status'] = status

    s3.put_object(
        Bucket=JSON_BUCKET,
        Key=JSON_KEY,
        Body=json.dumps(
            patients,
            ensure_ascii=False,
            indent=2
        ).encode('utf-8')
    )


def lambda_handler(event, context):

    for record in event['Records']:

        pdf_key = record['s3']['object']['key']

        patient_name = pdf_key.split('-')[0]

        text = extract_text_from_pdf_s3(
            PDF_BUCKET,
            pdf_key
        )

        if '투약기록지' in pdf_key:

            medication = parse_medication(text)

            update_json(
                patient_name,
                medication=medication
            )

        elif '간호기록지' in pdf_key:

            status = parse_status(
                text,
                patient_name
            )

            update_json(
                patient_name,
                status=status
            )

    return {
        'statusCode': 200,
        'body': 'patients.json 업데이트 완료'
    }