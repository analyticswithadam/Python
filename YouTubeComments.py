import os
from datetime import datetime
import re
import json
import pycodestyle
import googleapiclient.discovery # install pip install google-api-python-client
import googleapiclient.errors

# Initialize the YouTube API
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "*************"

youtube = googleapiclient.discovery.build(
    api_service_name, 
    api_version, 
    developerKey=DEVELOPER_KEY
    )


def youtube_comments(video_id, results):
    #  Creating the request for the video title
    video_request = youtube.videos().list(
        part="snippet",
        id=video_id,
    )

    # Executing the request and debugging the code
    video_response = video_request.execute()
    if 'items' not in video_response or not video_response['items']: #debugging code
        raise ValueError("Invalid video ID or no response from YouTube API")

    video_title = video_response['items'][0]['snippet']['title']
    channel_name = video_response['items'][0]['snippet']['channelTitle']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Initialize the comments list
    comments = []
    
    #Creating the request for the comments
    comments_request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults = 100
    )

    #Fetch comments, handling pagination if necessary
    while comments_request and len(comments) < results:
        comments_response = comments_request.execute()    
        #Iterating through each comment in the response
        for item in comments_response['items']:
            #Access the snippet section for each top-level comment
            comment = item['snippet']['topLevelComment']['snippet']        
            #Append items to a dataframe
            comments.append({
                "video_title": video_title,
                "channel_uploader": channel_name,
                "author": comment.get('authorDisplayName', 'Unknown'),
                "publish_date": comment.get('publishedAt', ''),
                "updated_date": comment.get('updatedAt', ''),
                "like_count": comment.get('likeCount', 0),
                "text_display": comment.get('textDisplay', ''),
                "url": video_url
            })
            if len(comments) >= results:
                break
        comments_request = youtube.commentThreads().list_next(
            comments_request, comments_response
            )

    #create the dataframe
    df = pd.DataFrame(comments)
    return df, video_title


def save_file(df, video_title):
    #get today's date
    today = datetime.today().strftime('%Y-%m-%d')

    #remove special characters and limit title length
    clean_title = re.sub(r'[^A-Za-z0-9 ]+', '',video_title)
    clean_title = clean_title[:20].strip() #Limit to 20 characters
    clean_title = clean_title.replace(' ', '_') #replace spaces with _

    #Create the full path and filename with today's date and part of video title
    save_path = '*********'
    filename = os.path.join(save_path, f'youtube_{clean_title}_{today}.csv')
    #Save the dataframe to CSV
    print(f"Youtube Video Comments saved to {filename}")
    return  df.to_csv(filename, index=False)


def run_youtube(video_id, results):
    df, video_title = youtube_comments(video_id, results)
    save_file(df, video_title)
