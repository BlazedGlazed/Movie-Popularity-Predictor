from googleapiclient.discovery import build
from config import YOUTUBE_API_KEY


def collect_yt_stats(video_id):
    try:
        # Build the YouTube API service object
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

        # API request to get video details
        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        response = request.execute()

        # Extract the like count
        if 'items' in response and len(response['items']) > 0:
            item = response['items'][0]
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            data = {
                "video_id" : video_id,
                "title": snippet.get('title', video_id),
                "like_count": int(stats.get('likeCount', 0)),
                "viewcount": int(stats.get('viewCount', 0))
            }
            return data
        else:
            print(f"Video with ID '{video_id}' not found or no items in response.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

def collect_yt_comments(video_id, max_comments=100):
    try:
        # Build the YouTube API service object
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        comments = []

        # API request to get video details
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )

        # Extract the comments
        while request and len(comments) < max_comments:
            response = request.execute()
            for item in response["items"]:
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment)
                if len(comments) >= max_comments:
                    break

            request = youtube.commentThreads().list_next(request, response)

        return comments

    except Exception as e:
        print(f"Error fetching comments for {video_id}: {e}")
        return []


if __name__ == "__main__":
    video_id='DZIASl9q90s'
    stats = collect_yt_comments(video_id)

    if collect_yt_comments is not None:
        print(f"The video has{stats}")
    else:
        print(f"Could not retrieve likes for video ID: {video_id}")

# Just for convinience- (activate venv)- E:\Python\Environments\myenv\Scripts\activate, (run the code)- python "E:/Python/My Projects/movie-popularity-predictor/src/collect_data.py"