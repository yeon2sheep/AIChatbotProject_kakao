# AIChatbotProject_kakao

## Overview

AIChatbotProject_kakao is a healthcare chatbot system designed to help caregivers easily access patient information through KakaoTalk.

The system automatically extracts key information from patient nursing records and medication records stored as PDF files in Amazon S3. AWS Lambda processes the uploaded documents, generates structured patient data in JSON format, and provides summarized patient status information through a KakaoTalk chatbot.

This project was developed as a prototype for improving communication between caregivers and healthcare providers by enabling convenient access to patient status updates.

### Tech Stack

* Python
* AWS Lambda
* Amazon S3
* Kakao Open Builder
* PyPDF2
* JSON

---

# 카카오톡 기반 환자 상태 조회 시스템

## 프로젝트 개요

본 프로젝트는 보호자가 카카오톡을 통해 환자의 상태를 손쉽게 확인할 수 있도록 구현한 시스템이다.

초기 목표는 환자의 상태 보고서를 매일 오전 10시에 보호자에게 자동으로 전송하는 것이었으나, 카카오톡의 정책상 일반 계정은 사용자가 먼저 메시지를 보내지 않은 상태에서 알림을 발송할 수 없다는 제약이 있었다.

이에 따라 사용자가 카카오톡 챗봇에 환자 정보를 입력하면 상태를 조회할 수 있는 방식으로 구현하였다.

---

# 카카오톡 알림 기능 구현

## 초기 목표

* 매일 오전 10시에 보호자에게 환자 상태 보고서를 카카오톡으로 자동 발송

## 제한 사항

* 카카오톡은 일반 계정에서 사용자가 먼저 메시지를 보내지 않은 경우 알림 발송이 불가능
* 선제적 메시지 발송 기능은 비즈니스 계정에서만 제공

## 구현 방식

* 사용자가 카카오톡 챗봇에 환자 정보를 입력
* 챗봇이 환자의 상태 정보를 조회
* 환자의 상태를 요약하여 응답

---

# 카카오톡 챗봇 기능

## 1. 환자 상태 요청

* 사용자가 카카오톡 챗봇에게 환자 상태 조회 요청
* 챗봇이 환자 이름과 인증 코드를 요청

## 2. 이름 및 인증 코드 입력

* 사용자가 환자 이름과 인증 코드를 입력
* 환자 이름과 인증 코드는 카카오 오픈빌더 엔티티로 사전 등록
* 입력된 값은 AWS Lambda 함수로 전달

## 3. 챗봇 응답 생성

* Lambda 함수가 환자 정보를 조회
* 환자의 상태 요약 정보를 생성
* AI 챗봇 사이트 이동 버튼을 함께 제공

## 4. 기본 대화 기능

* 인삿말 제공
* 사용 방법 안내
* 오류 발생 시 안내 문구 제공

---

# AWS Lambda를 활용한 응답 생성 방식

## 시스템 구성

### Input Bucket

* patient-data-pdf

### Output Bucket

* chatbot-patient-data

### Lambda Function

* AIchatbot_ocr
* chatbot2

---

# AIchatbot_ocr Lambda

## 동작 과정

1. 환자의 투약기록지 및 간호기록지 PDF를 S3 버킷(`patient-data-pdf`)에 업로드
2. S3 이벤트 트리거 발생
3. `AIchatbot_ocr` Lambda 함수 자동 실행
4. PDF 내용 분석 후 환자 정보 추출
5. JSON 파일 생성 및 저장

## PDF 데이터 처리

### 텍스트 추출

* `PyPDF2` 라이브러리의 `PdfReader` 클래스 사용
* 텍스트 기반 PDF에서 문자열 추출

### 투약기록지 처리

* 추출된 텍스트에 `"내복"` 문구 포함 여부 확인
* 포함 시 `"medication": "복약 완료"` 저장

### 간호기록지 처리

* 특정 키워드가 포함된 문장 추출

예시

* 큐로켈
* 점심은 계속 skip되는

추출 결과

* "낮에도 밤에도 소리지르는 행동보여 큐로켈 투여하면서 양상 관찰중"
* "점심은 계속 skip되는 양상보여 신경과 외진 파킨슨 증상심해져 진료후"

### JSON 저장

생성된 정보는 다음과 같은 형태로 저장된다.

```json
{
  "김영애": {
    "code": "3d35fr",
    "medication": "복약 완료",
    "status": "낮에도 밤에도 소리지르는 행동보여 큐로켈 투여하면서 양상 관찰중"
  },
  "장민규": {
    "code": "7x92ab",
    "medication": "복약 완료",
    "status": "점심은 계속 skip되는 양상보여 신경과 외진 파킨슨 증상심해져 진료후"
  }
}
```

생성된 파일은 `chatbot-patient-data` 버킷의 `patients.json`으로 저장된다.

---

# chatbot2 Lambda

## 동작 과정

1. `chatbot-patient-data` 버킷의 `patients.json` 읽기
2. 환자 이름 및 인증 코드 확인
3. 환자 정보 조회
4. 카카오톡 응답 메시지 생성
5. 사용자에게 결과 전달

## 조회 정보

* 환자 이름
* 인증 코드
* 복약 여부
* 상태 정보

## 응답 예시

```text
김영애님의 상태 요약

💊 복약 여부 : 복약 완료
💟 상태 : 낮에도 밤에도 소리지르는 행동보여 큐로켈 투여하면서 양상 관찰중

자세한 내용은 AI 챗봇에게 물어봐주세요.
```

---

# 전체 시스템 흐름

```text
PDF 업로드
    ↓
patient-data-pdf (S3)
    ↓
AIchatbot_ocr (Lambda)
    ↓
patients.json 생성
    ↓
chatbot-patient-data (S3)
    ↓
chatbot2 (Lambda)
    ↓
카카오 오픈빌더
    ↓
보호자
```
