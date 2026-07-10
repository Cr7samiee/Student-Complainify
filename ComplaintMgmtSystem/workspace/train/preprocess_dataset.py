import pandas as pd
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRAIN_DIR = os.path.join(BASE_DIR, "TrainDataset")
OUTPUT_DIR = os.path.join(BASE_DIR, "workspace", "train")

# Load dataset #1
df1 = pd.read_csv(os.path.join(TRAIN_DIR, "university_complaint_triage_dataset.csv"))
df1 = df1.rename(columns={"text": "complaint_text", "department": "category", "urgency": "priority"})
df1["source"] = "complaint_triage"

# Load dataset #2
df2 = pd.read_csv(os.path.join(TRAIN_DIR, "university_query_test.csv"))
df2 = df2.rename(columns={"Student_Query": "complaint_text", "Department": "category", "Priority_Label": "priority"})
df2 = df2.drop(columns=["Query_ID", "Days_To_Deadline"], errors="ignore")
df2["source"] = "query_test"

# Combine
df = pd.concat([df1, df2], ignore_index=True)

# Normalize category names
category_map = {
    "Academic Office": "Academics",
    "Examination Cell": "Academics",
    "Finance Office": "Fees / Finance",
    "Hostel Office": "Hostels",
    "Administration": "Administration",
    "IT Support": "IT Support",
    "Library": "Library",
    "Hostels": "Hostels",
    "Academics": "Academics",
    "Fees / Finance": "Fees / Finance",
    "Maintenance": "Maintenance",
    "Transport": "Transport",
    "Security / Discipline": "Security / Discipline",
}
df["category"] = df["category"].map(category_map).fillna(df["category"])

# Standardize priority
df["priority"] = df["priority"].str.strip().str.title()

# Clean text
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()

df["complaint_text"] = df["complaint_text"].apply(clean_text)

# Remove empty
df = df[df["complaint_text"].str.len() > 0].reset_index(drop=True)

# Save
output_path = os.path.join(OUTPUT_DIR, "training_dataset.csv")
df.to_csv(output_path, index=False)

print(f"Original #1 rows: {len(df1)}")
print(f"Original #2 rows: {len(df2)}")
print(f"Combined clean rows: {len(df)}")
print(f"\nCategory distribution:")
print(df["category"].value_counts().to_string())
print(f"\nPriority distribution:")
print(df["priority"].value_counts().to_string())
print(f"\nSaved to: {output_path}")
