"""Build the static reading site from the two supplied papers."""
from pathlib import Path
from html import escape as esc
import json
import re
import shutil
from datetime import date

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
PREVIEW = json.loads((DATA / 'preview.json').read_text(encoding='utf-8'))
SOVEREIGNTY = json.loads((DATA / 'sovereignty.json').read_text(encoding='utf-8'))
BASE = 'https://auraofintelligence.github.io/joyful-responsible-abundance/'
REPO = 'https://github.com/auraofintelligence/joyful-responsible-abundance'
TITLE = 'Joyful Responsible Abundance'
PAGES = []
PARTS = {
 1: ('people.html', 'People and practice', 'Start with a person', 'How a personal Aura, practical learning and continuity of care can help people carry their experience through life.', 'community-hero'),
 2: ('capacity.html', 'Shared capacity and ownership', 'Make room to participate', 'Healthy living, time, useful work and locally owned computing give more people the means to act.', 'local-compute'),
 3: ('civic.html', 'Evidence and public decisions', 'Turn a concern into a decision', 'Follow a household bill, a legal question or a local problem through evidence, responsibility and a public response.', 'amity-jetty'),
 4: ('world.html', 'Cooperation across the world', 'Let local learning travel', 'Connect personal growth, AI alignment, peaceful cooperation and the proposed global festival in July 2035.', 'global-festival')
}
LINKS = PREVIEW['links']
HERO_IMAGES = {
 'choice-hero': ('People consider an imagined coastal city, with a large computing precinct beyond a community workshop and garden.', 'An imagined future, with choices still open. AI-generated concept image.'),
 'community-hero': ('People learn and tend plants in an imagined Australian coastal commons.', 'An imagined coastal learning commons. AI-generated concept image.'),
 'local-compute': ('People learn beside a secure computing cabinet in an imagined community workshop.', 'An imagined community computing workshop. AI-generated concept image.'),
 'global-festival': ('People gather for music, art and conversation in an imagined coastal festival.', 'An imagined setting for the proposed 2035 global festival. AI-generated concept image.'),
 'amity-jetty': ('People on the jetty at Amity Point, Minjerribah, beneath a sunset.', 'Amity Point, Minjerribah. Photograph by Pacificwizard, CC0.')
}

def link(label, href, cls=''):
    return f'<a href="{esc(href, quote=True)}"'+(f' class="{cls}"' if cls else '')+f'>{esc(label)}</a>'

def rich(text):
    result=[]
    for token in re.split(r'(\{\{[^}]+\}\}|\*\*[^*]+\*\*|\*[^*]+\*)',text):
        if token.startswith('{{'):
            key,label=token[2:-2].split('|',1)
            href='civic.html#bills' if key=='@bills' else LINKS[key]
            result.append(link(label,href))
        elif token.startswith('**'):
            result.append('<strong>'+esc(token[2:-2])+'</strong>')
        elif token.startswith('*'):
            result.append('<em>'+esc(token[1:-1])+'</em>')
        else:
            result.append(esc(token))
    return ''.join(result)

def prose(text):
    out=[]
    listed=False
    for block in text.split('\n\n'):
        m=re.match(r'^\d+\.\s+(.*)',block,re.S)
        if m:
            if not listed: out.append('<ol>');listed=True
            out.append('<li>'+rich(m.group(1))+'</li>')
        else:
            if listed: out.append('</ol>');listed=False
            out.append('<p>'+rich(block)+'</p>')
    if listed: out.append('</ol>')
    return ''.join(out)

def figure(name,alt,caption,cls='media-wide',photo=False):
    width,height=(960,720) if name=='point-lookout' else (1536,1152) if name=='amity-jetty' else (1536,1024)
    loading='fetchpriority="high"' if cls=='hero-art' else 'loading="lazy"'
    return f'<figure class="{cls}"><img src="assets/images/{name}-1536.webp" srcset="assets/images/{name}-768.webp 768w, assets/images/{name}-1536.webp {width}w" sizes="(max-width: 760px) 100vw, 80vw" width="{width}" height="{height}" {loading} decoding="async" alt="{esc(alt,quote=True)}"><figcaption>{caption}</figcaption></figure>'

def hero_media(name):
    alt,caption=HERO_IMAGES[name]
    height=864 if name=='choice-hero' else 1152 if name=='amity-jetty' else 1024
    return f'<div class="hero-media"><img src="assets/images/{name}-1536.webp" srcset="assets/images/{name}-768.webp 768w, assets/images/{name}-1536.webp 1536w" sizes="100vw" width="1536" height="{height}" fetchpriority="high" decoding="async" alt="{esc(alt,quote=True)}"></div><div class="hero-shade" aria-hidden="true"></div>'

def hero_caption(name):
    return '<div class="hero-caption wrap"><p>'+HERO_IMAGES[name][1]+' <a href="about.html#images">Image credits</a></p></div>'

def page_head(kicker,title,deck,image=None):
    content=f'<div class="breadcrumb">{link("Home","index.html")} <span aria-hidden="true">/</span> {esc(kicker)}</div><p class="eyebrow">{esc(kicker)}</p><h1>{esc(title)}</h1><p class="lede">{deck}</p>'
    if image:
        return f'<header class="page-head page-hero">{hero_media(image)}<div class="wrap hero-content">{content}</div>{hero_caption(image)}</header>'
    return f'<header class="page-head wrap">{content}</header>'

def reading(sections,top=''):
    toc=''.join(f'<li>{link(t,"#"+i)}</li>' for i,t,c in sections)
    body=''.join(f'<section class="chapter" id="{i}"><h2>{esc(t)}</h2>{c}</section>' for i,t,c in sections)
    return f'{top}<div class="reading-layout wrap"><aside class="on-this-page"><details open><summary>On this page</summary><ol>{toc}</ol></details></aside><article class="prose">{body}</article></div>'

def nextlinks(index):
    def destination(page,direction,cls,relation=''):
        rel=f' rel="{relation}"' if relation else ''
        return f'<a class="{cls}" href="{page["file"]}"{rel}><span class="page-direction">{direction}</span><span class="page-title">{esc(page["title"])}</span></a>'
    previous=destination(PAGES[index-1],'← Previous','page-prev','prev') if index else destination(PAGES[-1],'Choose a path','page-prev')
    following=destination(PAGES[index+1],'Next →','page-next','next') if index<len(PAGES)-1 else destination({'file':'index.html','title':'Home'},'Back to the beginning →','page-next')
    directory=link('Site map','site-map.html') if 0<index<len(PAGES)-1 else ''
    position=f'<div class="page-position"><span>Page {index+1} of {len(PAGES)}</span>{directory}</div>'
    return '<nav id="page-navigation" class="page-nav wrap" aria-label="Previous and next pages">'+previous+position+following+'</nav>'

def write_page(filename,title,description,body,image='choice-hero',category='Guide'):
    PAGES.append(dict(file=filename,title=title,description=description,category=category))
    primary=[('start-here.html','Start here'),('explore.html','Explore the plan'),('sovereignty.html','Superintelligence'),('tools.html','Try the tools'),('library.html','Library')]
    nav=''.join(link(t,f, 'active' if f==filename else '') for f,t in primary)
    menu_primary=''.join(link(t,f) for f,t in primary)
    canonical=BASE+('' if filename=='index.html' else filename)
    schema=json.dumps({'@context':'https://schema.org','@type':'WebPage','name':title,'description':description,'url':canonical,'inLanguage':'en-AU','author':{'@type':'Person','name':'Luke Nathan Hayes'},'isPartOf':{'@type':'WebSite','name':TITLE,'url':BASE}},ensure_ascii=False)
    html=f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | {TITLE}</title><meta name="description" content="{esc(description,quote=True)}"><meta name="theme-color" content="#0b1116"><link rel="canonical" href="{canonical}"><link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="icon" href="favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="assets/apple-touch-icon.png"><link rel="manifest" href="site.webmanifest"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title,quote=True)}"><meta property="og:description" content="{esc(description,quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{BASE}assets/images/{image}-1536.webp"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script><script type="application/ld+json">{schema}</script></head>
<body id="top"><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="wrap"><a class="brand" href="index.html" aria-label="Joyful Responsible Abundance home"><img class="brand-mark" src="favicon.svg" width="42" height="42" alt=""><span class="brand-words">Joyful Responsible<br>Abundance</span></a><nav class="main-nav" aria-label="Main navigation">{nav}<details class="nav-menu"><summary>All pages</summary><div>{menu_primary}{link('Site map','site-map.html')}{link('Project directory','projects.html')}{link('Words explained','glossary.html')}{link('About and image credits','about.html')}{link('Complete sovereignty paper','sovereignty-paper.html')}</div></details></nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><!-- page-navigation --><div class="wrap footer-grid"><div><p class="eyebrow">An invitation to understand and participate</p><h2>More people with the means to act.</h2><p>Ideas, proposals and public tools by Luke Nathan Hayes.<br>Minjerribah on Quandamooka Country, Australia.</p></div><nav aria-label="Footer">{link('All pages','site-map.html')}{link('References and documents','library.html')}{link('Related projects','projects.html')}{link('Source repository',REPO)}{link('About and image credits','about.html')}{link('Public Source licence','LICENCE.md')}</nav></div><div class="wrap footer-note"><p>Reading edition · 5 November 2026 · Australian English. The papers distinguish working tools, proposed programmes and conditional future scenarios.</p><a href="#top" class="back-top">Back to top ↑</a></div></footer></body></html>'''
    (ROOT/filename).write_text(html,encoding='utf-8')

home='<section class="hero hero-home">'+hero_media('choice-hero')+'''<div class="wrap hero-content"><p class="eyebrow">Joyful Responsible Abundance · A whole-system proposal</p><h1>Our future is<br><span>still a choice.</span></h1><p class="hero-intro">Powerful intelligence is being built into the world. The choices we make now can spread its benefits, deepen dependence, or open new ways to live.</p><p class="hero-detail">Who owns it, who directs it and who has the means to take part will shape what comes next.</p><div class="actions"><a class="button" href="start-here.html">Explore the alternative <span aria-hidden="true">↗</span></a><a class="button secondary" href="sovereignty.html">Understand what is at stake</a></div></div>'''+hero_caption('choice-hero')+'''</section>
<section class="choice-section wrap"><div class="section-heading"><p class="eyebrow">Between the world we inherit and the world we build</p><h2>The balance takes work.</h2><p>More powerful technology does not settle how we live together. Ownership, health, time and public decisions influence whether people gain room to act or find their choices narrowing.</p></div><div class="choice-grid"><article class="choice-pressure"><p class="eyebrow">The pressure of the status quo</p><h3>Decisions made around us.</h3><p>People can depend on systems they have little time, information or authority to question.</p><ul><li>Essential tools and services can be controlled elsewhere, with little practical room to change provider or challenge the rules.</li><li>Poor health, confusing bills and financial strain can consume the time and energy needed to participate.</li><li>Claims can travel further than the evidence, while responsibility for a decision becomes difficult to trace.</li></ul><a href="sovereignty.html">Follow the questions of power and authority →</a></article><article class="choice-possibility"><p class="eyebrow">The alternative we can practise</p><h3>People equipped to decide.</h3><p>The proposal connects the conditions for a good life with the capacity to shape shared decisions.</p><ul><li>Shared computing, local skills and locally made or appropriately licensed open-source AI models can give communities more options.</li><li>Health, learning, continuity of care and clearer household bills can make more room for people to act.</li><li>Inspectable evidence, public responsibility and records of correction can make decisions easier to understand and challenge.</li></ul><a href="explore.html">Meet the components of the plan →</a></article></div><div class="choice-bridge"><p>Joyful Responsible Abundance is a direction to choose and keep working towards. It takes institutions, infrastructure and everyday practice, with room to disagree, test an idea and change course.</p><div class="choice-axis"><span>Understand the forces</span><span>Build shared capability</span><span>Practise the choice</span></div></div></section>
<section class="wrap intro-grid"><div><p class="eyebrow">A wake-up call with somewhere to go</p><h2>From everyday pressures to decisions on a world scale.</h2></div><div><p>A confusing electricity bill is a small encounter with a much larger question: can you understand a system well enough to question how it treats you? <a href="civic.html#bills">Household Bill Check</a> begins there. The wider plan connects personal learning, health, useful work, public evidence and shared computing.</p><p>The same question reaches into AI research, factories, public services and connected machines. Who can inspect them, correct them and direct what they do? Who shares in the gains when they become more productive?</p><p>This site brings together two papers by Luke Nathan Hayes. The <a href="explore.html">whole-system preview</a> introduces the capacities people need to build lives they can choose. The <a href="sovereignty.html">sovereignty paper</a> follows the race to build powerful intelligence and the authority that comes with it. Together they connect personal agency with choices facing Australia and the world.</p></div></section>
<section class="wrap"><div class="section-heading"><p class="eyebrow">Follow the connections</p><h2>Start close to home. Keep the whole world in view.</h2></div><div class="path-list">'''
for number,(file,title,kicker,deck,img) in PARTS.items():
    home+=f'<article><span class="path-number">0{number}</span><div class="path-copy"><h3>{link(kicker,file)}</h3><p>{esc(deck)}</p></div>{link("Explore →",file)}</article>'
home+='''</div></section><section class="feature-strip"><div class="wrap split-feature"><div><p class="eyebrow">The sovereignty question</p><h2>Australians need more than access to someone else’s intelligence.</h2><p>Access is useful. Authority also matters. The sovereignty paper follows the connections between money, chips, electricity, manufacturing, software and decisions, asking which capabilities Australia can build, own and govern.</p><a class="button" href="sovereignty.html">Understand the race</a></div><div><p class="eyebrow">Two distinct planning scales</p><h3>Australia: 3,000 locations.<br>A$18–19 billion.</h3><p>The global comparison describes 44,000 locations at A$264 billion. These are separate planning scenarios for shared computing, with locally made and appropriately licensed open-source models among the choices it could support.</p><p>Change the number of installations or the allowance per site to see what drives the total.</p><a href="tools.html#compute">Explore both scales in the calculator →</a></div></div></section>'''
home+='<section class="wrap split-feature"><div><p class="eyebrow">A place to begin</p><h2>Rooted in Minjerribah. Open to the world.</h2><p>A coastal community has its own seasons, meeting places, transport constraints and ways of sharing knowledge. The plan begins with that texture of ordinary life, then asks how communities can exchange what they learn while keeping authority over their own choices.</p><p>The photographs on this site show real places. The concept images imagine possible settings for the proposals.</p><a href="about.html">Meet the work and its sources →</a></div>'+figure('amity-jetty','People on Amity Point jetty beneath a sunset on North Stradbroke Island.','Amity Point, Minjerribah. Photograph by Pacificwizard, CC0. <a href="about.html#images">Image credits</a>.')+'</section>'
write_page('index.html','Our future is still a choice','An educational guide to choosing joyful responsible abundance, from everyday agency and shared computing to superintelligence and Australian sovereignty.',home)

sections=[
('the-question','The question behind both papers','<p>Imagine your local library could lend more than books. It could give people access to powerful computers, help them learn to use AI, and offer a place to work on local questions. Now add tools that let a person keep their own learning, check a bill, trace a public claim and share useful findings on their own terms.</p><p>The whole-system proposal asks what people need to build lives they can choose. The sovereignty paper follows who is building the larger machinery, who holds authority and how Australia can keep room to act. Read together, they make ownership, health, time and public evidence practical choices at personal, local, national and global scales.</p>'),
('three-words','What joyful responsible abundance means','<p><strong>Joyful</strong> asks whether life becomes more worth living, with room for relationships, discovery, creativity, rest and belonging. <strong>Responsible</strong> asks who decides, who bears the consequences and how mistakes can be corrected. <strong>Abundance</strong> asks whether useful capabilities become more available and more widely shared.</p><p>Held together, these words give people questions they can apply to a real decision. A quicker service may save time. It also matters whose time it saves, who can access it and what happens when it makes a mistake.</p>'),
('connection','How the pieces work together','<p>Start with someone who needs a safer route into a community hall. Their personal record can hold the photographs and what they tried. A public workbench can help find the responsible institution. Shared computing can support a map or a drainage model. A community record can show what work was contributed and whether the repair happened.</p><p>The person gains a skill. The community gains an account it can check. Another town can try the method and improve it. That repeated process connects individual learning with public capability.</p><p><a href="tools.html#connections">Explore the connection tree</a> or follow the <a href="civic.html#combined">worked example from notice to repair</a>.</p>'),
('urgency','Why this deserves attention now','<p>The sovereignty paper examines a race involving AI models, chips, electricity, finance, factories, robotics and ambitions in orbit. Its central concern is that decisions made during construction can shape who owns the resulting capability and who can direct it later.</p><p>A household can change an appliance more easily than a country can replace an energy system. Similar differences appear when a public service depends on proprietary software, contracts, technical skills and data arrangements built up over many years. Understanding those dependencies while choices remain open is part of sovereignty.</p><p><a href="sovereignty.html">Read the introduction to the race</a>. The complete paper keeps reported figures, company targets and the author’s conditional scenarios in view.</p>'),
('read','Choose a way through','<p>For the human side, begin with <a href="people.html">people and practice</a>, then move to <a href="capacity.html">shared capacity</a>, <a href="civic.html">public decisions</a> and <a href="world.html">global cooperation</a>. For the larger forces, begin with <a href="sovereignty.html">superintelligence and sovereignty</a>.</p><p>Use <a href="glossary.html">Words explained</a> whenever a term is unfamiliar. The <a href="library.html">library</a> links the source papers and references. The <a href="projects.html">project directory</a> leads to public tools, sites and repositories you can inspect.</p>')]
write_page('start-here.html','A first look at the whole system','Begin with the human question, learn the three principles, and connect everyday problems with the AI race.',page_head('Start here','A first look at the whole system','A guided introduction for people meeting these ideas for the first time.')+reading(sections))

explore=page_head('Explore','One system, many ways in','Follow the sequence, or begin with a question that matters in your life.')+'<div class="wrap path-list">'
for n,(file,title,kicker,deck,img) in PARTS.items():
    subs=''.join('<li>'+link(p['title'],file+'#'+p['id'])+'</li>' for p in PREVIEW['pages'] if p['part']==n)
    explore+=f'<article><span class="path-number">0{n}</span><div class="path-copy"><h2>{link(title,file)}</h2><p>{esc(deck)}</p><ul>{subs}</ul></div></article>'
explore+='</div>'
write_page('explore.html','Explore the whole system','Every component of the whole-system proposal, with direct links to its explanation and public projects.',explore)

for n,(file,title,kicker,deck,img) in PARTS.items():
    sections=[]
    for p in PREVIEW['pages']:
        if p['part']!=n:continue
        content=prose(p['text'])
        if p['id']=='build': content+='<p class="source-note"><a href="tools.html#compute">Change the site count and cost in the calculator</a>.</p>'
        if p['id']=='gajra': content+='<p class="source-note">The festival and world-vote proposals are described in the <a href="'+LINKS['alignmentpaper']+'">human and SI alignment paper, page 25</a>, and the <a href="'+LINKS['ungapdf']+'">UNGA81 contribution, page 7</a>.</p>'
        if p['id']=='verse': content+=figure('community-hero','An imagined coastal learning commons with a small group sharing a table.','Concept image of shared learning. AI-generated; the Verse Box remains a proposed trial.')
        if p['id']=='compute': content+=figure('local-compute','People learning beside a rack of computers in an imagined Australian community workshop.','An imagined community computing and learning space. AI-generated concept image.')
        if p['id']=='gajra': content+=figure('global-festival','An imagined global festival with music, art and people gathering beside the sea.','An imagined setting for the proposed July 2035 global festival. AI-generated concept image; a venue has not been selected in these papers.')
        sections.append((p['id'],p['title'],content))
    write_page(file,title,deck,page_head('The whole-system proposal',title,deck,img)+reading(sections),img or 'choice-hero')

chapters=SOVEREIGNTY['chapters']
sovereignty=page_head('Superintelligence and Australia','The race is also about who holds authority','A guide to the forces behind the AI race, and the choices Australia can make while its next layer of infrastructure is being built.','choice-hero')+'<section class="wrap intro-grid"><div><p class="eyebrow">Start with the words</p><h2>Intelligence needs a physical world to work in.</h2></div><div><p>An AI model is learned software. It runs on computers that need chips, power, cooling and communications. More capable systems also depend on people, investment, factories and the rules that govern access and use.</p><p><strong>Superintelligence</strong> describes a possible level of AI that exceeds human capability across many areas. The paper explores how progress towards that level could interact with industry, robotics and political authority. Its future figures are conditional scenarios, explained through their assumptions.</p><p><strong>Sovereignty</strong> asks who has effective authority. For a connected system, that includes who controls updates, permissions, data, maintenance and the power to pause or stop it.</p></div></section>'
sovereignty+=figure('local-compute','An imagined local computing workshop with people discussing how the equipment works.','AI-generated concept image. A local installation makes one part of the larger infrastructure question tangible.','media-wide wrap')+'<section class="wrap path-list">'
for i,ch in enumerate(chapters,1):
    file='sovereignty-'+ch['slug']+'.html'
    sovereignty+=f'<article><span class="path-number">{i:02}</span><div class="path-copy"><h2>{link(ch["title"],file)}</h2><p>{esc(ch["deck"])}</p></div></article>'
sovereignty+='</section><section class="feature-strip"><div class="wrap"><h2>Follow the claims back to their evidence.</h2><p>The source paper is dated 5 November 2026. Corporate dollar amounts are US dollars unless marked Australian dollars. Reported measurements, company ambitions and scenario calculations have different meanings.</p><div class="actions"><a class="button" href="sovereignty-paper.html">Read the complete paper</a><a class="button secondary" href="documents/superintelligence-and-australian-sovereignty.docx">Download the reviewed Word edition</a></div></div></section>'
write_page('sovereignty.html','Superintelligence and Australian sovereignty','Understand the race over AI, industrial capability and authority, then explore Australia’s practical choices.',sovereignty,'local-compute','Sovereignty')

for i,ch in enumerate(chapters):
    sections=[]
    for j,section in enumerate(ch['sections']):
        body=section.get('html') or ''.join('<p>'+rich(p)+'</p>' for p in section.get('paragraphs',[]))
        sections.append((section.get('id',f'section-{j+1}'),section['title'],body))
    content=page_head('The sovereignty question',ch['title'],esc(ch['deck']))+reading(sections)
    content+='<div class="wrap prose"><p class="source-note">Adapted from the reviewed sovereignty paper dated 5 November 2026. <a href="sovereignty-paper.html">Read the full argument, dated sources and calculation method</a>.</p></div>'
    write_page('sovereignty-'+ch['slug']+'.html',ch['title'],ch['deck'],content,'local-compute','Sovereignty')

def source_html(block):
    text=block['text']; matches=[]; end=0
    for item in block.get('links',[]):
        label=item['text']; target=item.get('target')
        if not target or not label:continue
        pos=text.find(label,end)
        if pos<0:pos=text.find(label)
        if pos>=0 and not any(a<=pos<b for a,b,c in matches):
            matches.append((pos,pos+len(label),link(label,target)));end=pos+len(label)
    out=[];position=0
    for a,b,c in sorted(matches):out.extend([esc(text[position:a]),c]);position=b
    out.append(esc(text[position:]))
    return ''.join(out)

source_sections=[];current=None
for b in SOVEREIGNTY['source_blocks']:
    if not b['text'].strip():continue
    if b['style']=='Heading 1':
        current=[b['id'],b['text'],''];source_sections.append(current)
    elif current:
        tag='h3' if b['style'].startswith('Heading') else 'p'
        current[2]+=f'<{tag} id="{b["id"]}">{source_html(b)}</{tag}>'
fullintro='<div class="wrap prose"><p>This complete reading edition preserves the reviewed paper’s argument and linked references. Evidence is dated 5 November 2026. Corporate amounts are in US dollars unless Australian dollars are specified. Company targets and the paper’s conditional scenarios retain their attribution.</p><p>The paper uses “open-source” in describing an Aura direction. Each public project’s own licence specifies the actual reuse permissions, including the Public Source terms used by several linked repositories.</p><p><a href="documents/superintelligence-and-australian-sovereignty.docx">Download the original reviewed Word document</a> · <a href="sovereignty.html">Return to the introductory guide</a></p></div>'
write_page('sovereignty-paper.html','The complete sovereignty paper','The full reviewed paper with dated references and the method behind its conditional scenarios.',page_head('Complete reading edition','The Super Intelligence race and Australian sovereignty','Prepared for Luke Nathan Hayes · reviewed edition · 5 November 2026')+reading(source_sections,fullintro),'local-compute','Source')

tools=page_head('Learn by exploring','Change an assumption. Follow a connection.','Two ways to make the scale and structure of the proposal easier to understand.')+'''<div class="wrap"><section id="compute" class="tool-panel"><p class="eyebrow">The cost of shared computing</p><h2>How large is the proposed investment?</h2><p>The Australian plan starts with 3,000 sites and an initial allowance of A$6 million per site. Multiplying those gives A$18 billion, within the stated A$18–19 billion planning range. The global comparison uses 44,000 sites at the same allowance, giving A$264 billion.</p><form id="compute-calculator"><div class="preset-buttons"><button type="button" data-sites="3000" data-cost="6">Australian scenario</button><button type="button" data-sites="44000" data-cost="6">Global scenario</button><button type="button" data-sites="10" data-cost="6">Ten-site example</button></div><div class="control-grid"><label for="site-count">Number of sites<input id="site-count" name="sites" type="number" min="1" max="1000000" step="1" value="3000" required></label><label for="site-cost">Initial allowance per site, A$ million<input id="site-cost" name="cost" type="number" min="0.01" max="1000" step="0.01" value="6" required></label></div><div class="calculator-result" aria-live="polite" aria-atomic="true"><p>Initial capital estimate</p><output id="compute-total">A$18 billion</output><p id="compute-detail">3,000 sites × A$6 million per site</p></div><p class="error" id="compute-error" role="alert"></p></form><noscript><p>The calculator needs JavaScript for changes. The Australian base calculation is 3,000 × A$6 million = A$18 billion. The global comparison is 44,000 × A$6 million = A$264 billion.</p></noscript><p>The allowance covers an initial installation and support package. Running costs, staff, electricity, maintenance and replacement need continuing budgets. These are planning scenarios, and actual site costs need engineering and procurement work.</p><p><a href="capacity.html#build">Read the assumptions and ownership model</a> · <a href="'''+LINKS['middlepdf']+'''">Read Installing the Missing Middle</a></p></section>
<section class="tool-panel" id="connections"><p class="eyebrow">How the parts reinforce one another</p><h2>Follow the connection tree</h2><p>Choose a branch to see a role in the system. The branches meet again when people work on a shared problem.</p><div class="connection-map"><div class="tree-root">People with the means to understand, choose and act</div><div class="tree-branches">'''
nodes=[('person','A person learns','people.html','An Aura holds chosen context, corrections and learning. A Verse Box offers a supported first encounter. Genesis explores how that record grows through practice.'),('conditions','Daily life makes room','capacity.html#conditions','Healthy De-Slop and household bill de-slop aim to reduce avoidable strain. Time, health and clearer information help people take part.'),('compute','A community has capacity','capacity.html#compute','Shared computers provide access to tools that exceed an individual device. Local skills, ownership and locally made or open-source models are part of the sovereignty question.'),('evidence','A concern becomes evidence','civic.html','Bill Check, Luke’s Relevance and the Legal Engine help organise a question and trace supporting material. P4A connects it with public responsibilities and decisions.'),('world','Learning travels','world.html','Communities share methods they choose to share, compare results and correct errors. GAJRA Earth connects this work with global alignment conversations and peaceful cooperation.')]
for i,(key,title,href,text) in enumerate(nodes):tools+=f'<button type="button" data-node="{key}" aria-controls="node-{key}" aria-pressed="false">{esc(title)}</button>'
tools+='</div></div>'
for key,title,href,text in nodes:tools+=f'<section class="node-detail" id="node-{key}"><h3>{esc(title)}</h3><p>{esc(text)}</p>{link("Read this part →",href)}</section>'
tools+='''<p class="source-note">A worked route connects all five branches in <a href="civic.html#combined">Following one problem from notice to repair</a>. Each component has its own stage of development and evidence needs.</p></section>
<section class="tool-panel" id="electricity"><p class="eyebrow">A scale you can compare</p><h2>What does a gigawatt mean over a year?</h2><p>Power is the rate at which electricity is used. Energy is the amount used over time. Think of a tap and a bucket: the flow rate is like power, while the water collected is like energy. This calculator makes the sovereignty paper’s electricity comparison visible.</p><form id="energy-calculator"><div class="preset-buttons"><button type="button" data-gw="13">13 GW example</button><button type="button" data-gw="100">100 GW example</button></div><div class="control-grid"><label for="power-gw">Electrical power, gigawatts<input id="power-gw" type="number" value="13" min="0.01" max="10000" step="0.01" required></label><label for="utilisation">Share of the year at that power, per cent<input id="utilisation" type="number" value="100" min="1" max="100" step="1" required></label></div><div class="calculator-result" aria-live="polite" aria-atomic="true"><p>Annual electricity use</p><output id="energy-total">113.88 TWh per year</output><p id="energy-comparison">About 39.7% of the paper’s 286.8 TWh Australian comparison.</p></div><p id="energy-error" class="error" role="alert"></p></form><p>The formula is gigawatts × 8,760 hours × utilisation ÷ 1,000. The fixed comparison is Australia’s 2025 generation of 286.8 terawatt-hours as reported in the paper. This measures electricity, not useful computing or intelligence. Actual loads and annual output vary.</p><p><a href="sovereignty-paper.html#p0016">Read the source comparison and its dated reference</a> · <a href="sovereignty-paper.html#p0208">Read the electricity scenario method</a></p></section></div>'''
write_page('tools.html','Explore the scale and connections','A transparent compute-cost calculator and an interactive tree explaining how the system’s components connect.',tools)

refs=page_head('Library','The evidence and the original papers','Read the source documents, inspect the proposals and follow the public projects. Every title below opens a source or an explicitly identified project page.')+'<section class="wrap"><div class="actions"><a class="button" href="documents/whole-system-preview.docx">Download the whole-system preview</a><a class="button secondary" href="documents/superintelligence-and-australian-sovereignty.docx">Download the sovereignty paper</a></div><div class="library-tools"><label for="library-search">Find a source<input id="library-search" type="search" placeholder="Try compute, care, festival or alignment"></label><label for="category-filter">Show<select id="category-filter" aria-label="Filter sources"><option value="all">All sources</option><option value="system">Whole-system sources</option><option value="sovereignty">Sovereignty references</option></select></label><p id="result-count" role="status"></p></div><div class="reference-list">'
for group in PREVIEW['references']:
    for e in group['entries']:
        extras=' · '.join(link(x['label'],LINKS[x['key']]) for x in e['extra'])
        refs+=f'<article data-category="system" data-search="{esc(e["title"]+" "+e["detail"],quote=True)}"><p class="ref-meta">Whole-system sources</p><h2>{link(e["title"],LINKS[e["key"]])}</h2><p>{esc(e["detail"])}</p><p class="link-row">{extras}</p></article>'
register=False
for b in SOVEREIGNTY['source_blocks']:
    if b['text']=='Reference register': register=True;continue
    if register and b['text'].strip() and b['links']:refs+=f'<article data-category="sovereignty" data-search="{esc(b["text"],quote=True)}"><p class="ref-meta">Sovereignty reference</p><p>{source_html(b)}</p></article>'
refs+='</div><p class="source-note">The sovereignty paper’s references preserve their original observation and announcement dates. Its full <a href="sovereignty-paper.html#p0206">calculation method</a> explains how the future scenarios were constructed.</p></section>'
write_page('library.html','References and source documents','A searchable source library linking both papers, their references and the associated public projects.',refs,category='Library')

projects=page_head('Project directory','Meet the projects behind the plan','Public pages give you a way to explore the work. Repositories let you inspect the files, documentation and development history.')+'<div class="wrap"><div class="library-tools"><label for="library-search">Find a project<input id="library-search" type="search" placeholder="Try Aura, bills, compute or GAJRA"></label><p id="result-count" role="status"></p></div><div class="project-grid">'
for group in PREVIEW['references']:
    for e in group['entries']:
        candidates=[(e['title'],LINKS[e['key']])]+[(x['label'],LINKS[x['key']]) for x in e['extra']]
        sites=[(label,url) for label,url in candidates if ('github.io' in url or 'p4a.xyz' in url) and not re.search(r'\.(pdf|docx)$',url,re.I)]
        explicit=[(label,url) for label,url in candidates if re.match(r'https://github.com/[^/]+/[^/]+/?$',url)]
        if not sites and not explicit:continue
        repos={url for label,url in explicit}
        for label,url in sites:
            m=re.match(r'https://([^.]+)\.github\.io/([^/]+)',url)
            if m:repos.add(f'https://github.com/{m[1]}/{m[2]}')
            if 'p4a.xyz' in url:repos.add('https://github.com/auraofintelligence/p4a-xyz-cinema')
        actions=' · '.join(link(label,url) for label,url in sites)
        actions+=''.join('<p>'+link('Repository · '+url.rsplit('/',1)[-1],url)+'</p>' for url in sorted(repos))
        projects+=f'<article data-search="{esc(e["title"]+" "+e["detail"],quote=True)}"><p class="ref-meta">{esc(group["title"].replace("References for ",""))}</p><h2>{esc(e["title"])}</h2><p>{esc(e["detail"])}</p><div class="link-row">{actions}</div></article>'
projects+='</div></div>'
write_page('projects.html','Related public projects and repositories','Explore the public sites and source repositories connected with the whole-system plan.',projects,category='Library')

terms={
'Artificial intelligence or AI':'Software that performs tasks such as recognising patterns, working with language or producing an answer. Its capabilities depend on its design, training, tools and the setting in which it is used.',
'AI alignment':'Work to make an AI system behave consistently with intended purposes and limits. The plan also asks how people clarify and revise those purposes together.',
'Superintelligence or SI':'A proposed level of AI capability that would substantially exceed human capability across many fields. Future scenarios explore possible consequences and depend on assumptions.',
'Compute':'The processing work computers can do. Chips, memory, electricity, cooling and communications make that work possible.',
'AI model':'Learned software that uses patterns developed during training. Running an existing model to respond to a request is called inference.',
'Open weights and open source':'Open weights make a model’s learned numerical parameters available under a licence. A broader open-source release can also provide code and other material needed to inspect, reproduce or change it. The actual licence and released materials matter.',
'Sovereign compute':'Practical authority over computing capacity, including who controls access, data, software choices, maintenance and decisions about its use.',
'The Missing Middle':'Shared computing between personal devices and very large data centres, with local access, skills and ownership. The Australian proposal describes 3,000 sites.',
'An Aura':'A proposed personal workspace connecting chosen records and AI tools. The person can decide what to keep, correct, use or share.',
'Verse Box':'A proposed portable setting for a supported introduction to an Aura, helping a visitor complete a useful task and take their own work away.',
'Aura Genesis':'A proposed longer learning process in which a person and their Aura build a useful record through experience, reflection and correction.',
'The Geode':'A proposed adult research setting within Genesis, bringing together a chamber, breathing equipment, sensory experiences and reflection. Its health research requires its own clinical and ethical design.',
'Healthy De-Slop':'Work to reduce avoidable strain through food, movement, rest, reflection and connection. The expanded idea includes making household bills and institutional information easier to understand and challenge.',
'Co-operative':'An organisation owned by its members for a shared purpose, with arrangements giving members a say in its operation.',
'The Braided Economy':'The proposed use of financial records, contribution records and accounts of outcomes together, so communities can see money, voluntary work and what actually changed.',
'C-Hour':'One verified hour of voluntary human contribution in the proposed community record. It has no cash value.',
'A digital twin':'A model or representation of a person, place or system that can be used to explore a question. Its usefulness depends on how it represents the real thing and how its results are checked.',
'Web3 Sensorium':'A proposal for sharing inspectable models, measurements and scientific debate across independently operated systems, with records of sources and corrections.',
'GAJRA Earth':'The proposed Global Association for Joyful Responsible Abundance on Earth. A gajra is a garland, used here to express connection among distinct, locally rooted associations.',
'A conditional scenario':'An account of what could happen if specified assumptions hold. Changing the assumptions changes the result. It can help expose choices and dependencies without claiming to know the future.',
'A Protopian Gambit':'An opening move that improves something now and creates more worthwhile possibilities for the next move. It is also the name of Luke’s 22-song album.'}
glossary=page_head('Words explained','A shared vocabulary','Definitions you can return to as the ideas become more connected.')+'<div class="wrap prose glossary"><dl>'+''.join('<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>' for k,v in terms.items())+'</dl></div>'
write_page('glossary.html','Words explained','Plain-language explanations of the terms used throughout the plan and sovereignty paper.',glossary)

about_sections=[('author','About this work','<p>Luke Nathan Hayes develops the Aura of Intelligence, GAJRA Earth and connected proposals from Minjerribah on Quandamooka Country. This site brings together the whole-system preview and the reviewed paper on superintelligence and Australian sovereignty.</p><p>The intended audience includes people encountering these ideas for the first time, community organisers, researchers and readers who want to inspect the sources. The site explains each component before asking readers to follow its connections.</p><p><a href="'+REPO+'">Inspect this website’s source</a> · <a href="library.html">Read the original documents</a> · <a href="projects.html">Explore the related projects</a></p>'),('editions','How to read the editions','<p>The whole-system preview incorporates household bill de-slop, the 22-song album count, GAJRA Earth’s public alignment watch and the proposed July 2035 global festival marking Live Aid’s fiftieth anniversary. The sovereignty paper and its scenarios are dated 5 November 2026.</p><p>The introductory sovereignty chapters are educational adaptations. The complete reading edition preserves the source paper’s argument, links and calculation methods. The source documents are available to download.</p>'),('images','Images and photographs','<p>The opening coastal city, community commons, local computing workshop and future festival are AI-generated concept images created for this site. They illustrate proposed possibilities and choices about the future. These are imagined settings. Subtle butterflies appear as incidental details in some scenes.</p><p>The Amity Point sunset is a real photograph by Pacificwizard, released under CC0. <a href="https://commons.wikimedia.org/wiki/File:Amity_Point_Jetty_at_Sunset._North_Stradbroke_Island,_Queensland,_Australia.jpg">Original photograph and licence</a>.</p><p>The Point Lookout photograph is by John Fairbairn, 2020, and is used under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. It is resized for web delivery, with the original credit border preserved. <a href="https://commons.wikimedia.org/wiki/File:Point_Lookout,_North_Stradbroke_Island.jpg">Original photograph</a>.</p>'+figure('point-lookout','Waves breaking against the rocks at Point Lookout, North Stradbroke Island.','Point Lookout, Minjerribah. Photograph by John Fairbairn, CC BY 4.0.')),('access','Reading and accessibility','<p>All chapters and references are readable without JavaScript. Search, the calculator and the connection selector run in your browser. The site uses descriptive links, a heading hierarchy, keyboard controls, a skip link and a print layout. It includes a human-readable site map and a machine-readable sitemap.</p><p>Original material follows the <a href="LICENCE.md">Strange But True Public Source Licence</a>. Third-party photographs retain their stated licences.</p>')]
write_page('about.html','About the work and image credits','Authorship, edition details, image provenance, accessibility and reuse permissions.',page_head('About','The work, its sources and its place','A public reading space for a connected body of proposals and research.')+reading(about_sections))

mapbody=page_head('Site map','Every page, in one place','Use this directory to read in sequence or find a particular topic.')+'<div class="wrap path-list">'
for category in ['Guide','Sovereignty','Source','Library']:
    items=[p for p in PAGES if p['category']==category]
    mapbody+='<section><h2>'+category+'</h2><ul>'+''.join('<li>'+link(p['title'],p['file'])+'<p>'+esc(p['description'])+'</p></li>' for p in items)+'</ul></section>'
mapbody+='</div>'
write_page('site-map.html','Site map','A complete directory of the website’s guides, interactive tools, original papers, references and projects.',mapbody)
(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+p['file']+'</loc><lastmod>2026-11-05</lastmod></url>' for p in PAGES)+'</urlset>',encoding='utf-8')
(DATA/'page-index.json').write_text(json.dumps(PAGES,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'sitemap.xml\n',encoding='utf-8')
(ROOT/'llms.txt').write_text('# Joyful Responsible Abundance\n\nEducational reading site by Luke Nathan Hayes. Public source rights apply.\n\n'+ '\n'.join('- ['+p['title']+']('+BASE+p['file']+'): '+p['description'] for p in PAGES)+'\n\nOriginal documents: documents/whole-system-preview.docx and documents/superintelligence-and-australian-sovereignty.docx. The source paper is dated 5 November 2026; future figures are conditional scenarios. See LICENCE.md for reuse rights.\n',encoding='utf-8')
for index,page in enumerate(PAGES):
    path=ROOT/page['file']
    html=path.read_text(encoding='utf-8').replace('<!-- page-navigation -->',nextlinks(index))
    path.write_text(html,encoding='utf-8')
print('Built',len(PAGES),'pages.')
