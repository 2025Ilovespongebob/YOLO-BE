# 🎯 YOLO Object Detection API Server

실시간 객체 감지를 위한 FastAPI 기반 스트리밍 서버

## 🚀 서버 실행

```bash
pip install -r requirements.txt
python -m app.main
# 서버: http://0.0.0.0:8000
```

---

## 📡 API 엔드포인트

### 1️⃣ WebSocket 실시간 스트리밍 (권장)

**Endpoint:** `ws://{SERVER_IP}:8000/stream/ws`

#### 요청 (클라이언트 → 서버)
```json
{
  "frame": "data:image/jpeg;base64,/9j/4AAQ...",
  "conf_threshold": 0.5
}
```

| 필드 | 타입 | 설명 |
|-----|------|-----|
| `frame` | string | Base64 인코딩된 이미지 (JPEG 권장) |
| `conf_threshold` | float | 감지 신뢰도 임계값 (0.0~1.0, 기본값 0.5) |

#### 응답 (서버 → 클라이언트)
```json
{
  "detections": [
    {
      "class_id": 0,
      "class_name": "pothole",
      "confidence": 0.89,
      "bbox": { "x1": 100, "y1": 150, "x2": 300, "y2": 400 }
    }
  ],
  "annotated_frame": "data:image/jpeg;base64,/9j/4AAQ...",
  "detection_count": 1
}
```

| 필드 | 타입 | 설명 |
|-----|------|-----|
| `detections` | array | 감지된 객체 목록 |
| `detections[].class_id` | int | 클래스 번호 |
| `detections[].class_name` | string | 클래스 이름 |
| `detections[].confidence` | float | 신뢰도 (0.0~1.0) |
| `detections[].bbox` | object | 바운딩 박스 좌표 (픽셀) |
| `annotated_frame` | string | 바운딩박스가 그려진 이미지 (Base64) |
| `detection_count` | int | 감지된 객체 수 |

---

### 2️⃣ HTTP 단일 이미지 감지

**Endpoint:** `POST /stream/detect`

#### 요청
```
Content-Type: application/x-www-form-urlencoded

image_base64=data:image/jpeg;base64,/9j/4AAQ...
conf_threshold=0.5  (optional, query param)
```

#### 응답
WebSocket 응답과 동일한 JSON 형식

---

### 3️⃣ 클래스 목록 조회

**Endpoint:** `GET /stream/classes`

#### 응답
```json
{
  "classes": {
    "0": "pothole",
    "1": "crack"
  }
}
```

---

## 📱 React Native / Expo 연동 예시

```javascript
const SERVER_IP = '192.168.0.10'; // ⚠️ 서버 IP로 변경
const ws = new WebSocket(`ws://${SERVER_IP}:8000/stream/ws`);

// 이미지 전송 (카메라에서 캡처한 base64 이미지)
const sendFrame = (base64Image) => {
  ws.send(JSON.stringify({
    frame: base64Image,
    conf_threshold: 0.5
  }));
};

// 결과 수신
ws.onmessage = (event) => {
  const { detections, annotated_frame, detection_count } = JSON.parse(event.data);
  console.log(`감지된 객체: ${detection_count}개`);
  // detections 배열로 UI 업데이트
  // annotated_frame을 Image 컴포넌트에 표시
};
```

---

## ⚠️ 주의사항

| 항목 | 내용 |
|-----|------|
| **이미지 형식** | JPEG Base64 권장 (PNG도 가능) |
| **이미지 크기** | 640x480 권장 (너무 크면 느려짐) |
| **IP 주소** | 모바일에서는 `localhost` 대신 서버 IP 사용 |
| **네트워크** | 서버와 클라이언트가 같은 Wi-Fi에 있어야 함 |

---

## 🔧 API 문서 (Swagger UI)

서버 실행 후 http://localhost:8000/docs 접속

---

## 📂 프로젝트 구조

```
app/
├── main.py              # FastAPI 앱
├── router/
│   └── stream.py        # 스트리밍 엔드포인트
├── service/
│   └── yolo_service.py  # YOLO 모델 서비스
└── best.pt              # YOLO 모델 파일
```
