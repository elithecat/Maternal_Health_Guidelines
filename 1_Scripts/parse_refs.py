import re, json, sys
lines = open(sys.argv[1]).read().split('\n')
start = next(i for i,l in enumerate(lines) if l.strip()=='REFERENCES')
end = next(i for i,l in enumerate(lines) if l.strip()=='APPENDICES')
skip = re.compile(r'^(=== PAGE|VOL\. 141|© 2023|and Gynecologists\. Published|Unauthorized reproduction|n College of Obstetricians|by Wolters Kluwer|of this article is prohibited|erinatal Mental Health Treatment|agement OBSTETRICS|\d{4} CPG Perinatal)')
body = [l.strip() for l in lines[start+1:end] if not skip.match(l.strip())]
refs = {}; cur = 0; buf = []
for l in body:
    m = re.match(r'^(\d{1,3})\. (.*)$', l)
    if m and int(m.group(1)) == cur+1:
        if cur: refs[cur] = buf
        cur += 1; buf = [m.group(2)]
    else:
        buf.append(l)
refs[cur] = buf
assert sorted(refs)==list(range(1,182))
out=[]
for n,parts in sorted(refs.items()):
    t = ''
    for p in parts:
        if t.endswith('-') and not re.search(r'\d-$', t): t = t[:-1] + p   # dehyphenate words
        elif t.endswith(('/', '.')) and re.search(r'doi[:.] ?10\.\S*$', t): t = t + p  # DOI continuation
        else: t = (t + ' ' + p).strip()
    t = t.replace('(cid:1)','').replace('(cid:3)','').replace('ą','').strip()
    d = re.search(r'doi[:.] ?(10\..*)$', t)
    doi = re.sub(r'\s','', d.group(1)).rstrip('.') if d else None
    m = re.search(r'\b((?:19|20)\d{2});(\d+)(?:\([^)]*\))?:([A-Za-z]?\d+)', t)
    yr = vol = fp = None
    if m: yr, vol, fp = int(m.group(1)), m.group(2), m.group(3)
    au = re.match(r"^([A-ZÀ-Ýa-zß-ÿ'’\- ]+?) [A-Z]{1,3}[,.]", t)
    au = au.group(1) if au else None
    out.append({'ref':n,'citation':t,'doi':doi,'year':yr,'volume':vol,'first_page':fp,'first_author':au})
json.dump(out, open(sys.argv[2],'w'), indent=1, ensure_ascii=False)
print(len(out))
