# 공통 가이드 회귀 검사

`python scripts/check_guide.py`는 Python 표준 라이브러리로 HTML 구조, 단계·기존 앵커, 내부 링크, 저장소 참조 파일, docs/html 일치를 검사합니다.

`python scripts/check_content.py`는 가이드 Markdown 65개(본문 64개와 작업지), Markdown 목차 참조, 이번 감사에서 발견한 오류 유형 8개의 재등장을 검사합니다. 의미상 모든 충돌이나 외부 규정의 최신성을 자동 판정하지는 않습니다.

`node scripts/browser_qa.cjs`는 Playwright와 Chromium 계열 브라우저가 있는 환경에서 실행합니다. 먼저 `python -m http.server 8731 --bind 127.0.0.1 --directory docs`로 로컬 서버를 시작합니다.

- `GUIDE_BASE_URL`: 테스트할 서버 주소. 기본값 `http://127.0.0.1:8731/`, 마지막 `/` 포함
- `GUIDE_BROWSER_PATH`: 설치된 Chrome/Edge 실행 파일 경로. 생략하면 Playwright 기본 Chromium
- `GUIDE_QA_OUTPUT`: JSON 결과와 스크린샷 저장 폴더. 기본값 `.qa/`이며 Git에서 제외
- `NODE_PATH`: 환경에 이미 설치된 Playwright가 별도 패키지 경로에 있는 경우 해당 node_modules 경로

브라우저 검사는 7단계 진입, 키보드·검색 포커스·빈 결과·Escape, 테마·체크 저장, 여러 탭 병합, 1440/390/320px 가로 넘침, 기존 URL의 query·fragment, JavaScript·localStorage 비활성 대응을 확인합니다. 연구설계·근거검증 페이지 검색 이동, 내용 복사, 요청문 펼치기, 작업지 실제 다운로드와 작성표도 확인합니다. 전체 화면읽기 도구 검증이나 WCAG 적합성 인증을 대신하지 않습니다.

배포 워크플로는 `check_guide.py`와 `check_content.py`를 통과해야 Pages 파일을 올립니다. 브라우저 검사는 위 환경에서 별도로 실행합니다. 외부 규정의 최신성은 검사 대상이 아닙니다.
