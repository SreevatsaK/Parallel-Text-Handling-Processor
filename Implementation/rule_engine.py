import re
from collections import Counter


# Sentiment words
POSITIVE_WORDS = {
    "growth", "profit", "improved", "success",
    "breakthrough", "record", "strong", "confidence",
    "won", "secured", "celebrated", "increase"
}

NEGATIVE_WORDS = {
    "decline", "failure", "crash", "error",
    "issue", "problem", "crisis", "breach",
    "protest", "loss", "conflict", "slowdown"
}


# Thematic classification words
THEME_GROUPS = {
    "Economy": {"market", "inflation", "gdp", "economy", "currency", "growth"},
    "Politics": {"government", "minister", "parliament", "policy", "election"},
    "Technology": {"software", "ai", "technology", "platform", "system"},
    "Sports": {"team", "match", "league", "coach", "tournament"},
    "World": {"international", "global", "summit", "organization", "conflict"}
}


def analyze_chunk(text):

    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)

    positive_count = sum(word_counts[w] for w in POSITIVE_WORDS if w in word_counts)
    negative_count = sum(word_counts[w] for w in NEGATIVE_WORDS if w in word_counts)

    sentiment_score = positive_count - negative_count

    if sentiment_score > 0:
        sentiment_label = "Positive"
    elif sentiment_score < 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # -------- THEME DETECTION --------
    detected_themes = []

    for theme, keywords in THEME_GROUPS.items():
        if any(word in keywords for word in words):
            detected_themes.append(theme)

    # If no theme detected, assign "General"
    if not detected_themes:
        detected_themes.append("General")

    return {
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label,
        "themes": detected_themes
    }