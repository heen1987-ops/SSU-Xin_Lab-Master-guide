"""Build the static reading guide from content/*.md. No network access required."""
from pathlib import Path
from html import escape, unescape
from urllib.parse import urlsplit, urlunsplit
import argparse
import hashlib
import json
import re
import markdown

ROOT = Path(__file__).resolve().parents[1]
CSS_VERSION = hashlib.sha256((ROOT/'docs/assets/guide.css').read_text(encoding='utf-8').encode('utf-8')).hexdigest()[:12]
PAGES = {
    'index': '작성 과정', 'case-study': '초안 → 제출본', 'chapter-writing': '장별 작성', 'methods': '연구방법',
    'empirical': '설문·관찰 연구', 'experiment': '비교실험',
    'writing': '인용·표·그림', 'requirements': '학위·제출 요건', 'references': '참고자료',
}
PRIMARY = ['index', 'case-study', 'chapter-writing', 'methods', 'writing', 'requirements', 'references']
ALIASES = {
    'master': 'index', 'phd': 'index', '석사과정': 'index', '박사과정': 'index',
    '실증논문가이드': 'empirical', '실험논문가이드': 'experiment',
    'research-workbench': 'index', 'skill-workflow': 'index',
    'academic-coordinator': 'index',
}
# Preserve common bookmarks from the previous guide.
FRAGMENTS = {
    'index': {'overview':'start','roadmap':'topic','journey':'topic','process':'topic',
              'research-topic':'topic','problem':'topic','research-gap':'literature',
              'research-design':'design','data':'design','results':'analysis',
              'chapters':'writing','review':'defense','checklist':'defense',
              'submission':'defense','resources':'reading','tracks':'reading',
              'research-map':'topic','literature-matrix':'literature','claim-evidence':'analysis',
              'risk-register':'design','chapter-map':'writing','review-response':'defense',
              'research-brief':'topic','download':'reading'},
    'empirical': {'overview':'main','structure':'analysis','design-workbench':'sampling','theory':'measurement',
                  'measure':'measurement','cases':'reporting','citation':'reporting','resources':'checklist',
                  'm1':'measurement','m2':'measurement','m3':'sampling','m4':'analysis','m5':'reporting','m6':'checklist','more':'checklist'},
    'experiment': {'overview':'main','structure':'method','methodpack':'comparison','audit':'results',
                  'cases':'case','citation':'method','resources':'case','checklist':'results',
                  'e1':'claims','e2':'comparison','e3':'method','e4':'results','e5':'results','e6':'case','more':'case'},
    'requirements': {'diff':'degree','track':'degree','schedule':'preparation','exam':'degree',
                     'exam-common':'degree','record':'degree','quartile':'degree','review':'degree','open':'submission'},
}
FRAGMENTS['index'].update({'stages':'start','meaning':'start','method':'design','guides':'reading',
    'publication':'defense','exam':'defense','format':'writing','more':'reading',
    'routing':'design','empirical':'design','fulltext':'literature','handoff':'writing','workbook':'reading',
    'semester-gantt-hint':'topic','semester-gantt-title':'topic','wbs-gantt-root':'topic',
    **{f'gantt-semester-{n}':'topic' for n in range(1,5)},
    **{f'gantt-task-{n}':'topic' for n in range(1,7)},
    **{f'c{n}':'defense' for n in range(1,10)}})
for mapping in FRAGMENTS.values():
    mapping.update({'main-content':'main','navlinks':'main','theme-toggle':'main'})

def convert_links(body):
    def replace(m):
        value=unescape(m.group(1)); u=urlsplit(value)
        if not u.scheme and not u.netloc and u.path.endswith('.md'):
            value=urlunsplit(('', '', u.path[:-3]+'.html', u.query, u.fragment))
        return 'href="'+escape(value, quote=True)+'"'
    return re.sub(r'href="([^"]+)"',replace,body)

def render_page(slug):
    source=(ROOT/'content'/f'{slug}.md').read_text(encoding='utf-8')
    title=source.splitlines()[0].removeprefix('# ')
    md=markdown.Markdown(extensions=['tables','attr_list','toc'],extension_configs={'toc':{'toc_depth':'2-2'}})
    body=convert_links(md.convert(source))
    body=re.sub(r'<table>(.*?)</table>',r'<div class="table-scroll" role="region" aria-label="가로로 읽을 수 있는 표" tabindex="0"><table>\1</table></div>',body,flags=re.S)
    # Scope header cells to make the reading order explicit for assistive technology.
    body=body.replace('<th>', '<th scope="col">').replace('<th style=', '<th scope="col" style=')
    nav=''.join(f'<a href="{s}.html"'+(' aria-current="page"' if s==slug else '')+f'>{PAGES[s]}</a>' for s in PRIMARY)
    if slug in ('empirical','experiment'):
        body='<p class="breadcrumb"><a href="methods.html">연구방법</a> / '+PAGES[slug]+'</p>'+body
    description=source.split('\n\n')[1]
    description=re.sub(r'\*|\[|\]|\([^)]*\)', '', description)[:150]
    mapping=json.dumps(FRAGMENTS.get(slug,{}),ensure_ascii=False)
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description,quote=True)}">
<meta name="source" content="content/{slug}.md">
<title>{escape(title)} · Xin Lab</title>
<link rel="stylesheet" href="assets/guide.css?v={CSS_VERSION}">
</head>
<body>
<a class="skip-link" href="#main">본문으로 건너뛰기</a>
<header><div class="header-inner"><a class="brand" href="index.html">Xin Lab <span>논문 작성 가이드</span></a><nav aria-label="전체 안내">{nav}</nav></div></header>
<div class="layout">
<aside><nav aria-label="이 페이지의 목차"><p>이 페이지에서</p>{md.toc}</nav></aside>
<main id="main"><p class="eyebrow">석사·박사 공통 안내</p><details class="mobile-toc"><summary>이 페이지의 목차</summary>{md.toc}</details><article>{body}</article>
<div class="page-end"><a href="index.html">작성 과정</a><a href="#main">맨 위로 ↑</a></div></main>
</div>
<footer>Xin Lab · 질문과 근거를 연결하는 논문 작성 안내</footer>
<script>
const legacy = {mapping};
let fragment; try {{ fragment = decodeURIComponent(location.hash.slice(1)); }} catch {{ fragment = ''; }}
if (legacy[fragment]) {{ location.replace(location.pathname + location.search + '#' + legacy[fragment]); }}
</script>
</body>
</html>
'''

def render_alias(slug,target):
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>논문 작성 가이드로 이동</title><link rel="stylesheet" href="assets/guide.css?v={CSS_VERSION}"></head>
<body><main class="redirect"><h1>논문 작성 가이드</h1><p><a href="{target}.html">{PAGES[target]} 읽기</a></p></main>
<script>location.replace({json.dumps(target+'.html')} + location.search + location.hash);</script></body></html>
'''

def outputs():
    return {**{s+'.html':render_page(s) for s in PAGES},**{s+'.html':render_alias(s,t) for s,t in ALIASES.items()}}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected=outputs(); errors=[]
    for name,value in expected.items():
        path=ROOT/'docs'/name
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8')!=value: errors.append(name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding='utf-8',newline='\n')
    stale={p.name for p in (ROOT/'docs').glob('*.html')}-expected.keys()
    if errors or stale: raise SystemExit(f'Generated HTML differs: {errors}; unexpected files: {sorted(stale)}')
    print(f'{"Checked" if args.check else "Built"} {len(PAGES)} pages and {len(ALIASES)} redirects')

if __name__=='__main__': main()
