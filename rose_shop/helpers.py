import requests
import requests_cache



requests_cache.install_cache(cache_name = 'image_cache', backend='sqlite', expire_after=900)




def get_image(search):

    url = "https://google-search72.p.rapidapi.com/imagesearch"

    querystring = {"q": search,"gl":"us","lr":"lang_en","num":"1","start":"0"}

    headers = {
        "X-RapidAPI-Key": "9aac146b28msha98b54ca2f39ee0p16455djsn9a0f2e345df6",
        "X-RapidAPI-Host": "google-search72.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    img_url = data['items'][0]['originalImageUrl'] #traversing data dictionary to get the image url we want
    return img_url