import json
import os
import requests
from loguru import logger

logger.add("log/log.log")


def download_media(url):
    """Скачивание видео из инстаграма по ссылке"""
    response = requests.get(url)
    response.raise_for_status()

    filename = url.split("/")[-1].split("?")[0]
    download_path = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)

    with open(download_path, "wb") as file:
        file.write(response.content)
    return os.path.join(os.getcwd(), download_path)


def here_we_download(all_links):
    """Cкачивание видео из инстаграма по ссылкам"""
    for media_link in all_links:
        download_media(media_link)


def download_from_instagram(link):
    """Cкачивание видео из инстаграма по ссылке"""
    method = "cobalt"
    print(link)

    if method == "cobalt":
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
        }
        body = {"url": link, "vCodec": "h264", "vQuality": "max"}
        api = "https://co.wuk.sh/api/json"

        logger.info(api)
        response = requests.post(api, headers=headers, data=json.dumps(body))
        mydict = response.json()

        if response.status_code == 200:
            if mydict["status"] == "redirect":
                download_list = [mydict["url"]]
                logger.info(download_list)
            elif mydict["status"] == "picker":
                download_list = [obj["url"] for obj in mydict["picker"]]
            here_we_download(download_list)
        else:
            print("\nAPI responded failure: " + str(response.status_code))
            return False, None, []
