"""기존 감사 결함의 재발과 Markdown 목차 링크를 검사한다. 표준 라이브러리만 사용."""
from collections import Counter
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
REPO_PREFIX = '/heen1987-ops/SSU-Xin_Lab-Master-guide/blob/main/'
errors = []
fragments = 0

class VisibleText(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.parts, self.hidden = [], 0
        self.feed(value)
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('style', 'script'): self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def heading_ids(value):
    ids = set(re.findall(r'<a\s[^>]*id=[\"\x27]([^\"\x27]+)', value))
    counts = Counter()
    fenced = False
    for line in value.splitlines():
        if re.match(r'^\s*(```|~~~)', line):
            fenced = not fenced
            continue
        if fenced: continue
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match: continue
        title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', match[1])
        title = unescape(re.sub(r'<[^>]+>', '', title)).lower()
        slug = ''.join(c for c in title if c in ('-', '_', ' ') or unicodedata.category(c)[0] in ('L', 'N', 'M'))
        slug = slug.replace(' ', '-')
        index = counts[slug]
        counts[slug] += 1
        ids.add(f'{slug}-{index}' if index else slug)
    return ids

# 감사에서 발견한 잘못된 지침의 재등장을 막는 회귀 규칙이다.
# 새로운 모든 충돌의 의미 판정이나 외부 규정 검증을 대신하지 않는다.
FORBIDDEN = {
    '유사도 수치를 제출 승인으로 해석': r'2%로\s*제출\s*통과',
    '회의 녹음의 일괄 의무화': r'모두\s*녹음해\s*두세요',
    '인용 스타일을 연구방법으로 고정': r'(?:실증|실험)\s*트랙\s*기본(?:\s|\||$)',
    '학위만으로 관문 부재 단정': r'석사에는\s*없고\s*박사에만',
    '사례의 심사 승인 상태 과장': r'최근\s*통과\s*사례|실제\s*통과\s*논문',
    '원문 확인 범위 과장': r'석사\s*3편\s*정독',
    '구성요소 비교 방식의 일괄 강제': r'한\s*번에\s*하나만\s*바꿈',
    '심사 소요일을 확정 하한으로 간주': r'심사\s*기한의\s*하한',
}

markdowns = list(ROOT.glob('*.md'))
for directory in ('01_실증트랙_경영IS', '02_실험트랙_공학컴공', '12_단계별_지침_라이브러리', 'handbook', 'templates'):
    markdowns.extend((ROOT/directory).glob('*.md'))
markdowns.append(ROOT/'docs/assets/research-workbook.md')
cache = {p.resolve(): heading_ids(p.read_text(encoding='utf-8-sig')) for p in markdowns}

for p in markdowns:
    value = p.read_text(encoding='utf-8-sig')
    for description, pattern in FORBIDDEN.items():
        if re.search(pattern, value): errors.append(f'{p.relative_to(ROOT)}: {description}')
    for link in re.findall(r'\]\(([^\s)]+)\)', value):
        parsed = urlsplit(link)
        if not parsed.fragment: continue
        if parsed.netloc == 'github.com' and parsed.path.startswith(REPO_PREFIX):
            target = ROOT/unquote(parsed.path[len(REPO_PREFIX):])
        elif not parsed.scheme and not parsed.netloc:
            target = p.parent/unquote(parsed.path) if parsed.path else p
        else: continue
        if target.suffix != '.md': continue
        fragments += 1
        if unquote(parsed.fragment) not in cache.get(target.resolve(), set()):
            errors.append(f'{p.relative_to(ROOT)}: Markdown 앵커 없음 {link}')

for p in (ROOT/'docs').glob('*.html'):
    value = p.read_text(encoding='utf-8')
    visible = ' '.join(VisibleText(value).parts)
    for description, pattern in FORBIDDEN.items():
        if re.search(pattern, visible): errors.append(f'{p.relative_to(ROOT)}: {description}')
    for link in re.findall(r'href=[\"\x27]([^\"\x27]+)', value):
        parsed = urlsplit(unescape(link))
        if not parsed.fragment or parsed.netloc != 'github.com' or not parsed.path.startswith(REPO_PREFIX): continue
        target = ROOT/unquote(parsed.path[len(REPO_PREFIX):])
        if target.suffix != '.md': continue
        fragments += 1
        if unquote(parsed.fragment) not in cache.get(target.resolve(), set()):
            errors.append(f'{p.relative_to(ROOT)}: 저장소 Markdown 앵커 없음 {link}')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'통과: Markdown {len(markdowns)}개, 목차 참조 {fragments}건, 기존 결함 재발 규칙 {len(FORBIDDEN)}개')
