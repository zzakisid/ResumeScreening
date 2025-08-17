from utils.parsing import load_resumes_csv, combine_resume_text


# Load resumes
resumes = load_resumes_csv("Resume.csv")

# Process all resumes
resume_texts = [combine_resume_text(r) for r in resumes]

# Use with your matcher
from utils.matchers import get_tfidf_similarity

job_desc = "Python developer with cloud experience"
scores = get_tfidf_similarity(job_desc, resume_texts)


import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.parsing import load_resumes_csv, combine_resume_text


# Test 1: Check CSV loading
def test_load_resumes():
    test_csv = "Resume.csv"  # Update path if needed
    resumes = load_resumes_csv(test_csv)
    assert isinstance(resumes, list), "Should return a list"
    print(f"✓ Loaded {len(resumes)} resumes")


# Test 2: Check text combination
def test_combine_text():
    sample_resume = {
        "skills": "Python, SQL",
        "experience": "5 years",
        "education": None,  # Test missing field
    }
    combined = combine_resume_text(sample_resume)
    assert "Python" in combined, "Skills should be included"
    assert "None" not in combined, "Should skip None values"
    print(f"✓ Combined text: {combined[:50]}...")


if __name__ == "__main__":
    test_load_resumes()
    test_combine_text()
    print("All tests passed!")
