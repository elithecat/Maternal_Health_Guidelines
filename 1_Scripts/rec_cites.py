import re, json, sys
txt = open(sys.argv[1]).read()
a = txt.index('CLINICAL RECOMMENDATIONS AND'); b = txt.index('REFERENCES')
sec = txt[a:b]
sec = re.sub(r'(?m)^(=== PAGE.*|VOL\. 141.*|© 2023.*|and Gynecologists\. Published.*|Unauthorized reproduction.*|n College of Obstetricians.*|by Wolters Kluwer.*|of this article is prohibited.*|erinatal Mental Health Treatment.*|agement OBSTETRICS.*|\d{4} CPG Perinatal.*)$', '', sec)
flat = re.sub(r'-\n', '', sec); flat = re.sub(r'\s+', ' ', flat)
recs = [
 ('R1','ACOG recommends that obstetricians be prepared'),
 ('R2','ACOG recommends that obstetricians initiate'),
 ('R3','ACOG recommends that a validated screening'),
 ('R4','ACOG recommends that treatment for perina'),
 ('R5','ACOG recommends against withholding'),
 ('GPP1','Use Perinatal Psychiatry Access Programs as'),
 ('R6','ACOG recommends that psychotherapy be'),
 ('R7','ACOG recommends that selective serotonin reuptake inhibitors be used as first-line phar'),
 ('R8','ACOG recommends consideration of brexano'),
 ('R9','ACOG recommends that selective serotonin reuptake inhibitors be used as first-line psycho'),
 ('R10','ACOG recommends that benzodiazepines be'),
 ('R11','ACOG recommends against discontinuing'),
 ('R12','ACOG recommends against valproate'),
 ('R13','ACOG recommends that pregnant individuals using'),
 ('R14','ACOG recommends that pregnant patients taking lithium'),
 ('GPP2','It is imperative that lithium dosing'),
 ('GPP3','Postpartum psychosis is a psychiatric emer'),
]
pos=[]
for k,s in recs:
    s2 = re.sub(r'-','',s)
    i = flat.replace('-','').find(s2)
    assert i>=0, k
    pos.append(i)
nf = flat.replace('-','')
out={}
for j,(k,s) in enumerate(recs):
    chunk = nf[pos[j]: pos[j+1] if j+1<len(recs) else len(nf)]
    nums=set()
    for g in re.findall(r'\((\d{1,3}(?:\s*[,–]\s*\d{1,3})*)\)', chunk):
        for part in re.split(r'\s*,\s*', g):
            if '–' in part:
                x,y = map(int, part.split('–')); nums.update(range(x,y+1))
            else: nums.add(int(part))
    nums = sorted(n for n in nums if 1<=n<=181)
    out[k]=nums
    print(k, nums)
json.dump(out, open(sys.argv[2],'w'))
