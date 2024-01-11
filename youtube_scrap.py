import os, requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pandas as pd
from pytube import YouTube as YT


def get_authenticated_service(api_name, api_version, scopes, client_secrets_file,api_key):
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build(
        api_name, api_version, credentials=credentials, developerKey=api_key
    )
def getIds(youtube,channel_id):
    uploads_playlist_id = get_uploads_playlist_id(youtube, channel_id)

    next_page_token = None
    first = True
    videos = []

    while first or next_page_token:
        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()
        first = False
        videos.append(pd.Series([item['contentDetails']['videoId'] for item in response['items']]))
        next_page_token = response.get('nextPageToken')
    return pd.concat(videos)

def get_channel_videos(youtube, **kwargs):
    results = youtube.channels().list(**kwargs).execute()
    channel_id = results["items"][0]["id"]
    print(f"Channel ID: {channel_id}")

    video_ids = getIds(youtube=youtube,channel_id=channel_id).reset_index(drop=True)
    print(video_ids)

    video_statistics = pd.concat(video_ids.apply(get_video_details,youtube=youtube).tolist())

    return video_statistics

def get_video_details(id, youtube):
    video_details = []

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=id,
    )
    response = request.execute()
    print(response['items'])
    item = response['items'][0]

    title = item["snippet"]["title"]
    date = item['snippet']['publishedAt']
    views = int(item["statistics"]["viewCount"])
    video_url = f"https://www.youtube.com/watch?v={item['id']}"

    return pd.DataFrame({'title':[title],'date':[date],'url':[video_url],'views':[views]})

def get_uploads_playlist_id(youtube, channel_id):
    response = youtube.channels().list(part='contentDetails', id=channel_id).execute()
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    return uploads_playlist_id

def main():
    api_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyBjNR15l8xH3qwhl5pSxn4hT5YrKB5IWrM"
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    client_secrets_file = "client_secret.json"  # Replace with your client secrets file

    youtube = get_authenticated_service(
        api_name, api_version, scopes, client_secrets_file, api_key
    )

    #channel_id = "UCStskNMVWL1j5BHklBJV5Dw"#input("Enter the username of the YouTube channel: ")
    channel_info = youtube.channels().list(
        part="id",
        mine=True
    ).execute()
    if not channel_info["items"]:
        print("Channel not found.")
        return



    videos = get_channel_videos(
        youtube, part="snippet", mine=True
    )

    videos.to_csv('youtube_inventory.csv',index=False)

    videos.apply(download_video,axis=1)

    #for video in youtube_shorts:
    #    print(f"Working on {video['title']}")
    #    file = open(f"youtube_shorts/{video['title']}_{video['views']}.webm","wb")
    #    res = requests.get(video['url'])
    #    print(res)
    #    file.write(res.content)
    #    file.close()
    #    print("="*60)

def download_video(row):
    if row['views'] >= 1000:
        print(f"Working on {row['title']}")
        try:
            # Create a YouTube object
            yt = YT(row['url'])

            # Get the highest resolution stream
            video_stream = yt.streams.get_highest_resolution()

            # Set the output path for the downloaded video
            video_stream.download(f"youtube_shorts/")

        except Exception as e:
            print(f"An error occurred: {e}")
        print("="*60)

if __name__ == "__main__":
    os.chdir(os.getcwd())
    if "youtube_shorts" not in os.listdir(os.getcwd()):
        os.mkdir("youtube_shorts")

    main()
