## 프로젝트 설치
1. 레포 클론
```bash
git clone https://github.com/2025Ilovespongebob/BE
cd BE
```
2. 가상환경 세팅
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# 커밋 컨벤션

| 유형     | 상세                                         |
| -------- | -------------------------------------------- |
| feat     | 새로운 기능 추가                             |
| fix      | 버그 수정                                    |
| refactor | 코드 리팩토링 (기능 변경 없이 구조 개선)     |
| test     | 테스트 코드 작성                             |
| chore    | 기타 자잘한 작업 (빌드 설정, 패키지 관리 등) |
| docs     | 문서 추가 또는 수정                          |
| delete   | 불필요한 코드나 파일 삭제                    |
| build    | 빌드 관련 파일 및 설정 변경                  |

---

## 브랜치 형식
커밋유형/#이슈번호
예 : feat/#1

## 라우터 설명
main.py: FastAPI 앱 인스턴스 생성 및 라우터(Router) 등록.
core/: 공통 설정(환경 변수, DB 설정 등), 보안 로직 등.
routers/ (또는 api/): 엔드포인트 정의 (HTTP 메소드, 경로).
schemas/ (또는 models/): Pydantic 모델로 데이터 유효성 검사 및 직렬화 담당.
services/: 비즈니스 로직 구현. 라우터와 데이터베이스 사이의 중개 역할.
repositories/ (또는 db/): 데이터베이스 접근 및 CRUD 작업.
domain/: 핵심 비즈니스 규칙 및 엔티티(Entity).

## 한 브랜치에서 개발 끝나고 다른 브랜치에서 개발 할 때,
git checkout main
git pull origin main
git checkout -b feat/#?

