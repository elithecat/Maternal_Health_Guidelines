import json, sys
S = sys.argv[1]
refs = {r['ref']: r for r in json.load(open(f'{S}/refs.json'))}
rc = json.load(open(f'{S}/rec_cites.json'))
rc['GPP1'] = [n for n in rc['GPP1'] if n != 3]   # "(3)" is a list marker, not a citation
recs = {
 'R1': ('General approach','ACOG recommends that obstetricians be prepared to counsel patients on the benefits and risks of psychopharmacotherapy for perinatal mental health conditions when clinically indicated.','Strong','Moderate'),
 'R2': ('General approach','ACOG recommends that obstetricians initiate psychopharmacotherapy for perinatal depression or anxiety disorders, refer patients to appropriate behavioral health resources when indicated, or both.','Strong','Moderate'),
 'R3': ('General approach','ACOG recommends that a validated screening tool be used to monitor for response to treatment or remission of depression or anxiety symptoms. If clinically indicated, the pharmacotherapy dosage should be up-titrated, with the goal of remission of depressive and anxiety symptoms.','Strong','High'),
 'R4': ('Health equity','ACOG recommends that treatment for perinatal mood and anxiety disorders be equitably available and accessible to all pregnant and postpartum individuals.','Strong','Moderate'),
 'R5': ('General approach','ACOG recommends against withholding or discontinuing medications for mental health conditions due to pregnancy or lactation status alone.','Strong','Low'),
 'GPP1': ('General approach','Use Perinatal Psychiatry Access Programs as a resource for management and treatment guidance for individuals with mental health conditions.','Good Practice Point','Ungraded'),
 'R6': ('Depression','ACOG recommends that psychotherapy be considered a first-line treatment for mild-to-moderate perinatal depression.','Strong','Moderate'),
 'R7': ('Depression','ACOG recommends that SSRIs be used as first-line pharmacotherapy for perinatal depression. SNRIs are reasonable alternatives. Pharmacotherapy should be individualized based on prior response to therapy (if applicable). If there is no pharmacotherapy history, sertraline or escitalopram are reasonable first-line medications.','Strong','Low'),
 'R8': ('Depression','ACOG recommends consideration of brexanolone administration in the postpartum period for moderate-to-severe perinatal depression with onset in the third trimester or within 4 weeks postpartum (balancing rapid onset against access, cost, breastfeeding, inpatient monitoring, and lack of efficacy data beyond 30 days).','Strong','Moderate'),
 'R9': ('Anxiety','ACOG recommends that SSRIs be used as first-line psychopharmacotherapy for perinatal anxiety. SNRIs are reasonable alternatives. Pharmacotherapy should be individualized based on prior response to therapy (if applicable). If there is no pharmacotherapy history, sertraline or escitalopram are reasonable first-line medications.','Strong','Low'),
 'R10': ('Anxiety','ACOG recommends that benzodiazepines be avoided or prescribed sparingly as a treatment for perinatal anxiety.','Strong','Moderate'),
 'R11': ('Bipolar disorder','ACOG recommends against discontinuing mood stabilizers, except for valproate, during pregnancy due to the risk of recurrence or exacerbation of mood symptoms.','Strong','Moderate'),
 'R12': ('Bipolar disorder','ACOG recommends against valproate as a first-line treatment for bipolar disorder. Valproate should be avoided in pregnancy because reasonable alternatives usually can be identified.','Strong','Moderate'),
 'R13': ('Bipolar disorder','ACOG recommends that pregnant individuals using antipsychotic medications undergo screening for gestational diabetes mellitus, consistent with standard prenatal care.','Strong','Moderate'),
 'R14': ('Bipolar disorder','ACOG recommends that pregnant patients taking lithium in the first trimester receive a detailed ultrasound examination in the second trimester.','Strong','Moderate'),
 'GPP2': ('Bipolar disorder','It is imperative that lithium dosing be monitored during pregnancy and postpartum.','Good Practice Point','Ungraded'),
 'GPP3': ('Postpartum psychosis','Postpartum psychosis is a psychiatric emergency. Treatment options within the scope of obstetricians while awaiting psychiatric assessment include sedating antipsychotics such as olanzapine or haloperidol, which can be used with benzodiazepines such as lorazepam; if haloperidol is used, benztropine or diphenhydramine should be given to prevent extrapyramidal symptoms and dystonia.','Good Practice Point','Ungraded'),
}
extra = {
 'T2a': {'citation':'Huybrechts KF, Palmsten K, Avorn J, Cohen LS, Holmes LB, Franklin JM, et al. Antidepressant use in pregnancy and the risk of cardiac defects. N Engl J Med 2014;370:2397–407. doi: 10.1056/NEJMoa1312828','doi':'10.1056/NEJMoa1312828','first_author':'Huybrechts','year':2014,'volume':'370','first_page':'2397'},
 'T2c': {'citation':'Palmsten K, Huybrechts KF, Michels KB, Williams PL, Mogun H, Setoguchi S, et al. Antidepressant use and risk for preeclampsia. Epidemiology 2013;24:682–91. doi: 10.1097/EDE.0b013e31829e0aaa','doi':'10.1097/EDE.0b013e31829e0aaa','first_author':'Palmsten','year':2013,'volume':'24','first_page':'682'},
 'T2d': {'citation':'Wartko PD, Weiss NS, Enquobahrie DA, Chan KC, Stephenson-Famy A, Mueller BA, et al. Antidepressant continuation in pregnancy and risk of gestational diabetes. Pharmacoepidemiol Drug Saf 2019;28:1194–203. doi: 10.1002/pds.4799','doi':'10.1002/pds.4799','first_author':'Wartko','year':2019,'volume':'28','first_page':'1194'},
 'T2e': {'citation':'Malm H, Sourander A, Gissler M, Gyllenberg D, Hinkka-Yli-Salomäki S, McKeague IW, et al. Pregnancy complications following prenatal exposure to SSRIs or maternal psychiatric disorders: results from population-based national register data. Am J Psychiatry 2015;172:1224–32. doi: 10.1176/appi.ajp.2015.14121575','doi':'10.1176/appi.ajp.2015.14121575','first_author':'Malm','year':2015,'volume':'172','first_page':'1224'},
 'T2f': {'citation':'Palmsten K, Hernández-Díaz S, Huybrechts KF, Williams PL, Michels KB, Achtyes ED, et al. Use of antidepressants near delivery and risk of postpartum hemorrhage: cohort study of low income women in the United States. BMJ 2013;347:f4877. doi: 10.1136/bmj.f4877','doi':'10.1136/bmj.f4877','first_author':'Palmsten','year':2013,'volume':'347','first_page':'f4877'},
 'T2h': {'citation':'Kautzky A, Slamanig R, Unger A, Höflich A. Neonatal outcome and adaption after in utero exposure to antidepressants: a systematic review and meta-analysis. Acta Psychiatr Scand 2022;145:6–28. doi: 10.1111/acps.13367','doi':'10.1111/acps.13367','first_author':'Kautzky','year':2022,'volume':'145','first_page':'6'},
 'T2i': {'citation':'Brown AS, Gyllenberg D, Malm H, McKeague IW, Hinkka-Yli-Salomäki S, Artama M, et al. Association of selective serotonin reuptake inhibitor exposure during pregnancy with speech, scholastic, and motor disorders in offspring. JAMA Psychiatry 2016;73:1163–70. doi: 10.1001/jamapsychiatry.2016.2594','doi':'10.1001/jamapsychiatry.2016.2594','first_author':'Brown','year':2016,'volume':'73','first_page':'1163'},
 'F1': {'citation':'Byatt N, Mittal LP, Brenckle L, Logan DG, Masters GA, Bergman A, et al. Lifeline for Moms Perinatal Mental Health Toolkit. University of Massachusetts Medical School; 2019. (Source for Figures 1 and 2.) https://www.umassmed.edu/lifeline4moms/products-resources/toolkits-and-apps/2019/11/lifeline4moms-perinatal-mental-health-toolkit/','doi':None,'first_author':'Byatt','year':2019,'volume':None,'first_page':None},
}
cites = {k: [str(n) for n in v] for k,v in rc.items()}
cites['R7'] += ['T2a','T2c','T2d','T2e','T2f','T2h','T2i']   # Table 2 footnotes (T2b = ref 104, T2g = ref 110)
cites['R3'] += ['F1']
master = {}
for k,ids in cites.items():
    for i in ids:
        if i not in master:
            src = refs[int(i)] if i.isdigit() else extra[i]
            master[i] = {'ref_id': i, **{x:src.get(x) for x in ('citation','doi','first_author','year','volume','first_page')}, 'recs': []}
        master[i]['recs'].append(k)
master['104']['note'] = 'Also Table 2 footnote (pregnancy loss row)'
master['110']['note'] = 'Also Table 2 footnote (PPHN row)'
json.dump({'recs':{k:{'section':v[0],'text':v[1],'strength':v[2],'evidence_quality':v[3],'citations':cites[k]} for k,v in recs.items()},
           'citations': list(master.values())}, open(f'{S}/master.json','w'), indent=1, ensure_ascii=False)
print('unique citations:', len(master), '| rec-citation links:', sum(len(v) for v in cites.values()))
