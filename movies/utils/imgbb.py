import requests
import base64
import os

def upload_tmdb_image_to_imgbb(tmdb_image_url):
    api_key = os.getenv("IMGBB_API_KEY")

    # Download the image from TMDB
    response = requests.get(tmdb_image_url)
    if response.status_code != 200:
        raise Exception("Failed to download image from TMDB")

    image_data = base64.b64encode(response.content)
    upload = requests.post(
        "https://api.imgbb.com/1/upload",
        data={
            'key': api_key,
            'image': image_data
        }
    )

    result = upload.json()
    if 'data' in result and 'url' in result['data']:
        return result['data']['url']
    else:
        raise Exception("ImgBB upload failed")
