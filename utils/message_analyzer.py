import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from better_profanity import profanity
import pandas as pd
import numpy as np
import re
import html
import joblib

# Kid-friendly explanations with advice
EXPLANATIONS = {
    1: "This word may sound a bit unkind. Be careful when using it.",
    2: "This word may be hurtful. Try not to use it."
}

SUGGESTION_RECIPIENT = {
    0: "<p style=\"margin-block-end:0px;\">The text may include unfriendly or slightly negative words considered as \"Not Cool\". Although it is not deeply offensive terms, it still can hurt others. The risk score indicates that the language as unfriendly but not necessary as bullying.</p>",
    1: "<p style=\"margin-block-end:0px;\">The text contains harmful words that are considered as \"No Go\". This makes the message highly offensive and emotionally damaging. The risk score indicates that the language could hurt feelings, lower self-esteem, and be seen as bullying.</p>"
}

SUGGESTION_SENDER = {
    0: "<p style=\"margin-block-end:0px;\">If the message feels uncomfortable, try to understand the context first.<br>Here's what you can do:</p><ol style=\"margin-block-end:0px;\"><li>If it's a misunderstanding, you can calmly ask, \"Did you mean that in a bad way?\"</li><li>If it continues, talk to a friend or adult.</li><li>Do not overreact if it seems like a small disagreement.</li></ol><p style=\"margin-block-end:0px;\"><strong>How to Respond:</strong> Try to stay calm and don't take it personally. Ask politely what they mean or simply move on.</p>",
    1: "<p style=\"margin-block-end:0px;\">If you see a message like this, do not reply with anger. Here's what you can do:</p><ul style=\"margin-block-end:0px;\"><li>Take a screenshot for evidence.</li><li>Block or mute the sender.</li><li>Report it to a parent, teacher, or trusted adult.</li><li>Remember that hurtful words say more about the bully than about you.</li></ul><p style=\"margin-block-end:0px;\"><strong>How to Respond:</strong> Instead of answering back, say nothing, save the proof, and show it to your teacher, parent or trusted adults.</p>"
}

# Regex patterns
USER_RE = re.compile(r"@\w+")
URL_RE = re.compile(r'(?i)\b(?:https?://|www\.)?[a-z0-9-]+\.[a-z0-9-]{2,}(?:/[^ \n]*)?\b')

DEFAULT_WEIGHTS = {"handcrafted": 0.2, "tfidf": 0.8}

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

            if label == 0:
                if profanity.contains_profanity(word) or profanity.contains_profanity(lookup_word):
                    label = 2

            # if label == 1 and not profanity.contains_profanity(word) and not profanity.contains_profanity(lookup_word):
            #     label = 0

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

def clean_text(text: str) -> str:
    """Clean and normalize tweet-like text, removing non-ASCII characters."""
    if not isinstance(text, str):
        return ""

    # Decode HTML entities (&amp; -> &)
    text = html.unescape(text)

    # Replace mentions with <USER>
    text = USER_RE.sub(" <USER> ", text)

    # Replace URLs with <URL>
    text = URL_RE.sub(" <URL> ", text)

    # Lowercase
    text = text.lower()

    # Remove non-ASCII characters (emojis, accented letters, etc.)
    text = text.encode("ascii", "ignore").decode()

    # Keep only letters, numbers, hashtags, <URL>, <USER>, ?, !
    text = re.sub(r"[^a-z0-9#<>!? ]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

def avg_word_length(text):
    words = str(text).split()
    return np.mean([len(w) for w in words]) if words else 0

def num_exclamations(text):
    return str(text).count("!")

def profanity_count(text):
    words = str(text).split()
    return sum(1 for w in words if profanity.contains_profanity(w))

def all_caps_ratio(text):
    words = str(text).split()
    if not words:
        return 0
    cleaned = [re.sub(r'[^A-Za-z]', '', w) for w in words]
    return sum(1 for w in cleaned if w.isupper() and len(w) > 1) / len(words)

def polarity_score(text):
    return sia.polarity_scores(str(text))["compound"]

def add_handcrafted_features(df, text_col="cleaned_text"):
    df["word_count"] = df[text_col].apply(lambda x: len(str(x).split()))
    df["avg_word_len"] = df[text_col].apply(avg_word_length)
    df["num_exclamations"] = df[text_col].apply(num_exclamations)
    df["profanity_count"] = df[text_col].apply(profanity_count)
    df["all_caps_ratio"] = df["text"].apply(all_caps_ratio)
    df["polarity"] = df[text_col].apply(polarity_score)
    return df

def extract_handcrafted_features(texts):
    """
    texts: str, list of str, or pd.Series
    Returns: numpy array of handcrafted features
    """
    # If single string, convert to list
    if isinstance(texts, str):
        texts = [texts]

    # If numpy array, convert to list
    if isinstance(texts, np.ndarray):
        texts = texts.tolist()

    # Ensure it's a 1D Series
    texts = pd.Series(texts)

    # Create DataFrame for feature extraction
    df_tmp = pd.DataFrame({"text": texts})
    df_tmp = add_handcrafted_features(df_tmp, text_col="text")

    hand_cols = ["word_count", "avg_word_len", "num_exclamations",
                 "profanity_count", "all_caps_ratio", "polarity"]

    return df_tmp[hand_cols].values.astype(float)

def predict_cyberbullying(texts, weights=DEFAULT_WEIGHTS):
    """
    Predict cyberbullying risk scores for a list of texts.
    Returns list of dicts with 'text', 'predicted_label', 'risk_score'.
    """
    if isinstance(texts, str):
        texts = [texts]

    cleaned_texts = [clean_text(t) for t in texts]

    # handcrafted features
    X_hand = extract_handcrafted_features(cleaned_texts)

    # Get probabilities
    prob_hand = handcrafted.predict_proba(X_hand)[:, 1] * weights["handcrafted"]
    prob_tfidf = tfidf.predict_proba(cleaned_texts)[:, 1] * weights["tfidf"]

    # Weighted average
    total_weight = sum(weights.values())
    avg_proba = (prob_hand + prob_tfidf) / total_weight

    y_pred = (avg_proba > 0.5).astype(int)

    return [{"text": t, "predicted_label": int(p), "risk_score": float(r)} 
            for t, p, r in zip(texts, y_pred, avg_proba)]

def give_suggestion(score):
    if score > 50:
        index = 1
    else:
        index = 0
    
    return SUGGESTION_RECIPIENT.get(index), SUGGESTION_SENDER.get(index)

# Make sure nltk resources are available
nltk.download("vader_lexicon")

# Initialize sentiment analyzer
sid = SentimentIntensityAnalyzer()
sia = SentimentIntensityAnalyzer()

# Handcrafted model pipeline
handcrafted = joblib.load("pipeline/handcrafted_pipeline.pkl")

# tfidf model pipeline
tfidf = joblib.load("pipeline/tfidf_pipeline.pkl")
