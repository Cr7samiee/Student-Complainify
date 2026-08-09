"""Generate and append balanced synthetic student-complaint rows (v5).

v5 builds multi-part sentences (opener + topic + bad + closer) from large
combinatorial pools so thousands of UNIQUE texts exist per class. Priority is
a DETERMINISTIC, text-only function (assign_priority): High/Medium/Low come
from class-locked phrase pools, so the label is exactly what the model can
learn from the words.

Modes:
    python generate_sentiment_priority_data.py            # top up missing classes
    python generate_sentiment_priority_data.py --rebuild  # relabel all rows + dedupe
    python generate_sentiment_priority_data.py --fresh    # keep only hand-written
        (source=claude) rows, regenerate all synthetic rows from scratch

Final file: data/sentiment_dataset.csv
"""

import csv
import random
import os
import re
import sys


def normalize(text):
    """Remove 'unwanted data' noise: control chars, stray spacing, latin dashes."""
    text = re.sub(r'[\x00-\x1f\x7f\u00ad]', '', text)
    text = text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2018', "'").replace('\u2019', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([,.!?\-:;])', r'\1', text)
    return text


# Sentiment convention: 'negative' is reserved for STRONG complaint language.
# Mild problem-reports ("issue", "not getting on time", "water coolers
# non-functional") are labeled 'neutral' — urgency is handled by priority.
STRONG_NEG = re.compile(
    r'\b(stol\w*|steal\w*|theft|robbery|harass\w*|abuse|threaten\w*|assault|'
    r'unsafe|unhygienic|filthy|rotten|stale|spoiled|foul|smelly|infest\w*|'
    r'disgust\w*|terribl\w*|horribl\w*|awful|broken|crack(?:ed)?|'
    r'leak(?:ing|s|ed)?|malfunction\w*|not\s+work(?:ing)?|not\s+fixed|'
    r'never\s+fixed|no\s+(?:response|reply|action|update)|'
    r'no\s+one\s+(?:responds|listens|cares)|nobody\s+(?:responds|listens|cares)|'
    r'ignored|ignor\w*|refus\w*|overcharg\w*|rude|delay(?:s|ed)?|serious|'
    r'emergency|danger\w*|damag\w*|unresolved|fight\w*|insult\w*|cheat\w*|'
    r'molest\w*)\b',
    re.IGNORECASE
)


def soften(rows):
    """Downgrade negative -> neutral when the text lacks strong complaint
    language (see STRONG_NEG). Deterministic: re-derives priority + polarity."""
    for r in rows:
        if r['sentiment_label'].strip().lower() == 'negative' \
                and not STRONG_NEG.search(r['complaint_text']):
            r['sentiment_label'] = 'neutral'
            r['priority'] = assign_priority(r['complaint_text'], 'neutral')
            r['polarity_score'] = str(polarity(r['complaint_text'], 'neutral'))
    return rows


def relabel(rows):
    """Re-decide priority on every row from its text (deterministic ground truth)."""
    seen = set()
    out = []
    for r in rows:
        r['complaint_text'] = normalize(r['complaint_text'])
        key = r['complaint_text'].lower()
        if len(r['complaint_text']) < 10 or key in seen:
            continue
        seen.add(key)
        r['sentiment_label'] = r['sentiment_label'].strip().lower()
        if r['sentiment_label'] not in ('positive', 'neutral', 'negative'):
            continue
        r['priority'] = assign_priority(r['complaint_text'], r['sentiment_label'])
        r['category'] = (r.get('category') or 'General/Suggestion').strip()
        out.append(r)
    return soften(out)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET = os.path.join(BASE, 'data', 'sentiment_dataset.csv')
SEED = 42
TARGET = 4000

CATEGORIES = sorted([
    'Library', 'Hostel/Accommodation', 'Infrastructure', 'Examination',
    'Academic', 'IT/Technical', 'Faculty/Staff Behavior', 'Canteen/Food',
    'General/Suggestion', 'Administrative',
])

TOPICS = {
    'Library': ['the printer kiosks in the eastern annex', 'the circulation reading room counter',
                'the online renewal system', 'the reading room lights', 'the photocopy counters',
                'the book drop counter', 'the reference section fans', 'the library entrance turnstiles'],
    'Hostel/Accommodation': ['the water supply in Block C', 'the bathroom fittings in the new floor',
                             'the common room appliances', 'the warden office timings', 'the laundry machine service',
                             'the corridor lights on second floor', 'the hostel room fans', 'the washroom drainage'],
    'Infrastructure': ['the drinking water coolers on campus', 'the main gate escalator',
                       'the auditorium lift', 'the balcony ramp', 'the campus footpaths',
                       'the street lights near the football field', 'the campus drainage network', 'the parking shades'],
    'Examination': ['the recheck process for answer scripts', 'the hall ticket download link',
                    'the result publication schedule', 'the supplementary exam form', 'the invigilation duty roster',
                    'the exam hall seating arrangement', 'the practical exam slots', 'the result verification desktops'],
    'Academic': ['the tutorial slot allocation', 'the assignment submission portal',
                 'the attendance portal', 'the project group selection', 'the lecture hall booking',
                 'the syllabus update notifications', 'the internal marks entry window', 'the lab batch timings'],
    'IT/Technical': ['the campus WiFi network', 'the lab systems in the computer lab',
                     'the single sign on portal', 'the projectors in lecture halls', 'the antivirus support team',
                     'the mobile data top-up system', 'the print server for labs', 'the biometric login scanner'],
    'Faculty/Staff Behavior': ['the behaviour of the front desk clerk', 'the response of the admissions office',
                               'the lab assistant attitude', 'the approach of the examination cell', 'the accounts desk responses',
                               'the sports office staff response', 'the hostel caretaker conduct', 'the placement cell handling'],
    'Canteen/Food': ['the food quality at the main canteen', 'the cleanliness of the serving counters',
                     'the meal price list', 'the afternoon lunch service', 'the coupon monitoring',
                     'the breakfast counter timings', 'the water jug refills', 'the cutlery hygiene'],
    'General/Suggestion': ['the suggestion box locations', 'the club activity registration',
                           'the event permits procedure', 'the volunteer requirement list', 'the feedback collection points',
                           'the orientation day arrangements', 'the college fest bookings', 'the notice board space'],
    'Administrative': ['the scholarship certificate issuance', 'the official transcript counter',
                       'the fee receipt correction window', 'the records verification service', 'the bonafide certificate service',
                       'the course registration desk', 'the college letter dispatch', 'the exam centre approvals'],
}

REQUESTS = {
    'Library': ['library membership for part time students', 'the photocopying policy',
                'the inter library loan procedure', 'the reference book renewal limits',
                'the e resource access policies', 'the grievance register location'],
    'Hostel/Accommodation': ['the room allotment process', 'the guest entry rules', 'the maintenance refund window',
                             'the curfew relaxation policy', 'the checkout formalities', 'the room transfer form'],
    'Infrastructure': ['the lift maintenance timetable', 'the lighting upgrade schedule',
                       'the drainage cleaning plan', 'the parking zone marking', 'the wall repair plan',
                       'the road resurfacing timeline'],
    'Examination': ['the marks correction window', 'the answer sheet viewing procedure',
                    'the grade recalculation timeline', 'the backlog subject form', 'the result verification steps',
                    'the revaluation deadline'],
    'Academic': ['the credit transfer policy', 'the elective selection procedure',
                 'the branch change form', 'the academic calendar circulars', 'the certificate request process',
                 'the attendance reversal window'],
    'IT/Technical': ['the VPN account request process', 'the licence approval process',
                     'the support ticket hours', 'the data restore procedure', 'the account activation steps',
                     'the wifi fault report form'],
    'Faculty/Staff Behavior': ['the complaint channel for staff conduct', 'the anonymous feedback process',
                               'the grievance escalation steps', 'the staff guidelines', 'the service standard document',
                               'the counselling hour details'],
    'Canteen/Food': ['the weekly menu schedule', 'the hygiene inspection details',
                     'the price revision policy', 'the refund window for missed meals', 'the portion size guidelines',
                     'the special meal order process'],
    'General/Suggestion': ['the event holiday calendar', 'the notice board permission process',
                           'the club funding rules', 'the guest speaker scheduling', 'the campus cleanup schedule',
                           'the fest stall allocation'],
    'Administrative': ['the certificate authentication process', 'the fee refund timeline',
                       'the transfer certificate procedure', 'the transcript request period',
                       'the verification letter format', 'the profile update form'],
}

POSITIVES = {
    'Library': ['the new e-book subscriptions', 'the renovated silent seating area',
                'the helpful circulation staff', 'the extended weekend hours', 'the upgraded catalogue search',
                'the smooth book return counter'],
    'Hostel/Accommodation': ['the cleaned common rooms', 'the quick window repairs', 'the polite caretaker team',
                             'the new water purifier', 'the upgraded common room lighting', 'the friendly complaints desk'],
    'Infrastructure': ['the new walkway panels', 'the renovated boundary walls',
                       'the new signboards in every block', 'the covered drainage channels', 'the pedestrian crossings',
                       'the freshly painted zebra crossings'],
    'Examination': ['the on time result publication', 'the transparent re-evaluation process',
                    'the improved exam seating', 'the updated admit card service', 'the clear evaluation criteria',
                    'the smooth result portal experience'],
    'Academic': ['the revised study structure', 'the recorded lecture facility',
                 'the approachable faculty mentors', 'the transparent grading policy',
                 'the helpful counselling hours', 'the improved lab manuals'],
    'IT/Technical': ['the improved network speed', 'the quick response of the IT team',
                     'the updated lab computers', 'the smoother login experience', 'the helpful digital portal',
                     'the responsive wifi setup team'],
    'Faculty/Staff Behavior': ['the courteous support at the helpdesk', 'the supportive mentoring approach',
                               'the friendly admission responses', 'the prompt replies of the faculty panel',
                               'the welcoming office tone', 'the fair seating assistance'],
    'Canteen/Food': ['the improved monthly menu', 'the cleaner serving counters',
                     'the faster lunch queues', 'the stable fixed price list', 'the hygienic ordering process',
                     'the quality control checks'],
    'General/Suggestion': ['the new courtyard seating', 'the redesigned notice boards',
                           'the responsive suggestions committee', 'the smoother campus entry', 'the updated orientation week',
                           'the well maintained restrooms'],
    'Administrative': ['the swift certificate verification', 'the new e office service',
                       'the upgraded front helpdesk', 'the clear fee notices', 'the courteous accounts staff',
                       'the helpful records section'],
}

NEG_OPENERS = [
    'This is a serious problem: ',
    'It is really disappointing that ',
    'Still facing the issue that ',
    'The condition of ',
    'I have tried several times but ',
    'Students here are badly affected because ',
    'This is at least the third time that ',
    'Honestly, nothing improves while ',
    'It bothers us every day that ',
    'My complaint remains unresolved because ',
    'The management is not listening while ',
    'It can no longer be ignored that ',
    'Warning signs were clear but ',
    'The situation with ',
]

# v5: bad-phrases and closers are class-locked so High/Medium text blocks
# never mix — the priority marker in the sentence IS the distinguishing
# vocabulary, which the model can learn exactly.
HIGH_BADS = [
    'remains completely unavailable',
    'has never been repaired',
    'stopped working again',
    'is out of order since morning',
]

MEDIUM_BADS = [
    'keeps getting delayed',
    'is still not working',
    'keeps breaking down',
    'is constantly under-maintained',
    'has not been fixed despite requests',
    'still does not function',
    'is not up to the expected standard',
    'has degraded further over time',
]

HIGH_CLOSERS = [
    ' and nothing has been done yet',
    ' and no one from the office follows up',
    ' and students have already reported it',
]

MEDIUM_CLOSERS = [
    ' since the start of the semester',
    ' for almost two weeks now',
    ' despite repeated complaints',
    ' again this month',
    ' with no date for repair available',
]

HIGH_OPENERS = [
    'This is a serious problem: ',
    'It can no longer be ignored that ',
    'Warning signs were clear but ',
]

NEG_CLOSERS = HIGH_CLOSERS + MEDIUM_CLOSERS
BAD_PHRASES = HIGH_BADS + MEDIUM_BADS

NEG_TAILS = [
    '.',
    '!',
    ' - please take it seriously.',
    ' - this is getting frustrating.',
    ' - kindly look into it at the earliest.',
]

NEU_OPENERS = [
    'Could you clarify the process for ',
    'Seeking clarification on ',
    'Kindly update the current policy for ',
    'I am looking for the exact procedure for ',
    'Requesting information about ',
    'Could you explain how ',
    'Please share the relevant circular for ',
    'Kindly confirm the required documents for ',
    'I would like to know the schedule for ',
    'When does the window for ',
    'Please guide me on the steps for ',
    'Is there any form for ',
    'Could you point me to the right authority for ',
    'May I know the current status of ',
]

NEU_SUFFIXES = [
    '?',
    ' Could you mail a copy of the policy?',
    ' If possible, share the office address as well.',
    ' Does it require prior appointment?',
    ' Are walk ins accepted?',
]

POS_OPENERS = [
    'Happy to report that ',
    'It is a pleasure to see that ',
    'Impressed that ',
    'Grateful to finally see ',
    'Very pleased that ',
    'Great news that ',
    'Commendable effort around ',
    'Delighted that ',
    'Really appreciate that ',
    'Satisfied that ',
    'A big thanks that ',
    'It truly helps that ',
    'Refreshing to note that ',
    'Good to see that ',
]

POS_TAILS = [
    ' – thanks to the concerned team.',
    ' and the turnaround was quick.',
    ' – our sincere thanks.',
    ' and the effort shows.',
    ' – the improvement is visible.',
    ' we really valued the support.',
]

URGENT_HINTS = ['emergency', 'danger', 'unsafe', 'stale', 'unhygienic', 'harass',
                'theft', 'leak', 'no water', 'serious']

# Deterministic, explainable priority rule (v5):
#   negative  -> High if a severity/urgency marker appears, else Medium
#   neutral   -> Medium if a deadline/window/timeline/form/schedule noun appears, else Low
#   positive  -> Low  (never promoted — thank-you content is not urgent)
# The marker vocabulary is exactly the vocabulary the generator uses, and
# High/Medium blocks never mix within a sentence (class-locked pools above).
HIGH_HINTS = (
    HIGH_BADS + [c.strip() for c in HIGH_CLOSERS] + [o.strip().rstrip(': ') for o in HIGH_OPENERS]
    + ['emergency', 'danger', 'unsafe', 'stale', 'unhygienic', 'harass',
       'theft', 'leak', 'no water', 'life threatening', 'injury']
)

NEU_MEDIUM_HINTS = [
    'deadline', 'window', 'timeline', 'form', 'schedule',
]

PRIORITY_WEIGHTS = {
    'negative': {'High': 0.42, 'Medium': 0.38, 'Low': 0.20},
    'neutral': {'High': 0.06, 'Medium': 0.34, 'Low': 0.60},
    'positive': {'High': 0.02, 'Medium': 0.30, 'Low': 0.68},
}

POS_WORDS = ['good', 'thank', 'great', 'satisfied', 'pleased', 'impressed', 'grateful', 'delighted',
             'happy', 'appreciate', 'improve', 'fixed', 'resolved']
NEG_WORDS = ['problem', 'broken', 'delay', 'unavailable', 'complaint', 'ignored', 'rude',
             'not working', 'not fixed', 'stale', 'unhygienic', 'unresolved', 'serious']


def polarity(text, sentiment):
    low = text.lower()
    pos = sum(1 for w in POS_WORDS if w in low)
    neg = sum(1 for w in NEG_WORDS if w in low)
    score = round((pos - neg) * 0.4, 3)
    if sentiment == 'positive' and score < 0.3:
        score = 0.35
    if sentiment == 'negative' and score > -0.3:
        score = -0.35
    if sentiment == 'neutral':
        score = max(-0.2, min(0.2, score))
    return round(max(-1.0, min(1.0, score)), 3)


def assign_priority(text, sentiment):
    """v5: priority is a deterministic, text-only function of the complaint.

    No randomness — the same sentence always maps to the same label, and the
    marker vocabulary (High/Medium phrase pools) never mixes within a
    sentence, so the priority rule is exactly what the trained model learns.
    """
    low = ' ' + text.lower() + ' '
    if sentiment == 'positive':
        return 'Low'
    if sentiment == 'neutral':
        return 'Medium' if any(m in low for m in NEU_MEDIUM_HINTS) else 'Low'
    if any(h in low for h in HIGH_HINTS):
        return 'High'
    return 'Medium'


def pick_priority(text, sentiment):
    return assign_priority(text, sentiment)


def make_text(sent, rng):
    cat = rng.choice(CATEGORIES)
    if sent == 'negative':
        topic = rng.choice(TOPICS[cat])
        high = rng.random() < 0.55
        if high:
            opener = rng.choice(HIGH_OPENERS)
            bad = rng.choice(HIGH_BADS)
            closer = rng.choice(HIGH_CLOSERS)
        else:
            opener = rng.choice([o for o in NEG_OPENERS if o not in HIGH_OPENERS])
            bad = rng.choice(MEDIUM_BADS)
            closer = rng.choice(MEDIUM_CLOSERS)
        red = opener + topic + ' ' + bad + closer + rng.choice(NEG_TAILS)
    elif sent == 'neutral':
        req = rng.choice(REQUESTS[cat])
        red = rng.choice(NEU_OPENERS) + req + rng.choice(NEU_SUFFIXES)
    else:
        topic = rng.choice(POSITIVES[cat])
        red = rng.choice(POS_OPENERS) + topic + rng.choice(POS_TAILS)
    return cat, red


def main():
    rebuild = '--rebuild' in sys.argv
    fresh = '--fresh' in sys.argv
    rng = random.Random(SEED)
    if rebuild or fresh:
        with open(DATASET, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            raw = list(reader)
        if fresh:
            raw = [r for r in raw if r.get('source', 'claude') == 'claude']
            print('fresh mode: keeping', len(raw), 'claude rows only')
        rows = relabel(raw)
        print('cleaned rows:', len(rows), '(from', len(raw), ')')
        with open(DATASET, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print('rewrote', DATASET)
        for r in rows:
            r['source'] = r.get('source', 'claude')
    else:
        with open(DATASET, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)
            rows = list(reader)

    seen = {r['complaint_text'].strip().lower() for r in rows}
    counts = {}
    for r in rows:
        key = r['sentiment_label'].lower()
        counts[key] = counts.get(key, 0) + 1

    gap = {k: max(0, TARGET - counts.get(k, 0)) for k in ('positive', 'neutral', 'negative')}
    print('existing counts:', counts)
    print('gap to generate :', gap)

    new_rows = []
    next_id = len(rows) + 1
    guard = 0
    while sum(gap.values()) > 0 and guard < 2_000_000:
        guard += 1
        sent = rng.choice([k for k, v in gap.items() if v > 0])
        cat, text = make_text(sent, rng)
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        new_rows.append({
            'complaint_id': 'C{:04d}'.format(next_id),
            'complaint_text': text,
            'category': cat,
            'sentiment_label': sent,
            'polarity_score': str(polarity(text, sent)),
            'priority': pick_priority(text, sent),
            'source': 'synth',
        })
        next_id += 1
        gap[sent] -= 1
        if len(new_rows) % 2000 == 0:
            print('...', len(new_rows), 'generated')

    if guard >= 2000000:
        print('WARNING: guard limit hit, remaining gap:', gap)

    with open(DATASET, 'a', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        for r in new_rows:
            w.writerow(r)

    print('generated:', len(new_rows), '| total rows now:', len(rows) + len(new_rows))
    final = {}
    final_pri = {}
    with open(DATASET, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            k = r['sentiment_label'].lower()
            final[k] = final.get(k, 0) + 1
            p = r['priority'].lower()
            final_pri[p] = final_pri.get(p, 0) + 1
    print('final sentiment:', final)
    print('final priority :', final_pri)


if __name__ == '__main__':
    main()