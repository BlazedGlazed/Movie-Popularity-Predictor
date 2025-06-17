from collect_data import collect_yt_stats, collect_yt_comments
from process_data import clean_comments, analyze_sentiment

video_id='EXeTwQWrcwY'
stats = collect_yt_stats(video_id)
if collect_yt_stats is not None:
    print(f"The video has{stats}")
else:
    print(f"\nCould not retrieve likes for video ID: {video_id}")

# video_id='JgDNFQ2RaLQ'
# comments = collect_yt_comments(video_id)
# if collect_yt_comments is not None:
#     print(f"The video has{comments}")
# else:
#     print(f"Could not retrieve likes for video ID: {video_id}")


# cleaned_sample_comments = clean_comments(comments)
# print("\nSample cleaned comments:", cleaned_sample_comments)

# overall_sentiment_score = analyze_sentiment(cleaned_sample_comments)
# print(f"\nOverall Comment Sentiment Score (1-10): {overall_sentiment_score}")