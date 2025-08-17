import pandas as pd


def verify_data():
    resumes = pd.read_csv("Resume.csv")
    jobs = pd.read_csv("jobDescriptions.csv")

    print("Resume columns:", resumes.columns.tolist())
    print("Job columns:", jobs.columns.tolist())
    print(
        "\nSample resume text:", resumes["Resume_str"].iloc[0][:100], "..."
    )  # Changed to Resume_str
    print("Sample job desc:", jobs["Description"].iloc[0])


verify_data()
