"""Check source links and known misleading guidance; not a semantic research review."""
from urllib.parse import unquote, urlsplit
from pathlib import Path
import re
import markdown
from build_site import ROOT, PAGES

FORBIDDEN={
    '유사도 수치를 제출 승인으로 해석':r'2%로\s*제출\s*통과',
    '회의 녹음의 일괄 의무화':r'모두\s*녹음해\s*두세요',
    '인용 스타일을 연구방법으로 고정':r'(?:실증|실험)\s*트랙\s*기본(?:\s|\||$)',
    '학위만으로 관문 부재 단정':r'석사에는\s*없고\s*박사에만',
    '사례의 심사 승인 상태 과장':r'최근\s*통과\s*사례|실제\s*통과\s*논문',
    '원문 확인 범위 과장':r'석사\s*3편\s*정독',
    '구성요소 비교 방식의 일괄 강제':r'한\s*번에\s*하나만\s*바꿈',
    '심사 소요일을 확정 하한으로 간주':r'심사\s*기한의\s*하한',
    '운영·도구 사용법 재유입':r'학술총무|스킬\s*사용법|\$ssu-paper|/ssu-paper',
    '개인 보관 경로 노출':r'[CGN]:[/\\]|내 드라이브|codex@localhost',
}
sources={p.resolve():p.read_text(encoding='utf-8') for p in (ROOT/'content').glob('*.md')}
ids={p:set(re.findall(r'id="([^"]+)"',markdown.markdown(s,extensions=['toc','attr_list','tables']))) for p,s in sources.items()}
errors=[];links=0
if {p.stem for p in sources}!=set(PAGES):errors.append('Unlisted or missing source page')
for path,value in sources.items():
    for label,pattern in FORBIDDEN.items():
        if re.search(pattern,value):errors.append(f'{path.name}: {label}')
    for link in re.findall(r'\]\(([^\s)]+)\)',value):
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        links+=1
        if target not in sources:errors.append(f'{path.name}: missing source {link}')
        elif u.fragment and unquote(u.fragment) not in ids[target]:errors.append(f'{path.name}: missing source anchor {link}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Passed: {len(sources)} source pages, {links} source references, {len(FORBIDDEN)} content regression rules')
