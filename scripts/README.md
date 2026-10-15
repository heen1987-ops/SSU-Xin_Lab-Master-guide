# 가이드 생성·검사·유지관리

## 원문과 생성본

`handbook/`와 `templates/`의 Markdown이 새 핸드북·서식의 원본입니다. `scripts/build_handbook.py`가 열람 페이지 13종과 내려받는 빈 서식 6종을 `docs/`와 `html/`에 생성합니다. 생성 HTML에는 원본 경로 주석이 있으므로 직접 수정하지 않습니다.

```text
python -m pip install -r scripts/requirements-docs.txt
python scripts/build_handbook.py
python scripts/build_handbook.py --check
python scripts/check_guide.py
python scripts/check_content.py
```

`--check`는 파일을 변경하지 않고 원문과 생성본·다운로드 서식의 일치를 확인합니다. Markdown 렌더러는 재현 가능한 생성을 위해 판본을 고정합니다. 변경 시 새로 생성하고 링크·표·목차를 다시 확인하세요.

기존 `index.html`, 방법별 페이지, `requirements.html`, `research-workbench.html`과 공통 CSS·JS는 수동 관리 대상입니다. `docs/`를 수정한 뒤 대응하는 `html/` 파일도 같은 내용으로 갱신합니다. 홈페이지 탐색·검색의 새 진입점은 `docs/assets/guide.js`에도 연결합니다.

## 자동 검사 범위

`python scripts/check_guide.py`는 Python 표준 라이브러리로 HTML 구조, 단계·기존 앵커, 내부 링크, 저장소 참조 파일, docs/html 일치를 검사합니다.

`python scripts/check_content.py`는 루트·트랙·단계별 지침·핸드북·서식·연구 작업지의 Markdown 목차 참조와 기존 감사에서 발견한 오류 유형 8개의 재등장을 검사합니다. 실제 검사 문서 수는 실행 결과에 표시합니다. 의미상 모든 충돌이나 외부 규정의 최신성을 자동 판정하지는 않습니다.

`node scripts/browser_qa.cjs`는 Playwright와 Chromium 계열 브라우저가 있는 환경에서 실행합니다. 먼저 `python -m http.server 8731 --bind 127.0.0.1 --directory docs`로 로컬 서버를 시작합니다.

- `GUIDE_BASE_URL`: 테스트할 서버 주소. 기본값 `http://127.0.0.1:8731/`, 마지막 `/` 포함
- `GUIDE_BROWSER_PATH`: 설치된 Chrome/Edge 실행 파일 경로. 생략하면 Playwright 기본 Chromium
- `GUIDE_QA_OUTPUT`: JSON 결과와 스크린샷 저장 폴더. 기본값 `.qa/`이며 Git에서 제외
- `NODE_PATH`: 환경에 이미 설치된 Playwright가 별도 패키지 경로에 있는 경우 해당 node_modules 경로

브라우저 검사는 7단계 진입, 키보드·검색 포커스·빈 결과·Escape, 테마·체크 저장, 여러 탭 병합, 1440/390/320px 가로 넘침, 기존 URL의 query·fragment, JavaScript·localStorage 비활성 대응을 확인합니다. 연구설계·근거검증 페이지 검색 이동, 내용 복사, 요청문 펼치기, 작업지 실제 다운로드와 작성표도 확인합니다. 전체 화면읽기 도구 검증이나 WCAG 적합성 인증을 대신하지 않습니다.

PR과 기본 브랜치의 자동 검사는 생성본 일치·구조·내용 검사를 수행합니다. PR은 검증만 하며, Pages 배포는 기본 브랜치 반영 또는 수동 실행 시 검사 통과 후 진행합니다. 브라우저 검사는 위 환경에서 별도로 실행합니다. 외부 규정의 최신성은 검사 대상이 아닙니다.

핸드북을 수정한 경우 실제 브라우저에서 목차·페이지 간 이동·서식 다운로드·좁은 화면의 표 스크롤도 확인하세요. 운영 문서의 검토 범위와 남은 과제는 `CHANGELOG.md`에 기록하고, 학생별 실제 기록은 공개 저장소에 추가하지 않습니다.
