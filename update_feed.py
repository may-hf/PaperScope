#!/usr/bin/env python3
"""Daily metadata-only candidate feed from OpenAlex. No invented AI summaries."""
import datetime as dt, json, os, pathlib, re, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
TODAY=dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date()
LOOKBACK=(TODAY-dt.timedelta(days=35)).isoformat()
QUERIES={
 'Chemistry':['oxyhydride topochemical','perovskite hydride','mixed anion perovskite','topochemical reduction oxide','oxynitride perovskite'],
 'Geometry':['aperiodic tiling','polyomino tiling','maze graph','computational geometry tessellation','space filling tiling']
}
JOURNALS=('nature','science','journal of the american chemical society','chemistry of materials','inorganic chemistry','acs applied materials','jacs au','angewandte','chemical science')

def fetch(query):
    params=urllib.parse.urlencode({'search':query,'filter':f'from_publication_date:{LOOKBACK},type:article','per-page':35,'select':'id,doi,title,publication_date,primary_location,authorships,abstract_inverted_index,open_access'})
    url='https://api.openalex.org/works?'+params
    req=urllib.request.Request(url,headers={'User-Agent':'PaperScope/0.2 (personal literature digest; contact: paperscope@example.org)'})
    with urllib.request.urlopen(req,timeout=35) as r:return json.load(r)['results']

def abstract_text(inv):
    if not inv:return ''
    positions=[(pos,word) for word,arr in inv.items() for pos in arr]
    return ' '.join(w for _,w in sorted(positions))[:600]

def make(w,category):
    title=(w.get('title') or '').strip()
    doi=w.get('doi') or ''
    id=(doi.removeprefix('https://doi.org/').lower() if doi else w['id'].rsplit('/',1)[-1])
    authors=w.get('authorships') or []
    first=authors[0] if authors else {}
    aff=', '.join(i.get('display_name','') for i in first.get('institutions',[]) if i.get('display_name')) or '未確認'
    source=((w.get('primary_location') or {}).get('source') or {}).get('display_name') or '掲載誌未確認'
    pub=w.get('publication_date') or TODAY.isoformat()
    url=doi or ((w.get('primary_location') or {}).get('landing_page_url')) or w['id']
    abstract=abstract_text(w.get('abstract_inverted_index'))
    tags=[t for t in (['Oxyhydride','Topochemical','Perovskite','Oxynitride','Hydride','Vanadium','Chromium','Cobalt'] if category=='Chemistry' else ['Tiling','Maze','Polyomino','Graph Theory','Geometry']) if re.search(t.replace('Oxyhydride','oxyhydride').replace('Topochemical','topochemical'),title+' '+abstract,re.I)]
    return {'id':id,'title':title,'journal':source,'date':pub,'added':TODAY.isoformat(),'category':category,'tags':tags or [category],'firstAuthor':first.get('author',{}).get('display_name') or '未確認','firstAffiliation':aff,'corresponding':'未確認（出版社ページで要確認）','summary':'自動収集した論文候補です。研究内容・要旨は原論文で確認してください。','novelty':'新規性は未評価です。自動収集では査読・本文照合やAI要約を行っていません。','url':url,'source':'auto'}

def main():
    output=ROOT/'papers.json'
    old=json.loads(output.read_text()) if output.exists() else {'papers':[]}
    byid={p['id'].lower():p for p in old['papers'] if p.get('id')}
    failures=[];results={}
    for category,queries in QUERIES.items():
        candidates={}
        for query in queries:
            try: works=fetch(query)
            except Exception as exc: failures.append(f'{query}: {exc}');continue
            for w in works:
                if not w.get('title'):continue
                p=make(w,category);id=p['id'].lower()
                if id in byid:continue
                text=(p['title']+' '+p['journal']).lower()
                score=(sum(x in text for x in ('oxyhydride','hydride','topochemical','mixed anion','oxynitride','tiling','polyomino','maze'))*5+
                    (5 if category=='Chemistry' and any(j in p['journal'].lower() for j in JOURNALS) else 0)+
                    (TODAY-dt.date.fromisoformat(p['date'])).days*-0.05)
                if category=='Geometry' and 'tiling' not in text and 'polyomino' not in text and 'maze' not in text and 'tessellation' not in text:continue
                if category=='Chemistry' and not any(k in text for k in ('hydride','oxide','perovskite','anion','reduction','vanadium','chromium','cobalt')):continue
                candidates[id]=(score,p)
        results[category]=[p for _,p in sorted(candidates.values(),key=lambda v:v[0],reverse=True)[:(5 if category=='Chemistry' else 2)]]
    if failures and not any(results.values()):raise RuntimeError('No usable API responses: '+'; '.join(failures))
    for category in QUERIES:
        for p in results[category]:byid.setdefault(p['id'].lower(),p)
    output.write_text(json.dumps({'updated':TODAY.isoformat(),'papers':list(byid.values()),'notes':'Unreviewed metadata candidates; corresponding authors and summaries not verified.'},ensure_ascii=False,indent=2)+'\n')
    print('Saved',len(byid),'records; failures:',failures)
if __name__=='__main__':main()
