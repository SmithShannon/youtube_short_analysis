import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
import requests

def get_twitch_clips(client_id, client_secret, channel_name):
    # Get OAuth token
    token_url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }

    response = requests.post(token_url, params=params)
    access_token = response.json().get("access_token")

    # Get channel ID
    channel_url = f"https://api.twitch.tv/helix/users?login={channel_name}"
    headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}

    response = requests.get(channel_url, headers=headers)
    channel_id = response.json().get("data")[0].get("id")

    # Get clips from the channel
    clips_url = f"https://api.twitch.tv/helix/clips"
    params = {"broadcaster_id": channel_id, "first":100}  # Adjust 'first' based on your needs

    response = requests.get(clips_url, params=params, headers=headers)
    clips_data = [pd.Series(response.json().get("data"))]

    cursor = response.json().get("pagination", {}).get("cursor")


    while cursor:
        print(params)
        params["after"] = cursor
        res = requests.get(clips_url,params=params,headers=headers)
        clips_data.append(pd.Series(res.json().get("data")))
        cursor = res.json().get("pagination").get("cursor")
        print(res.json().get('data'))

    clips_inventory = pd.concat(pd.concat(clips_data).apply(lambda f:
                                                  pd.DataFrame({
                                                      "Title":[f['title']],
                                                      "ID":[f['id']],
                                                      'Url':[f['url']],
                                                      'Thumbnail_Url':[f['thumbnail_url']],
                                                      'Created On':[f['created_at']],
                                                      'Game ID':[f['game_id']]
                                                  })).tolist())



    # Print titles of all clips
    print(clips_inventory['Title'])
    clips_inventory['Raw_Url'] = clips_inventory['Thumbnail_Url'].apply(lambda f:
                                                                        f[:f.find('-preview')]+'.mp4')
    clips_inventory.to_csv('twitch_clip_inventory.csv',index=False)

if __name__ == "__main__":
    # Replace 'YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', and 'CHANNEL_NAME' with your actual values
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    channel_name = 'mikodite_yvette'

    get_twitch_clips(client_id, client_secret, channel_name)