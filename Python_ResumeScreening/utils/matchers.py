from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_enhanced_similarity(job_desc, resumes):
    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        corpus = [job_desc] + resumes
        tfidf_matrix = vectorizer.fit_transform(corpus)
        scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        tech_keywords = {
            "python": 0.15,
            "java": 0.12,
            "aws": 0.1,
            "docker": 0.1,
            "kubernetes": 0.1,
        }

        enhanced_scores = []
        for score, resume in zip(scores, resumes):
            boost = 1.0
            for kw, weight in tech_keywords.items():
                if kw in job_desc.lower() and kw in resume.lower():
                    boost += weight
            enhanced_scores.append(min(1.0, score * boost))

        return enhanced_scores
    except Exception:
        return None
