import pandas as pd
from pathlib import Path


def load_resumes_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.where(pd.notnull(df), None).to_dict("records")
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return []


def combine_resume_text(resume):
    return resume["Resume_str"]
