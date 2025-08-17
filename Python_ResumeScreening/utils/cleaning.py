import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download("punkt")
nltk.download("stopwords")


def clean_text(text):
    """Basic text cleaning without SpaCy."""
    # Lowercase + remove special chars
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())

    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    return " ".join([word for word in tokens if word not in stop_words])
