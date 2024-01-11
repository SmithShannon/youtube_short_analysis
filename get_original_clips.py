import os, requests
import pandas as pd
from pytube import YouTube as YT
from bs4 import BeautifulSoup as bs

def download_clips(row,output_path="."):
    print(row)
    res = requests.get(row['Raw_Url'])
    file = open (f"{output_path}/{row['Title']}_{row['Created On']}.mp4",'wb')
    file.write(res.content)
    file.close()


if __name__ == "__main__":
    # Replace 'YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET', 'CHANNEL_NAME', and 'OUTPUT_PATH' with your actual values
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    channel_name = 'mikodite_yvette'
    output_path = 'twitch_clips'

    if 'twitch_clips' not in os.listdir(os.getcwd()):
        os.mkdir('twitch_clips')

    twitch_inventory = pd.read_csv('twitch_clip_inventory.csv')
    # Download the clip using requests
    youtube_inventory = pd.read_csv('youtube_inventory.csv')

    twitch_youtubep1 = youtube_inventory[youtube_inventory['title'].str.contains('#Twitch')]
    twitch_youtubep1['twitch_title'] = twitch_youtubep1['title'].str.split('|',expand=True)[0].str.strip()
    twitch_youtube = twitch_youtubep1.merge(right=twitch_inventory,
                                            how='inner',
                                            left_on='twitch_title',
                                            right_on='Title',
                                            suffixes=('','_'))

    twitch_youtube[twitch_youtube['views']>=1000].apply(download_clips,output_path=output_path,axis=1)
    #download_clips(client_id, client_secret, channel_name, output_path)
