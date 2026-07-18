import csv, os, random

random.seed(42)
BASE = 'E:/Project-VI/workspace/ComplaintMgmtSystem/TrainDataset'
SRC = os.path.join(BASE, 'processed_dataset_815.csv')
DST = os.path.join(BASE, 'processed_dataset_965.csv')

with open(SRC, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    existing = list(reader)
    fields = reader.fieldnames

# 150 unrelated "Other" complaints that should NOT match any category
PRIOS = ['Low','Medium','High']
PRIO_ENC = {'Low': 1, 'Medium': 0, 'High': 2}

OTHER_TEXTS = [
    "I want to order pizza in the campus canteen",
    "College football match timings for this weekend",
    "Can someone recommend a good phone repair shop near college",
    "Where can I get the bus pass for local city transport",
    "The weather is too hot these days need AC in classroom",
    "Movie screening in auditorium this friday timings please",
    "Lost my water bottle in the playground blue color",
    "Any cricket tournament happening this semester",
    "Canteen food prices are too high need reduction",
    "Where is the lost and found office located in campus",
    "College fest date announced need volunteers for event",
    "Photography competition registration link not working",
    "Hackathon event next month how to register team",
    "The college app is showing wrong timetable for today",
    "Where can I get my bike repaired inside campus",
    "Campus wifi password for guest visitors",
    "The gym equipment is old need new machines",
    "Yoga classes timings in the sports complex",
    "Swimming pool closed for maintenance since last week",
    "College magazine submissions last date extended",
    "Cultural fest dance competition registration details",
    "Can we get a coffee vending machine in the library",
    "The ATM near the main gate is out of cash since yesterday",
    "College website home page has broken links",
    "Student discount card for local restaurants",
    "Where is the parking for two wheelers in campus",
    "Blood donation camp dates for this month",
    "NSS volunteer registration form link please",
    "College annual day function date and chief guest",
    "Tech fest workshop on artificial intelligence registration",
    "How to apply for student exchange program",
    "Internship opportunity at google for cse students",
    "The basketball court lights are not working at night",
    "College tie up with foreign universities for semester abroad",
    "Student council election dates and nomination forms",
    "The campus garden needs more benches for sitting",
    "ATM card blocked how to get new one from bank",
    "Where is the college medical room and its timings",
    "Anti ragging committee contact number and email id",
    "Career counseling cell timings and counselor name",
    "College timing change for summer session",
    "Holiday list for this academic year please share",
    "The canteen tea is too sweet need less sugar",
    "Volleyball court net is torn need replacement",
    "College bus for industrial visit to bangalore",
    "Where can I buy college uniform and books",
    "The college stadium flood lights are not working",
    "Online teaching platform zoom link not working",
    "How to change my branch from cse to ece",
    "College id card lost how to apply for duplicate",
    "Timetable for practical exams not uploaded yet",
    "Where is the chairman office and visiting hours",
    "Medical certificate format for leave application",
    "College parking sticker renewal process",
    "The canteen accepts only cash need digital payment",
    "College alumni meet date and venue details",
    "The drinking water in block c has bad taste",
    "Sports day events list and registration link",
    "Where to submit the fee receipt for verification",
    "College bus route map for all city routes",
    "The college wifi blocks instagram and youtube",
    "How to apply for education loan from bank",
    "Bank account opening for scholarship students",
    "The corridor lights in block a are very dim",
    "Campus placement training classes timings",
    "Soft skills workshop for final year students",
    "The projector in seminar hall has blurry image",
    "College main gate security checking bags everyday",
    "How to get bonafide certificate for passport",
    "The smart board in room 204 is not calibrated",
    "College app notifications not coming to my phone",
    "Where is the staff room for mechanical department",
    "The garden near library has too many mosquitoes",
    "Student grievance portal login not working",
    "College fest ticket price and online booking",
    "The lift in admin block is not working from monday",
    "How to get no objection certificate for internship",
    "The campus map is not available on the website",
    "College timing for summer vacation and holidays",
    "The scanner in the admin office is paper jam",
    "Where to get the examination hall ticket printed",
    "College bus fees refund for unused months",
    "The laptop charging port in library not working",
    "How to apply for semester break and vacation",
    "Study tour to goa for marine biology students",
    "The chemistry lab equipment is not maintained",
    "College uniform tailor shop recommended near campus",
    "Water cooler in sports complex not working since friday",
    "The college cctv footage request procedure",
    "How to check my attendance percentage online",
    "The college helpline number is always busy",
    "Guest house booking for parents visiting campus",
    "The WiFi in the hostel block is very slow at night",
    "College magazine editorial team selection process",
    "The biometric attendance machine not reading fingerprint",
    "Where is the principal office and meeting hours",
    "College holiday on account of local festival",
    "The chemistry lab safety equipment is missing",
    "How to get the syllabus for third year subjects",
    "College auditorium booking for club events",
    "The electrical lab has insufficient power sockets",
    "How to register for value added courses",
    "The college ncc unit recruitment dates please",
    "Civil engineering lab equipment calibration status",
    "The wifi router in block b is making noise",
    "How to get my degree certificate attested",
    "College tie up with coursera for online courses",
    "The sports ground grass needs cutting and maintenance",
    "Where to submit the project report for evaluation",
    "The civil engineering drawing hall needs new tables",
    "How to change my examination center for final exam",
    "College bus service during weekend and holidays",
    "The electrical engineering lab has safety issues",
    "Where is the pharmacy and medical store in campus",
    "The canteen tables are very dirty need cleaning",
    "How to apply for semester abroad program",
    "College uniform stitching shop near campus",
    "The computer lab keyboard keys are missing",
    "Where to get the scholarship sanction letter",
    "College placement preparation materials online",
    "The civil works near library making too much noise",
    "Industry visit to microsoft office organized by college",
    "College tie up with aws for cloud computing training",
    "The robotics lab equipment is outdated need upgrade",
    "How to apply for hostel room change request",
    "College fest cultural events list and schedule",
    "The digital board in physics lab has dead pixels",
    "Where is the college discipline committee office",
    "College holiday list for diwali and holi festival",
    "Mathematics lab software license expired cannot use",
    "How to get the college leaving certificate after course",
    "The ncc training camp schedule for this month",
    "College tie up with google for student certifications",
    "The plumbing in the chemistry lab sink is leaking",
    "Photocopy shop near college open on sunday",
    "Civil engineering surveying equipment is damaged",
    "Where is the internal complaints committee office",
]

other_rows = []
for txt in OTHER_TEXTS:
    p = random.choice(PRIOS)
    other_rows.append({'text': txt, 'category': 'Other', 'priority': p,
                       'source': 'synthetic_other', 'category_encoded': '9',
                       'priority_encoded': str(PRIO_ENC[p])})

all_rows = existing + other_rows
with open(DST, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader(); w.writerows(all_rows)

print(f'Added {len(other_rows)} Other rows, total {len(all_rows)}')
before = {}
for r in existing:
    c = int(r['category_encoded'])
    before[c] = before.get(c, 0) + 1
print('Before:', dict(sorted(before.items())), f'(total {len(existing)})')
after = {}
for r in all_rows:
    c = int(r['category_encoded'])
    after[c] = after[c] + 1 if c in after else 1
print('After:', dict(sorted(after.items())), f'(total {len(all_rows)})')
