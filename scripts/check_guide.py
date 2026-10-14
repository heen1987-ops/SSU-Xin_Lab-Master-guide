"""공통 가이드 구조·기존 주소·로컬 링크 회귀 검사. Python 표준 라이브러리만 사용."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {'master.html':'index.html', '석사과정.html':'index.html',
           'phd.html':'requirements.html', '박사과정.html':'requirements.html',
           '실증논문가이드.html':'empirical.html', '실험논문가이드.html':'experiment.html'}
errors = []
checked = 0

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.headings = [], [], 0
        self.language = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'html': self.language = attrs.get('lang')
        if tag == 'h1': self.headings += 1
        for key in ('href', 'src'):
            if key in attrs: self.links.append(attrs[key])

pages = {}
for folder in ('docs', 'html'):
    for path in (ROOT / folder).glob('*.html'):
        text = path.read_text(encoding='utf-8')
        page = pages[path.resolve()] = Page(text)
        if page.language != 'ko': errors.append(f'{path}: lang=ko 누락')
        if page.headings != 1: errors.append(f'{path}: h1은 하나여야 함')
        for identifier, count in Counter(page.ids).items():
            if count > 1: errors.append(f'{path}: 중복 id {identifier}')
        if path.name in ALIASES:
            if f"location.replace('{ALIASES[path.name]}' + location.search + location.hash)" not in text:
                errors.append(f'{path}: 기존 주소 query/fragment 전달 누락')
        elif any(label in text for label in ('>과정 선택<','>석사과정 가이드<','>박사과정 가이드<')):
            errors.append(f'{path}: 학위별 활성 탐색 라벨 잔존')

for path, page in pages.items():
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc: continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        checked += 1
        if not target.exists(): errors.append(f'{path.name}: 대상 없음 {link}'); continue
        if target.suffix == '.html' and parsed.fragment:
            if target.name in ALIASES: target = target.with_name(ALIASES[target.name])
            if unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{path.name}: 앵커 없음 {link}')

for folder in ('docs', 'html'):
    home = pages[(ROOT/folder/'index.html').resolve()]
    for stage in ('stages','topic','literature','design','analysis','writing','defense','publication','roadmap'):
        if stage not in home.ids: errors.append(f'{folder}: 연구 단계 누락 {stage}')
    required_legacy = ('meaning','topic','method','guides','roadmap','exam','format','checklist','resources','more',
                       'wbs-gantt-root','semester-gantt-title','semester-gantt-hint')
    for anchor in required_legacy:
        if anchor not in home.ids: errors.append(f'{folder}: 옛 공통 앵커 누락 {anchor}')
    requirements = pages[(ROOT/folder/'requirements.html').resolve()]
    for anchor in ('diff','track','schedule','exam','record','quartile','review','format','open'):
        if anchor not in requirements.ids: errors.append(f'{folder}: 옛 요건 앵커 누락 {anchor}')
    workbench = pages[(ROOT/folder/'research-workbench.html').resolve()]
    for anchor in ('routing','problem','empirical','fulltext','handoff','workbook'):
        if anchor not in workbench.ids: errors.append(f'{folder}: 연구설계·근거검증 절 누락 {anchor}')

for path in (ROOT/'docs').rglob('*'):
    if path.is_file():
        other = ROOT/'html'/path.relative_to(ROOT/'docs')
        if not other.exists() or path.read_bytes() != other.read_bytes():
            errors.append(f'docs/html 불일치: {path.name}')

# Markdown과 웹 본문이 참조하는 저장소 파일의 존재를 확인한다.
for path in ROOT.rglob('*.md'):
    text = path.read_text(encoding='utf-8-sig')
    for link in re.findall(r'\]\(([^\s)]+)\)', text):
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or not parsed.path: continue
        checked += 1
        target = (path.parent/unquote(parsed.path)).resolve()
        if not target.exists(): errors.append(f'{path.name}: Markdown 대상 없음 {link}')
        elif target.suffix == '.html' and parsed.fragment:
            if target.name in ALIASES: target=target.with_name(ALIASES[target.name])
            if unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{path.name}: HTML 앵커 없음 {link}')

prefix = '/heen1987-ops/SSU-Xin_Lab-Master-guide/blob/main/'
for path, page in pages.items():
    for link in page.links:
        parsed = urlsplit(link)
        if parsed.netloc == 'github.com' and parsed.path.startswith(prefix):
            target = ROOT/unquote(parsed.path[len(prefix):])
            checked += 1
            if not target.exists(): errors.append(f'{path.name}: 저장소 참조 없음 {link}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'통과: HTML {len(pages)}개, 링크·자산 {checked}건, 단계·호환 앵커·docs/html 일치 확인')
