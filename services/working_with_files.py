import os

import requests
from loguru import logger


def download_media(url, folder, filename):
    """
    Скачивание видео из instagram по ссылке
    :argument url: ссылка на видео
    :argument folder: путь до папки
    :argument filename: имя файла
    """
    response = requests.get(url)
    response.raise_for_status()

    # filename = url.split("/")[-1].split("?")[0]
    download_path = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)

    with open(download_path, "wb") as file:
        file.write(response.content)

    return os.path.join(os.getcwd(), download_path)


def download_image(url, folder, filename) -> None:
    """
    Скачивание изображения по ссылке
    :argument url: ссылка на изображение
    :argument folder: путь до папки
    :argument filename: имя файла
    """
    response = requests.get(url)
    response.raise_for_status()
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)
    logger.info(f"Image {filename} successfully downloaded.")
