"""Validate generated HTML, navigation, local links, anchors and bookmark redirects."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import unquote, urlsplit
import re
from build_site import ROOT, PAGES, ALIASES, FRAGMENTS

class Page(HTMLParser):
    def __init__(self,path):
        super().__init__();self.path=path;self.ids=[];self.links=[];self.h1=0;self.lang=None;self.mains=0;self.current=[]
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='h1':self.h1+=1
        if tag=='main':self.mains+=1
        if a.get('aria-current')=='page':self.current.append(a.get('href'))
        for attr in ('href','src'):
            if attr in a:self.links.append(a[attr])

pages={p.resolve():Page(p) for p in (ROOT/'docs').glob('*.html')};errors=[];links=0
for path,page in pages.items():
    if page.lang!='ko' or page.h1!=1 or page.mains!=1:errors.append(f'{path.name}: lang/h1/main invalid')
    if any(n>1 for n in Counter(page.ids).values()):errors.append(f'{path.name}: duplicate ids')
    if path.stem in PAGES and path.stem not in ('empirical','experiment') and page.current!=[path.name]:errors.append(f'{path.name}: current page navigation')
    for link in page.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=(path.parent/unquote(u.path)).resolve() if u.path else path
        if not target.is_relative_to((ROOT/'docs').resolve()) or not target.is_file():errors.append(f'{path.name}: missing local target {link}');continue
        links+=1
        if u.fragment and target.suffix=='.html' and unquote(u.fragment) not in pages[target].ids:errors.append(f'{path.name}: missing anchor {link}')
for slug,target in ALIASES.items():
    value=(ROOT/'docs'/f'{slug}.html').read_text(encoding='utf-8')
    if f'"{target}.html" + location.search + location.hash' not in value:errors.append(f'{slug}: query/hash lost')
for slug,mapping in FRAGMENTS.items():
    ids=pages[(ROOT/'docs'/f'{slug}.html').resolve()].ids
    for old,new in mapping.items():
        if new not in ids:errors.append(f'{slug}#{old}: missing redirect destination {new}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Passed: {len(pages)} HTML files, {links} local references, redirects and landmarks')
