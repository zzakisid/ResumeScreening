from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import webbrowser
from threading import Timer
from datetime import datetime

app = Flask(__name__, static_folder="static", template_folder="templates")

THEME = {
    "primary": "#4b6cb7",  # Changed to match CSS
    "secondary": "#182848",
    "accent": "#dc2626",
    "light": "#f8fafc",
    "dark": "#1e293b",
    "success": "#16a34a",
    "warning": "#d97706",
    "danger": "#b91c1c",
}


def get_enhanced_similarity(job_desc, resumes):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 3))  # Add ngrams
    corpus = [job_desc] + resumes
    tfidf_matrix = vectorizer.fit_transform(corpus)
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

    # Enhanced keyword boosting
    tech_keywords = {
        "python": 0.25,  # Increased weights
        "java": 0.2,
        "aws": 0.15,
        "machine learning": 0.3,
        # Add more domain-specific keywords
    }

    # Add skill synonyms
    synonyms = {
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "js": "javascript",
    }

    enhanced_scores = []
    for score, resume in zip(scores, resumes):
        boost = 1.0
        resume_lower = resume.lower()
        job_desc_lower = job_desc.lower()

        # Check both original and synonym terms
        for term, weight in tech_keywords.items():
            if (term in job_desc_lower and term in resume_lower) or (
                term in job_desc_lower and synonyms.get(term, "") in resume_lower
            ):
                boost += weight

        enhanced_scores.append(min(1.0, score * boost * 100))  # Scale to percentage

    return enhanced_scores


@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/Help")
def help():
    return render_template("help.html")

@app.route("/Setting")
def setting():
    return render_template("setting.html")

@app.route("/match", methods=["POST"])
def match_resume():
    """API endpoint for resume matching"""
    try:
        start_time = datetime.now()

        if "resume" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files["resume"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        try:
            all_resumes = pd.read_csv(file)
            if all_resumes.empty:
                return jsonify({"success": False, "error": "Empty CSV file"}), 400

            if (
                "Category" not in all_resumes.columns
                or "Resume" not in all_resumes.columns
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Missing required columns (Category, Resume)",
                        }
                    ),
                    400,
                )
        except Exception as e:
            return jsonify({"success": False, "error": f"CSV Error: {str(e)}"}), 400

        software_categories = [
            "Python Developer",
            "Java Developer",
            "Data Scientist",
            "DevOps Engineer",
            "ML Engineer",
            "Full Stack Developer",
            "Backend Engineer",
            "Data Engineer",
            "Cloud Architect",
        ]

        resumes = all_resumes[all_resumes["Category"].isin(software_categories)]

        if resumes.empty:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No software resumes found",
                        "available_categories": all_resumes["Category"]
                        .unique()
                        .tolist(),
                    }
                ),
                400,
            )

        resumes = resumes.to_dict("records")

        try:
            jobs = pd.read_csv("jobDescriptions.csv")
            if jobs.empty or "Description" not in jobs.columns:
                return (
                    jsonify(
                        {"success": False, "error": "Invalid job descriptions file"}
                    ),
                    400,
                )
            job_desc = jobs.iloc[0]["Description"]
        except Exception as e:
            return (
                jsonify(
                    {"success": False, "error": f"Job Descriptions Error: {str(e)}"}
                ),
                400,
            )

        resume_texts = [r["Resume"] for r in resumes]
        scores = get_enhanced_similarity(job_desc, resume_texts)

        if not scores or len(scores) != len(resumes):
            return jsonify({"success": False, "error": "Scoring failed"}), 500

        results = []
        for i, score in enumerate(scores):
            results.append(
                {
                    "id": str(resumes[i].get("ID", i + 1)),
                    "name": str(resumes[i].get("Name", "")),
                    "category": str(resumes[i].get("Category", "")),
                    "score": round(float(score) * 100, 2),
                    "experience": str(resumes[i].get("Experience", "")),
                    "skills": str(resumes[i].get("Key Skills", "")),
                }
            )

        if not results:
            return jsonify({"success": False, "error": "No valid results"}), 400

        results.sort(key=lambda x: x["score"], reverse=True)

        response = {
            "success": True,
            "job_title": str(jobs.iloc[0].get("Title", "Software Position")),
            "job_company": str(jobs.iloc[0].get("Company", "")),
            "matches": results[:20],
            "stats": {
                "total_resumes": len(all_resumes),
                "filtered": len(resumes),
                "avg_score": round(sum(r["score"] for r in results) / len(results), 2),
                "processing_time": round(
                    (datetime.now() - start_time).total_seconds(), 2
                ),
            },
        }

        if results:
            response["top_candidate"] = results[0]

        return jsonify(response)

    except Exception as e:
        app.logger.error(f"System error: {str(e)}")
        return jsonify({"success": False, "error": f"System Error: {str(e)}"}), 500


def open_browser():
    """Open browser automatically when app starts"""
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    # Create sample files if they don't exist
    if not os.path.exists("resumes.csv"):
        with open("resumes.csv", "w") as f:
            f.write(
                "ID,Name,Category,Experience,Key Skills,Resume\n"
                '1,John Doe,Python Developer,5 years,"Python, Django, AWS","Experienced Python developer with Django experience"\n'
                '2,Jane Smith,Data Scientist,3 years,"Python, Machine Learning, SQL","Data scientist with ML experience"'
            )

    if not os.path.exists("jobDescriptions.csv"):
        with open("jobDescriptions.csv", "w") as f:
            f.write(
                "Title,Company,Description\n"
                'Python Developer,Tech Corp,"Looking for Python developer with Django and AWS experience"\n'
                'Data Scientist,Data Inc,"Seeking data scientist with machine learning skills"'
            )

    Timer(0, open_browser).start()
    app.run(debug=True)