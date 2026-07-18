import csv, os, random, json

random.seed(42)
BASE = 'E:/Project-VI/workspace/ComplaintMgmtSystem/TrainDataset'
DATA_PATH = os.path.join(BASE, 'processed_dataset_815.csv')
OUT_PATH = os.path.join(BASE, 'processed_dataset_1274.csv')

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

new += gen(2, 50, {2:[
    'The {person} is coming late to {t} class every day',
    '{person} did not show up for the scheduled {t} lecture',
    'The {person} is not explaining {t} properly students struggling',
    '{t} results are delayed by {d} we need them for placement',
    'My {t} result is delayed by {d} please publish it soon',
    'Exam result not published even after {d} of waiting',
    'University delayed the {t} result for {d} very frustrating',
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
    'The {t} was conducted months ago but result still pending',
    '{t} held last semester still no result published yet',
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

# === NEW TEMPLATES FOR WEAK AREAS ===

# IT Support: password, server, antivirus, biometric, smart board
new += gen(0, 15, {0:[
    'My password for the {n} is not working cannot login at all',
    'The {n} server is down since {d} all systems are affected',
    'Antivirus on the {l} computer is blocking everything',
    'The biometric system at {l} is {p} cannot mark attendance',
    'The smart board in room {l} is {p} touch not responding',
    'Campus wide network outage in {l} since {d} no internet',
    'The {n} software license expired cannot use the application',
    'Online exam platform crashed during the {t} test',
    'The {n} system is {p} after the latest update',
    'Unable to connect to campus wifi with my device at {l}',
]}, {0:{'n':['wifi','network','portal','server','antivirus','system','application','vpn','email','lms'],
         'p':['not working','down','showing error','not responding','frozen','glitchy','malfunctioning','unreachable'],
         'd':['morning','yesterday','3 days','a week','this morning','last night'],
         'l':['library','lab 3','computer lab','main building','cse department','seminar hall','lecture hall'],
         't':['online exam','midterm','final']}})

# Hostels: roommate conflict, mess food, visitor policy, curfew, bed allocation
new += gen(1, 15, {1:[
    'My roommate is {p} every night disturbing my sleep',
    'The mess food quality is very {p} since {d} students getting sick',
    'Visitor entry in hostel is {p} friends cannot meet me',
    'Curfew timing is too strict in girls hostel need relaxation',
    'My bed allocation in room is wrong I requested lower berth',
    'Hostel {l} washroom is always dirty not cleaned for {d}',
    'The warden is {p} towards students from certain regions',
    'Laundry service in hostel is {p} clothes returned damaged',
    'Drinking water in hostel {l} has bad taste and smell',
    'Hostel complaint register is never checked by authorities',
]}, {1:{'p':['too noisy','very loud','arguing constantly','playing music','fighting','disturbing','dirty','unhygienic','biased','unfair','poor','bad','not allowed','too strict'],
         'd':['a week','last month','two weeks','this semester','since joining','many days'],
         'l':['block a','block b','block c','first floor','second floor','east wing','west wing']}})

# Academics: plagiarism, cheating, course quality, syllabus, elective
new += gen(2, 20, {2:[
    'Student was caught {p} in the {t} exam but no action taken',
    'The {t} course content is very {p} we are not learning anything',
    'Syllabus for {t} is not completed even after {d} of classes',
    'The {t} elective I wanted is not available this semester',
    'Another student copied my {t} assignment teacher did nothing',
    'The {t} practical sessions are not {p} at all waste of time',
    'Guest lecture for {t} was cancelled without prior notice',
    'The {t} question paper had questions outside the syllabus',
    'Industrial visit for {t} department not organized this year',
    'The {p} in the {t} lab is affecting our learning environment',
]}, {2:{'person':['professor sharma','dr patel','the faculty','the lecturer','the teacher','the instructor','prof gupta','the hod'],
         't':['assignment','project','lab report','lecture','course','exam','test','quiz','thesis','seminar','tutorial','workshop','internship','research paper','practical'],
         'p':['cheating','copying','plagiarism','outdated','boring','useless','poor quality','too easy','bad','not useful','distraction','noise','chaos'],
         'd':['one month','this semester','last semester','three weeks','several weeks']}})

# Fees/Finance: transaction failed, eligibility, installment, insurance
new += gen(3, 10, {3:[
    'My {t} payment failed but money was deducted from my account',
    'Scholarship eligibility criteria are {p} many deserving students left out',
    'The installment option for {t} is not available on portal',
    'Health insurance premium deducted but no insurance card issued',
    'The {t} calculation on my fee slip seems {p} please verify',
    'Sports fee charged but I do not use any sports facilities',
    'The bank transaction for {t} shows success but portal unpaid',
    'Financial aid application status not updated for {d}',
]}, {3:{'t':['tuition fee','hostel fee','exam fee','registration fee','admission fee','caution deposit','bus fee','lab fee'],
         'p':['wrong','incorrect','unfair','biased','too high','not transparent'],
         'd':['a month','three weeks','two months','last semester','since june']}})

# Security/Discipline: harassment, bullying, ragging, smoking, drugs, vandalism, cyber
new += gen(6, 60, {6:[
    'A {person} is {p} me every day in the {l} feeling very unsafe',
    'Senior students are {p} juniors in the hostel demanding money',
    'Someone is making {p} comments towards female students in {l}',
    'A group of students was {p} in the {l} after college hours',
    'A {person} {p} me on social media threatening to harm me',
    'Students are {p} cigarettes in the {l} near the no smoking zone',
    'I witnessed {p} being sold in the {l} during college hours',
    'Someone {p} the {th} in the {l} last night deliberately',
    'A {person} touched me {p} in the crowded {l} area',
    'There is a {p} environment in the {l} for LGBTQ students',
    'A group of students {p} the laboratory equipment in {l}',
    'The {person} used {p} language against me in front of everyone',
    'My social media account was {p} by someone from the {l}',
    'A {person} threatened to fail me if I reported the incident',
    'Students are {p} alcohol in the hostel rooms at night',
    'A {person} in the {l} is {p} students constantly making them cry',
    'The {person} touched me {p} during the lab session in {l}',
    'A {person} is {p} students based on their religion in {l}',
    'The {person} sends me {p} text messages late at night',
]}, {6:{'person':['teacher','professor','senior student','group of seniors','staff member','security guard','unknown person','classmate','lab assistant','faculty member','the hod','the coordinator'],
         'th':['window','door','furniture','chair','table','computer','bench','cctv camera','light'],
         'p':['harassing','bullying','stalking','ragging','teasing','threatening','blackmailing','intimidating','abusing','insulting','humiliating','smoking','vaping','selling drugs','taking drugs','vandalizing','destroying','damaging','inappropriate','sexual','improper','hostile','unsafe','hacking','impersonating','drinking'],
         'l':['library','canteen','parking lot','hostel','hostel courtyard','sports ground','main entrance','back gate','computer lab','auditorium','garden area','corridor','staircase','washroom','classroom','campus ground']}})

# Administration: admission, placement, records, grievance, exam admin, hostel admin
new += gen(7, 40, {7:[
    'My admission was {p} even though I met all eligibility criteria',
    'The placement cell is not {p} companies rejecting students unfairly',
    'My semester {t} has an error in the name and date of birth',
    'I filed a grievance {d} ago but no committee has been formed yet',
    'Exam center allocated is very far from my hostel {p} to reach',
    'Hostel allotment was {p} I applied for single room got shared',
    'The {person} in admission office lost my original documents',
    'My name correction application in records is pending for {d}',
    'Placement eligibility criteria are {p} many students cannot apply',
    'The college is not issuing my {t} despite multiple follow ups',
    'Duplicate {t} application submitted {d} ago no response',
    'The grievance committee rejected my complaint without hearing me',
    'Exam form could not be submitted due to portal {p} on last day',
    'The {person} in the accounts office is {p} processing refunds',
    'My transfer certificate application has been {p} for {d}',
    'The {t} office misplaced my internship report submitted last month',
    'The college is delaying {t} verification for my higher studies',
    'Attendance shortage condonation application not processed',
]}, {7:{'person':['the clerk','the administrative officer','the registrar','the dean','the office assistant','the department secretary','the coordinator','the admission officer','the front desk staff','the accounts officer'],
         't':['transcript','degree','marksheet','grade card','bonafide certificate','transfer certificate','migration certificate','internship approval','noc','hostel application','id card','admission form','character certificate','exam registration'],
         'p':['rejected','cancelled','denied','not responding','unhelpful','unfair','biased','slow','too strict','confusing','discriminatory','not transparent','wrong','incorrect','difficult','too far','inconvenient','rejected without reason','pending','stuck'],
         'd':['a month','two months','three weeks','45 days','last semester','since june','since admission','since march','this semester']}})

# Library: digital access, study room, printing, lost & found, disability
new += gen(8, 20, {8:[
    'Digital library access to e journals not working from home',
    'The library study room booking system is {p} never available',
    'Printing service in library is {p} pages not coming out clearly',
    'Lost and found section in library not helpful lost my {b} there',
    'No wheelchair access to the library {l} for disabled students',
    'The library {p} hours during holidays are not communicated',
    'Book recommendation submitted {d} ago no update on purchase',
    'The digital library website is {p} cannot search for articles',
    'Photocopy rates in library are too {p} compared to outside',
    'Scanner in the library is {p} cannot scan my documents',
]}, {8:{'b':['book','journal','notebook','textbook','calculator','pen drive'],
         'p':['always full','not working','down','slow','broken','expensive','high','not functioning','not updated','unclear','not announced'],
         'l':['reading hall','basement','entrance','first floor','reference section'],
         'd':['a month','three weeks','since last month','this semester','two months']}})

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
