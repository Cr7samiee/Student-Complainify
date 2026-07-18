import csv, os, random, json
from copy import deepcopy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, 'TrainDataset', 'processed_dataset.csv')

random.seed(42)

# ===== TEMPLATES per category (category_encoded -> list of templates) =====
# Placeholders: {noun}, {problem}, {duration}, {location}, {person}, {thing}, {amount}

TEMPLATES = {
    0: [  # IT Support
        "The {noun} is {problem} since {duration} in the {location} please fix it",
        "I cannot access the {noun} from {location} it keeps showing {problem}",
        "The {noun} at {location} has been {problem} for {duration} need urgent help",
        "My {noun} is not working tried restarting but still {problem}",
        "Please check the {noun} in {location} it is {problem} since yesterday",
        "The {noun} connection keeps dropping every few minutes it is very {problem}",
        "Unable to log into the {noun} system it says {problem}",
        "The {noun} server is down in {location} all computers are affected",
        "Request to reset my {noun} password it has been {problem} for {duration}",
        "The {noun} software is crashing whenever I try to {problem}",
        "Internet speed in the {location} is very slow it takes forever to load pages",
        "The printer in {location} is not printing it shows {problem} error",
        "VPN connection to the campus {noun} keeps failing from {location}",
        "My email account is {problem} cannot send or receive messages since {duration}",
        "The projector in room {location} is not connecting to my laptop",
        "The {noun} application freezes when I try to submit my work",
        "Login portal for the {noun} is {problem} it redirects to a blank page",
        "The shared drive {noun} is inaccessible from the {location} computers",
        "Antivirus on the {location} computers is blocking essential {noun} software",
        "The {noun} update failed and now the system is stuck in a boot loop",
    ],
    1: [  # Hostels
        "The {thing} in my hostel room is {problem} since {duration} need repair",
        "Water is {problem} from the ceiling in room {location} please check",
        "The {thing} on the {location} floor is not working since last week",
        "My roommate and I have a {problem} situation need intervention from warden",
        "The {thing} in the hostel washroom is {problem} since {duration}",
        "Hostel room {location} has no {thing} it was promised during admission",
        "The {thing} near my bed is {problem} making it hard to sleep at night",
        "Common room {thing} is {problem} students are unable to use it",
        "The {thing} in the hostel kitchen is not working since {duration}",
        "There is a {problem} smell coming from the {location} in our hostel",
        "The {thing} supply in the hostel has been {problem} for the past week",
        "Hostel security is {problem} people are entering without checking ids",
        "The {thing} in my room is making loud noise throughout the night",
        "Washroom drainage in {location} is completely blocked water is overflowing",
        "The {thing} on the hostel roof is damaged and water leaks during rain",
        "Hostel wifi is extremely {problem} in room {location} need better signal",
        "The {thing} in the dining hall is {problem} students are complaining",
        "Pest control is needed in hostel block {location} there are {thing} everywhere",
        "The {thing} attached to the wall is loose and might fall anytime",
        "Hostel room door lock is {problem} cannot secure the room properly",
    ],
    2: [  # Academics (teacher, faculty, marks, exams)
        "The {person} is coming late to {thing} class every day missing lecture time",
        "{person} did not show up for the scheduled {thing} lecture today",
        "The {person} is not explaining {thing} properly students are struggling",
        "{thing} results are delayed by {duration} we need them for placement",
        "The {person} refused to accept my assignment saying it is {problem}",
        "{thing} timetable was changed without notice I missed my class",
        "The {person} is giving too much {thing} in one week impossible to complete",
        "My {thing} marks were entered wrongly in the portal please check",
        "The {person} is not responding to emails about the {thing} project",
        "Study material for {thing} is not uploaded on the LMS even now",
        "The {person} canceled the {thing} lecture without rescheduling it",
        "{thing} exam schedule has two papers on the same day please resolve",
        "The {person} marked me absent even though I attended the {thing} class",
        "Grade for {thing} is missing from my transcript need it for {duration}",
        "The {person} is taking extra classes during lunch break very inconvenient",
        "{thing} assignment deadline was moved forward by two days unfair",
        "The {person} is not giving proper feedback on the {thing} submissions",
        "Lab sessions for {thing} are too short cannot complete the experiments",
        "The {person} lost my answer sheet for the {thing} midterm exam",
        "Classroom for {thing} is too small many students have to stand outside",
        "The {person} asked irrelevant questions in the viva that were not in syllabus",
        "{thing} project groups were assigned unfairly I got no strong members",
        "The {person} is using outdated slides from last year for {thing} course",
        "Attendance for {thing} was marked wrong I was present that day",
        "The {person} gave a surprise test without informing anyone beforehand",
    ],
    3: [  # Fees / Finance
        "My {thing} fee payment is showing as pending even after deduction from bank",
        "The {amount} scholarship amount for this semester has not been credited",
        "{thing} refund has been delayed by {duration} the finance office is not responding",
        "The {thing} fee structure was increased without prior notice to students",
        "My {thing} payment receipt is not generated even after successful transaction",
        "Request for {thing} fee waiver due to family financial difficulties",
        "The {amount} tuition fee receipt has incorrect name please issue correction",
        "Hostel fee payment portal is {problem} not accepting any transaction",
        "My {thing} installment plan was rejected without any reason given",
        "The {amount} examination fee was deducted twice from my account please refund",
        "Scholarship disbursement for this month has not happened it is already late",
        "The {thing} fee counter is always closed during lunch hours inconvenient",
        "I paid the {amount} late fee but it still shows as unpaid on portal",
        "The {thing} payment gateway charges extra convenience fee every transaction",
        "My educational loan document has not been processed by the finance department",
        "The {amount} caution deposit refund is pending since my graduation last year",
        "Library fine of {amount} was charged incorrectly I returned the book on time",
        "The {thing} fee receipt format is not accepted by my company for reimbursement",
        "Registration fee for the {thing} course was not refunded after course cancel",
        "The finance portal is showing {amount} due but I already paid last month",
    ],
    4: [  # Maintenance
        "The {thing} in {location} is {problem} since {duration} needs immediate repair",
        "A {thing} is broken near the {location} it is a safety hazard for students",
        "The {thing} pipe in {location} burst last night water is flooding the corridor",
        "{location} lights have been {problem} for {duration} very dark at night",
        "The {thing} door is jammed in {location} cannot open or close it properly",
        "A {thing} fell from the ceiling in {location} narrowly missing a student",
        "The {thing} in the {location} washroom has been leaking for {duration}",
        "Paint is peeling off the walls in {location} looks very unprofessional",
        "The {thing} railing on the staircase in {location} is loose and dangerous",
        "Window in {location} is broken letting in rain water during storms",
        "The {thing} elevator in {location} has been out of service for {duration}",
        "A {thing} tile in the {location} floor is cracked students keep tripping",
        "The {thing} plug point in {location} is sparking when used need electrician",
        "Mosquito breeding is happening near the {location} due to stagnant water",
        "The {thing} gate at the entrance of {location} is not closing properly",
        "Garbage is piling up near the {location} not collected for {duration}",
        "The {thing} bench in {location} is broken with sharp edges exposed",
        "Water tank on the rooftop of {location} is leaking since last month",
        "The {thing} AC unit in {location} is not cooling making the room unbearable",
        "A {thing} pipe is making loud hammering noise in {location} every morning",
    ],
    5: [  # Transport
        "The college bus number {location} is always late in the morning",
        "Bus driver of route {location} is driving very rashly please take action",
        "The bus AC is not working on route {location} it is very hot inside",
        "Evening bus from {location} leaves early many students miss it",
        "There are no buses after 6 pm from {location} campus to the station",
        "The bus conductor on route {location} is rude to students everyday",
        "Seats in the college bus {location} are torn and uncomfortable",
        "The bus timing for route {location} was changed without informing anyone",
        "Bus stop at {location} has no shelter students stand in the sun",
        "The bus skipped the {location} stop today leaving 10 students waiting",
        "College bus number {location} is overcrowded students have to stand",
        "The bus engine on route {location} is making strange noises",
        "Bus driver does not stop at {location} even when students signal",
        "The bus fare for route {location} has increased without any notice",
        "GPS tracker on bus {location} is not working cannot track its location",
        "The bus door on route {location} does not close properly while moving",
        "Morning bus from {location} reaches campus after the first lecture starts",
        "The bus cleaner on route {location} does not clean the bus properly",
        "Bus route {location} was discontinued without informing the students",
        "The bus horn on route {location} is excessively loud and disturbing",
    ],
    6: [  # Security / Discipline
        "Someone stole my {thing} from the {location} during lunch break",
        "There was a {problem} incident near the {location} last night",
        "Suspicious person was seen roaming around {location} after college hours",
        "A {thing} was found damaged in the {location} by unknown persons",
        "Students are {problem} in the {location} every evening creating noise",
        "The security guard at {location} is not checking anyone's id cards",
        "A {thing} was left unattended near the {location} for hours",
        "There is {problem} happening behind the {location} every afternoon",
        "CCTV camera near the {location} has been broken for {duration}",
        "Some students are {problem} in the library disturbing others studying",
        "A stranger entered the hostel at {location} at night without check",
        "The {location} gate is left open at night creating a security risk",
        "A group of people are {problem} near the campus boundary wall",
        "My {thing} went missing from the {location} locker room yesterday",
        "The emergency exit door in {location} is broken and unguarded",
        "There is a {problem} situation in the parking lot near {location}",
        "The fire alarm in {location} was triggered by someone as a prank",
        "A {thing} was thrown from upstairs in {location} almost hit someone",
        "The security light in {location} has been {problem} for {duration}",
        "Students caught {problem} in the {location} need disciplinary action",
    ],
    7: [  # Administration
        "My {thing} application has been pending for {duration} no response yet",
        "The {person} in the administration office is {problem} with students",
        "I need a {thing} certificate urgently for my {duration} application",
        "The {thing} form on the website is {problem} cannot download or submit",
        "Office hours for {thing} are very limited cannot meet the {person}",
        "My {thing} request was rejected without any explanation",
        "The {person} lost my original documents submitted for {thing} verification",
        "There is no {thing} counter for international student queries",
        "The {thing} approval process takes too long more than {duration}",
        "The {person} in admissions is giving wrong information to students",
        "My degree certificate has a spelling mistake in my name on it",
        "The {thing} office phone number is always busy cannot get through",
        "Transfer certificate application has been stuck for {duration}",
        "The administration staff at {location} is very unhelpful and rude",
        "My {thing} document was misplaced by the office please trace it",
        "The {thing} renewal process requires too many documents every year",
        "The {person} asked for a bribe to process my {thing} application",
        "Online {thing} application portal is showing wrong status information",
        "The administration building {location} has no signboards confusing to find",
        "My {thing} was sent to the wrong department please forward correctly",
    ],
    8: [  # Library
        "The {thing} I need for my project is not available in the library",
        "Library fine of {amount} was charged incorrectly I returned on time",
        "The {thing} section in the library is always closed during lunch",
        "Library timing should be extended during exam week closes too early",
        "The {thing} books on the shelf are all old editions need new ones",
        "Noise level in the library reading hall is very high no one controls",
        "The library {thing} system is down cannot issue or return books",
        "I lost a {thing} book from the library how do I pay the penalty",
        "The library {thing} machine is not working cannot scan my id card",
        "Reference {thing} cannot be taken home but there are no copies inside",
        "The library staff at the {thing} counter is very rude and slow",
        "Digital library computers are all occupied during peak hours every day",
        "The {thing} journal I need is missing from the periodical section",
        "Library membership renewal is not processed even after {duration}",
        "There are not enough {thing} copies for the number of students enrolled",
        "The library toilet near the {location} is very dirty since {duration}",
        "Book return drop box is full cannot return my {thing} book",
        "The {thing} catalogue search on the website shows wrong shelf location",
        "Photocopy machine in the library is broken since {duration}",
        "The library does not have {thing} material for visually impaired students",
    ],
}

# Pool values for each category
POOLS = {
    # IT Support
    0: {
        'noun': ['wifi', 'network', 'internet', 'printer', 'laptop', 'computer', 'projector',
                  'vpn', 'email', 'portal', 'software', 'server', 'scanner', 'router', 'system',
                  'application', 'login page', 'website', 'database', 'antivirus'],
        'problem': ['not working', 'very slow', 'down', 'disconnecting', 'crashing',
                     'showing error', 'not responding', 'frozen', 'unreachable', 'broken',
                     'glitchy', 'malfunctioning', 'acting up', 'lagging', 'unstable'],
        'duration': ['morning', 'yesterday', 'last week', '3 days', 'a week', 'two weeks',
                      'the past month', 'this morning', 'last night', 'a few hours'],
        'location': ['library', 'lab 3', 'block a', 'computer lab', 'main building',
                      'cse department', 'seminar hall', 'auditorium', 'admin block', 'lecture hall'],
    },
    # Hostels
    1: {
        'thing': ['fan', 'water cooler', 'geyser', 'tube light', 'bed', 'almirah', 'chair',
                   'table', 'curtain', 'window', 'door', 'mirror', 'sink', 'toilet seat',
                   'shower head', 'exhaust fan', 'cctv camera', 'bell', 'bathroom tap', 'drain'],
        'problem': ['broken', 'leaking', 'not working', 'damaged', 'blocked', 'loose',
                     'rusted', 'cracked', 'stuck', 'faulty', 'defective', 'malfunctioning',
                     'corroded', 'disconnected', 'wobbly'],
        'duration': ['last week', 'three days', 'a month', 'two weeks', 'since moving in',
                      'last semester', 'yesterday', 'this morning', 'ten days', 'a fortnight'],
        'location': ['101', '202', '303', 'block a', 'block b', 'block c', 'ground floor',
                      'first floor', 'second floor', 'third floor', 'east wing', 'west wing'],
    },
    # Academics
    2: {
        'person': ['professor sharma', 'dr patel', 'the faculty', 'the lecturer',
                    'the teacher', 'the instructor', 'prof gupta', 'the course coordinator',
                    'the hod', 'the lab assistant', 'dr verma', 'the tutor'],
        'thing': ['assignment', 'project', 'lab report', 'lecture', 'course',
                   'exam', 'test', 'quiz', 'thesis', 'seminar', 'tutorial',
                   'workshop', 'internship', 'research paper', 'practical'],
        'problem': ['too strict', 'unfair', 'biased', 'unhelpful', 'wrong',
                     'incorrect', 'invalid', 'incomplete', 'confusing', 'outdated',
                     'disorganized', 'unreasonable', 'unclear', 'unjustified', 'missing'],
        'duration': ['one week', 'ten days', 'two weeks', 'a month', 'since last month',
                      'this semester', 'last semester', 'fifteen days', 'three weeks'],
    },
    # Fees / Finance
    3: {
        'thing': ['tuition fee', 'hostel fee', 'exam fee', 'library fee', 'bus fee',
                   'lab fee', 'registration fee', 'admission fee', 'caution deposit',
                   'sports fee', 'development fee', 'transfer fee', 'degree fee'],
        'amount': ['5000', '10000', '15000', '25000', '50000', '2000', '7500',
                    '12000', '30000', '8000', '4500', '20000', '35000', '6000'],
        'problem': ['not working', 'down', 'showing error', 'unavailable', 'blocked',
                     'rejected', 'failed', 'declined', 'timed out', 'inaccessible'],
        'duration': ['two weeks', 'one month', 'three weeks', 'ten days', 'fifteen days',
                      'since last semester', 'last month', 'a fortnight', 'since march'],
    },
    # Maintenance
    4: {
        'thing': ['water pipe', 'toilet', 'sink', 'window', 'door handle', 'light fixture',
                   'ceiling fan', 'air conditioner', 'bench', 'table', 'chair', 'gate',
                   'elevator', 'staircase railing', 'water cooler', 'washbasin', 'tap',
                   'flush', 'tank', 'drainage pipe'],
        'problem': ['broken', 'leaking', 'damaged', 'blocked', 'cracked', 'loose',
                     'jammed', 'burst', 'clogged', 'stuck', 'not working', 'faulty',
                     'rusted', 'shattered', 'detached', 'overflowing', 'sparking', 'flooding'],
        'duration': ['a week', 'two weeks', 'three weeks', 'a month', 'two months',
                      'since last year', 'last semester', 'many days', 'since january', 'ages'],
        'location': ['block a', 'block b', 'block c', 'main building', 'science block',
                      'cse department', 'library', 'auditorium', 'sports complex', 'canteen',
                      'admin block', 'lecture hall 1', 'lecture hall 2', 'lab 1', 'lab 2'],
    },
    # Transport
    5: {
        'location': ['a-block', 'main gate', 'city center', 'railway station', 'bus stand',
                      'hostel gate', 'campus gate', 'market road', 'river road', 'east campus',
                      'north campus', 'west gate', 'south hostel', 'main road', 'bypass'],
    },
    # Security / Discipline
    6: {
        'thing': ['laptop', 'phone', 'wallet', 'bag', 'bicycle', 'books', 'charger',
                   'headphones', 'watch', 'tablet', 'keys', 'id card', 'calculator',
                   'notebook', 'water bottle', 'umbrella', 'jacket', 'purse', 'pen drive'],
        'problem': ['suspicious', 'dangerous', 'unacceptable', 'concerning', 'illegal',
                     'unsafe', 'threatening', 'harassing', 'disturbing', 'violent',
                     'inappropriate', 'disruptive', 'unruly', 'mischievous', 'questionable'],
        'location': ['library', 'canteen', 'parking lot', 'hostel courtyard', 'sports ground',
                      'main entrance', 'back gate', 'computer lab', 'auditorium', 'garden area',
                      'staircase', 'corridor', 'basement', 'rooftop', 'cycle stand'],
        'duration': ['a week', 'two weeks', 'a month', 'several days', 'the past month',
                      'last semester', 'since last month', 'many evenings now', 'a while'],
    },
    # Administration
    7: {
        'thing': ['bonafide certificate', 'transfer certificate', 'degree', 'transcript',
                   'migration certificate', 'internship approval', 'noc', 'scholarship form',
                   'fee waiver application', 'hostel application', 'library card', 'id card',
                   'grade card', 'admission form', 'exam registration', 'course add drop',
                   'student verification', 'character certificate', 'study leave', 'attendance sheet'],
        'person': ['the clerk', 'the administrative officer', 'the registrar', 'the dean',
                    'the office assistant', 'the department secretary', 'the coordinator',
                    'the admission officer', 'the accounts manager', 'the front desk staff'],
        'problem': ['rude', 'unhelpful', 'unresponsive', 'careless', 'slow',
                     'incompetent', 'dismissive', 'uncooperative', 'inflexible', 'disorganized'],
        'duration': ['a month', 'three weeks', 'two months', '45 days', 'last semester',
                      'since june', 'over a month', 'several weeks', 'since registration'],
        'location': ['ground floor', 'first floor', 'admin block', 'admission office',
                      'accounts section', 'registrar office', 'front desk', 'room 101',
                      'academic block', 'main office'],
    },
    # Library
    8: {
        'thing': ['book', 'journal', 'textbook', 'reference book', 'novel', 'magazine',
                   'research paper', 'thesis', 'dictionary', 'encyclopedia', 'study material',
                   'question bank', 'handbook', 'manual', 'guide book', 'atlas', 'report',
                   'newspaper', 'periodical', 'cd rom'],
        'amount': ['50', '100', '200', '500', '1000', '150', '250', '750', '300', '20'],
        'problem': ['unhelpful', 'rude', 'slow', 'careless', 'unprofessional',
                     'dismissive', 'incompetent', 'ignorant', 'lazy', 'inflexible'],
        'duration': ['a week', 'two weeks', 'three weeks', 'a month', 'ten days', 'fifteen days',
                      'since last month', 'since january', 'a fortnight', 'this semester'],
        'location': ['reading hall', 'reference section', 'circulation desk', 'digital section',
                      'periodical area', 'staircase area', 'entrance lobby', 'basement section'],
    },
}

PRIORITIES = ['Low', 'Medium', 'High']
PRIORITY_ENCODED = {'Low': 1, 'Medium': 0, 'High': 2}

# Target new docs per category
TARGETS = {
    0: 50,   # IT Support: 100 -> 150
    1: 0,    # Hostels: already 100
    2: 36,   # Academics: 114 -> 150
    3: 0,    # Fees: already 100
    4: 0,    # Maintenance: already 100
    5: 0,    # Transport: already 100
    6: 30,   # Security: 100 -> 130
    7: 50,   # Administration: 100 -> 150
    8: 99,   # Library: 1 -> 100
}

def generate(cat, templates, pools):
    t = random.choice(templates)
    pool = pools.get(cat, {})
    # Extract placeholders from template
    parts = []
    i = 0
    while i < len(t):
        if t[i] == '{':
            end = t.index('}', i)
            key = t[i+1:end]
            if key in pool:
                val = random.choice(pool[key])
            else:
                val = f'[{key}]'
            parts.append(val)
            i = end + 1
        else:
            parts.append(t[i])
            i += 1
    return ''.join(parts)

# Load existing data
with open(DATA_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    existing = list(reader)
    fieldnames = reader.fieldnames

current_counts = {}
for r in existing:
    cat = int(r['category_encoded'])
    current_counts[cat] = current_counts.get(cat, 0) + 1

print("Before:")
for c in sorted(TARGETS.keys()):
    print(f"  {c} ({TEMPLATES[c][0][:30]}...): {current_counts.get(c, 0)} docs")

# Generate synthetic data
new_rows = []
for cat, target_add in TARGETS.items():
    templates = TEMPLATES[cat]
    pools = POOLS.get(cat, {})
    for _ in range(target_add):
        text = generate(cat, templates, pools)
        # Assign priority randomly
        prio = random.choice(PRIORITIES)
        new_rows.append({
            'text': text,
            'category': '',  # will fill below
            'priority': prio,
            'source': 'synthetic',
            'category_encoded': str(cat),
            'priority_encoded': str(PRIORITY_ENCODED[prio]),
        })

# Add category names via decoder
cat_decoder = {0: 'IT Support', 1: 'Hostels', 2: 'Academics', 3: 'Fees / Finance',
               4: 'Maintenance', 5: 'Transport', 6: 'Security / Discipline',
               7: 'Administration', 8: 'Library'}
for r in new_rows:
    r['category'] = cat_decoder[int(r['category_encoded'])]

# Append
all_rows = existing + new_rows

with open(DATA_PATH, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nAdded {len(new_rows)} synthetic complaints")
print(f"Total now: {len(all_rows)}")

print("\nAfter:")
for c in sorted(TARGETS.keys()):
    cnt = sum(1 for r in all_rows if int(r['category_encoded']) == c)
    print(f"  {c} ({cat_decoder[c]}): {cnt} docs")
