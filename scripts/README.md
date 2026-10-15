# 사이트 빌드와 검사

Python 3.11 이상에서 실행합니다.

```sh
python -m pip install -r scripts/requirements.txt
python scripts/build_site.py
python scripts/build_site.py --check
python scripts/check_guide.py
python scripts/check_content.py
python -m http.server 8732 --directory docs
```

`content/*.md`가 본문 원본이며 `docs/*.html`은 생성 결과입니다. 본문은 원본에서 수정하고 다시 빌드합니다. `docs/assets/guide.css`는 공통 서식입니다. 외부 글꼴·분석 스크립트 없이 동작하며 JavaScript는 이전 주소 이동에만 사용합니다.

빌드 검사는 생성물의 일치 여부를, HTML 검사는 내부 링크·앵커·중복 ID·탐색 구조·이전 주소의 검색어/앵커 보존을 확인합니다. 내용 검사는 원본 링크와 기존의 잘못된 안내가 재등장하는지 확인합니다. 이 검사가 인용 원문의 정확성이나 연구의 타당성을 자동으로 보증하지는 않습니다.

화면 변경 시에는 브라우저에서 본문과 사례, 좁은 화면의 표 스크롤, 목차 링크, 이전 주소 이동을 확인합니다. PR에서는 검사를 실행하고, `main` 변경은 같은 검사를 통과한 뒤 GitHub Pages에 배포합니다.
