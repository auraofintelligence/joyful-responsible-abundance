"""Check the published pages, local assets and source anchors."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
from html import unescape
from collections import Counter
import json,re

ROOT=Path(__file__).resolve().parent
class Page(HTMLParser):
    def __init__(self,path):
        super().__init__();self.ids=[];self.links=[];self.images=[];self.h1=0
        self.feed(path.read_text(encoding='utf-8'))
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ('img','script') and 'src' in a:self.links.append(a['src'])
        if tag=='link' and 'href' in a:self.links.append(a['href'])
        if tag=='img':self.images.append(a)

pages={p.name:Page(p) for p in ROOT.glob('*.html')}
errors=[]
for name,p in pages.items():
    if p.h1!=1:errors.append((name,'heading count',p.h1))
    if len(set(p.ids))!=len(p.ids):errors.append((name,'duplicate IDs',[k for k,v in Counter(p.ids).items() if v>1]))
    for href in p.links:
        u=urlsplit(href)
        if u.scheme or u.netloc:continue
        path=unquote(u.path) or name
        if not (ROOT/path).is_file():errors.append((name,'missing file',href))
        elif u.fragment and path in pages and unquote(u.fragment) not in pages[path].ids:errors.append((name,'missing anchor',href))
    for img in p.images:
        if 'alt' not in img:errors.append((name,'missing alt',img))
    text=(ROOT/name).read_text(encoding='utf-8')
    if '{{' in text or 'C:/Users' in text or 'G:/Github' in text:errors.append((name,'unresolved or private text'))
    if '\u2014' in unescape(text):errors.append((name,'em dash found'))
source=json.loads((ROOT/'data/sovereignty.json').read_text(encoding='utf-8'))
full=(ROOT/'sovereignty-paper.html').read_text(encoding='utf-8')
plain=re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>','',full)))
for block in source['source_blocks'][3:]:
    t=re.sub(r'\s+',' ',block['text']).strip()
    if t and t not in plain:errors.append(('sovereignty-paper.html','missing source text',block['id']))
if errors:
    print(json.dumps(errors,ensure_ascii=False,indent=2));raise SystemExit(1)
print(f'Passed: {len(pages)} pages, all local links and source anchors, image descriptions and full sovereignty text.')
