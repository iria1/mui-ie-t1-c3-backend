import re
from nltk.sentiment import SentimentIntensityAnalyzer
from better_profanity import profanity

# Initialize sentiment analyzer
sid = SentimentIntensityAnalyzer()

# Kid-friendly explanations with advice
EXPLANATIONS = {
    1: "This word may sound a bit unkind. Be careful when using it.",
    2: "This word may be hurtful. Try not to use it."
}

def clean_token_for_lookup(token: str) -> str:
    # Lowercase
    token = token.lower()
    # Remove leading hashtags/mentions
    token = re.sub(r"^[#@]+", "", token)
    # Strip surrounding punctuation but keep word inside
    token = token.strip(".,!?;:'\"()[]{}")
    return token

def analyze_text_words(text):
    lines = text.splitlines()
    all_results = []

    for i, line in enumerate(lines, start=1):
        tokens = line.split()
        line_results = []

        for word in tokens:
            lookup_word = clean_token_for_lookup(word)
            score = sid.polarity_scores(lookup_word)["compound"]
            label = 0

            if -0.50 < score < -0.44:
                label = 1
            elif score <= -0.50:
                label = 2

            if profanity.contains_profanity(word) or profanity.contains_profanity(lookup_word):
                label = 2

            if label == 1 and not profanity.contains_profanity(word) and not profanity.contains_profanity(lookup_word):
                label = 0

            explanation = EXPLANATIONS.get(label, None)
            line_results.append({
                "word": word,
                "label": label,
                "explanation": explanation
            })

        all_results.append({
            "line": i,
            "content": line,
            "tokens": line_results
        })

    return all_results