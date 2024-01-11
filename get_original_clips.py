from twitchAPI.twitch import Twitch
import os, requests
import pandas as pd


def download_twitch_clips(client_id, client_secret, channel_name, output_path="."):
    twitch = Twitch(client_id, client_secret)
    twitch.authenticate_app([])

    # Get the channel ID
    channel_info = twitch.get_users(logins=[channel_name])
    channel_id = channel_info[0]['id']

    # Get the clips from the channel
    clips_url = f"https://api.twitch.tv/helix/clips"
    params = {"broadcaster_id": channel_id, "first": 100}  # Adjust 'first' based on your needs

    headers = {"Client-ID": client_id}
    response = requests.get(clips_url, params=params, headers=headers)
    clips_data = response.json().get("data")

    # Download each clip
    for clip in clips_data:
        clip_url = clip.get("url")
        clip_title = clip.get("title")
        clip_id = clip.get("id")

        # Download the clip using requests
        clip_response = requests.get(clip_url)

        # Save the clip to the specified output path
        clip_filename = f"{output_path}/clip_{clip_id}_{clip_title}.mp4"
        with open(clip_filename, 'wb') as clip_file:
            clip_file.write(clip_response.content)

        print(f"Clip '{clip_title}' downloaded and saved as '{clip_filename}'")


if __name__ == "__main__":
    # Replace 'YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', 'CHANNEL_NAME', and 'OUTPUT_PATH' with your actual values
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    channel_name = 'mikodite_yvette'
    output_path = 'twitch_clips/'

    download_twitch_clips(client_id, client_secret, channel_name, output_path)
