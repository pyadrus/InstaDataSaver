import json

import requests
from loguru import logger

from services.working_with_files import download_media

logger.add("log/log.log")


def here_we_download(all_links, folder, filename):
    """
    Cкачивание видео из инстаграма по ссылкам
    :argument all_links: ссылки на видео
    :argument folder: путь до папки
    :argument filename: имя файла
    """
    for media_link in all_links:
        download_media(media_link, folder, filename)


def download_from_instagram(link, folder, filename):
    """
    Cкачивание видео из инстаграма по ссылке
    :argument link: ссылка на видео
    :argument folder: путь до папки
    :argument filename: имя файла
    """
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
            here_we_download(download_list, folder, filename)
        else:
            print("\nAPI responded failure: " + str(response.status_code))
            return False, None, []
