import os

import requests
from loguru import logger


def download_video(video_url, folder_path, param) -> None:
    """Скачивание видео"""
    response = requests.get(video_url)
    response.raise_for_status()
    with open(folder_path + param, 'wb') as file:
        file.write(response.content)
    logger.info(f"Video {param} successfully downloaded.")


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