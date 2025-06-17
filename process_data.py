import re
import string
import emoji
from transformers import pipeline

def clean_comments(comments_list):
    """
    Cleans a list of YouTube comments.

    Args:
        comments_list (list): A list of strings, where each string is a comment.

    Returns:
        list: A list of cleaned comment strings.
    """
    cleaned_comments = []
    for comment in comments_list:
        comment = comment.lower()
        comment = re.sub(r'http\S+|www\S+', '', comment)
        comment = re.sub(r'@\w+', '', comment)
        comment = re.sub(r'#\w+', '', comment)
        comment = re.sub(r'\d+', '', comment)
        comment = comment.translate(str.maketrans('', '', string.punctuation))
        comment = re.sub(r'\s+', ' ', comment).strip()
        comment = re.sub(r'like if you agree', '', comment)
        comment = re.sub(r'who is watching in \d{4}', '', comment)
        comment = re.sub(r'first | second | third | official | trailer | new | full movie', '', comment)
        comment = emoji.replace_emoji(comment, replace='')
        if comment:
            cleaned_comments.append(comment)
    return cleaned_comments


def analyze_sentiment(comments_list):
    """
    Analyzes the sentiment of a list of cleaned comments and returns an
    overall sentiment score on a scale of 1-10.

    Args:
        comments_list (list): A list of cleaned comment strings.

    Returns:
        int or None: An integer sentiment score from 1 (strong negative) to 10 (strong positive),
                     rounded to the nearest integer. Returns None if no comments are provided.
    """
    if not comments_list:
        print("No comments provided for sentiment analysis. Returning None.")
        return None

    sentiments = []
    sentiment_analyzer = pipeline('sentiment-analysis')
    results = sentiment_analyzer(comments_list)

    for res in results:
        label = res['label']
        score = res['score'] # This is the confidence score from 0 to 1

        # Map sentiment scores to a 1-10 scale
        if label == 'POSITIVE':
            # Map positive scores from model (0.5 to 1.0) to a range (e.g., 6-10)
            # A score of 0.5 (least confident positive) maps to 6
            # A score of 1.0 (most confident positive) maps to 10
            # Linear interpolation: new_value = (old_value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
            sentiment_value = ((score - 0.5) * (10 - 6) / (1.0 - 0.5)) + 6
            # Ensure it's not below 5 (if for some reason score was just below 0.5)
            sentiment_value = max(6.0, sentiment_value)
        elif label == 'NEGATIVE':
            # Map negative scores from model (0.5 to 1.0) to a range (e.g., 1-5)
            # A score of 0.5 (least confident negative) maps to 5
            # A score of 1.0 (most confident negative) maps to 1
            # Inverse linear interpolation: Higher score (more negative) -> Lower final score
            sentiment_value = 5 - ((score - 0.5) * (5 - 1) / (1.0 - 0.5))
            # Ensure it's not above 5 (if for some reason score was just below 0.5)
            sentiment_value = min(5.0, sentiment_value)
            # Ensure it's not below 1
            sentiment_value = max(1.0, sentiment_value)
        else:
            # If a model returns 'NEUTRAL' or if score is very low for both, treat as 5 (neutral)
            sentiment_value = 5.0

        sentiments.append(sentiment_value)

    if sentiments:
        overall_score = sum(sentiments) / len(sentiments)
        rounded_score = round(overall_score)
        return rounded_score

    else:
        return None


if __name__ == "__main__":
    # Example for testing this specific file
    sample_raw_comments = [
        "Such a shit movie!",
        "It was okay, not great, not terrible. A bit boring.",
        "Worst film ever! A complete waste of time and money. 😡",
        "Wow! such a great movie! ✨",
        "You call this shit a movie?.",
        "Terrible acting and plot. So disappointing.",
        "What the hell did i watch?! 😍",
        "Total garbage, don't waste your time.👎",
        "I think the antagonist is a hero of this movie.",
        "Hate the visuals, but the story was weak.",
        "Definitely worth watching!"
    ]
    print("Sample raw comments:", sample_raw_comments)

    cleaned_sample_comments = clean_comments(sample_raw_comments)
    print("\nSample cleaned comments:", cleaned_sample_comments)

    overall_sentiment_score = analyze_sentiment(cleaned_sample_comments)
    print(f"\nOverall Comment Sentiment Score (1-10): {overall_sentiment_score}")

    # Test with empty comments
    print("\nTesting with empty comments list:")
    empty_comments_score = analyze_sentiment([])
    print(f"Overall Sentiment Score (empty list): {empty_comments_score}")