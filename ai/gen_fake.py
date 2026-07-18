import csv, os, random, json

random.seed(42)
BASE = 'E:/Project-VI/workspace/ComplaintMgmtSystem/TrainDataset'
DATA_PATH = os.path.join(BASE, 'processed_dataset.csv')
OUT_PATH = os.path.join(BASE, 'processed_dataset_1080.csv')

with open(DATA_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    existing = list(reader)
    fields = reader.fieldnames

before = {}
for r in existing:
    c = int(r['category_encoded'])
    before[c] = before.get(c, 0) + 1
print('Before:', before)

CAT_NAME = {0:'IT Support',1:'Hostels',2:'Academics',3:'Fees / Finance',4:'Maintenance',5:'Transport',6:'Security / Discipline',7:'Administration',8:'Library'}
PRIO_ENC = {'Low': 1, 'Medium': 0, 'High': 2}
PRIOS = ['Low','Medium','High']

def fill(t, pools):
    r = []; i = 0
    while i < len(t):
        if t[i] == '{':
            e = t.index('}', i)
            k = t[i+1:e]
            r.append(random.choice(pools.get(k, ['?'])))
            i = e + 1
        else:
            r.append(t[i]); i += 1
    return ''.join(r)

def gen(cat, n, tpls, pools):
    rows = []
    for _ in range(n):
        txt = fill(random.choice(tpls[cat]), pools.get(cat, {}))
        p = random.choice(PRIOS)
        rows.append({'text':txt,'category':CAT_NAME[cat],'priority':p,'source':'synthetic',
                     'category_encoded':str(cat),'priority_encoded':str(PRIO_ENC[p])})
    return rows

new = []

new += gen(0, 50, {0:[
    'The {n} is {p} since {d} in the {l} please fix it',
    'I cannot access the {n} from {l} it keeps showing {p}',
    'My {n} is not working tried restarting but still {p}',
    'Internet speed in the {l} is very slow takes forever',
    'The printer in {l} is not printing shows {p} error',
    'VPN connection to the campus {n} keeps failing from {l}',
    'My email account is {p} since {d} cannot send or receive',
    'The projector in room {l} is not connecting to my laptop',
    'Login portal for the {n} is {p} blank page',
    'The {n} connection keeps dropping every few minutes',
]}, {0:{'n':['wifi','network','internet','printer','laptop','computer','projector','vpn','email','portal','software','server','router','system'],
         'p':['not working','very slow','down','disconnecting','crashing','showing error','not responding','frozen','broken','lagging','unstable'],
         'd':['morning','yesterday','last week','3 days','a week','two weeks','this morning','last night'],
         'l':['library','lab 3','block a','computer lab','main building','cse department','seminar hall','auditorium','admin block']}})

new += gen(2, 36, {2:[
    'The {person} is coming late to {t} class every day',
    '{person} did not show up for the scheduled {t} lecture',
    'The {person} is not explaining {t} properly students struggling',
    '{t} results are delayed by {d} we need them for placement',
    'My {t} marks were entered wrongly in portal please check',
    'The {person} is not responding to emails about {t} project',
    'Study material for {t} is not uploaded on the LMS',
    'The {person} canceled the {t} lecture without rescheduling',
    '{t} exam schedule has two papers on same day resolve',
    'The {person} marked me absent even though I attended {t}',
    'Grade for {t} is missing from transcript need it for {d}',
    'The {person} is not giving proper feedback on {t} submissions',
    'The {person} asked irrelevant questions in viva not in syllabus',
    'Attendance for {t} was marked wrong I was present that day',
]}, {2:{'person':['professor sharma','dr patel','the faculty','the lecturer','the teacher','the instructor','prof gupta','the course coordinator','the hod'],
         't':['assignment','project','lab report','lecture','course','exam','test','quiz','thesis','seminar','tutorial','workshop','internship','research paper','practical'],
         'd':['one week','ten days','two weeks','a month','last semester','fifteen days']}})

new += gen(6, 30, {6:[
    'Someone stole my {th} from the {l} during lunch',
    'Suspicious person seen roaming around {l} after college hours',
    'A {th} was found damaged in the {l} by unknown persons',
    'The security guard at {l} is not checking id cards',
    'CCTV camera near the {l} has been broken for {d}',
    'Students misbehaving in the library disturbing others',
    'A stranger entered the hostel at {l} at night',
    'The {l} gate is left open at night security risk',
    'My {th} went missing from the {l} locker room',
    'Unsafe situation in the parking lot near {l}',
    'Students caught fighting in the {l} need action',
]}, {6:{'th':['laptop','phone','wallet','bag','bicycle','books','charger','headphones','watch','tablet','keys','id card','calculator'],
         'l':['library','canteen','parking lot','hostel courtyard','sports ground','main entrance','back gate','computer lab','auditorium','garden area','staircase','cycle stand'],
         'd':['a week','two weeks','a month','several days','since last month']}})

new += gen(7, 50, {7:[
    'My {t} application pending for {d} no response yet',
    'The {person} in admin office is rude with students',
    'I need a {t} certificate urgently for my job application',
    'The {t} form on website not working cannot submit',
    'Office hours for {t} are very limited cannot meet staff',
    'My {t} request was rejected without any explanation',
    'The clerk lost my original documents for {t} verification',
    'The {t} approval process takes too long more than {d}',
    'My degree certificate has spelling mistake in my name',
    'Transfer certificate application stuck for {d}',
    'The admin staff at {l} is very unhelpful and rude',
    'My {t} document was misplaced please trace it',
    'Someone asked for bribe to process my {t} application',
    'Online {t} portal showing wrong status information',
    'My application sent to wrong department please forward',
]}, {7:{'t':['bonafide certificate','transfer certificate','degree','transcript','migration certificate','internship approval','noc','scholarship form','fee waiver','hostel application','id card','grade card','admission form','character certificate'],
         'person':['the clerk','the administrative officer','the registrar','the dean','the office assistant','the department secretary','the coordinator','the front desk staff'],
         'd':['a month','three weeks','two months','45 days','last semester','since june','over a month','since registration'],
         'l':['ground floor','first floor','admin block','admission office','accounts section','registrar office','front desk','academic block']}})

new += gen(8, 99, {8:[
    'The {b} I need for my project not available in library',
    'Library fine charged incorrectly I returned book on time',
    'The {b} section in library always closed during lunch',
    'Library timing should be extended during exam week',
    'The {b} books on shelf are all old editions need new',
    'Noise level in library reading hall very high no control',
    'Library book issue system down cannot issue or return',
    'I lost a book from library how do I pay penalty',
    'Library id card machine not working cannot scan card',
    'Reference books cannot be taken home no copies inside',
    'Library staff at counter is very rude and slow',
    'Digital library computers all occupied during peak hours',
    'The journal I need is missing from periodical section',
    'Library membership renewal not processed even after {d}',
    'Not enough textbook copies for number of students',
    'Book return drop box full cannot return my book',
    'Book catalogue search shows wrong shelf location',
    'Photocopy machine in library broken since {d}',
]}, {8:{'b':['book','journal','textbook','reference book','novel','magazine','research paper','thesis','dictionary','encyclopedia','study material','question bank','handbook','manual','guide book','atlas','report','newspaper','periodical'],
         'd':['a week','two weeks','three weeks','a month','ten days','since last month','this semester']}})

all_rows = existing + new
with open(OUT_PATH, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(all_rows)

print(f'Added {len(new)} rows, total {len(all_rows)}')
after = {}
for r in all_rows:
    c = int(r['category_encoded'])
    after[c] = after[c] + 1 if c in after else 1
print('After:', dict(sorted(after.items())))
