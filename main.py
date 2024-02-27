import math
import os
import re
import time

import bs4
import requests
from bs4 import BeautifulSoup
from loguru import logger
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

from system.config import proxy_options
from instagram_pars.authorization import authorization_instagram
from instagram_pars.download_video import download_from_instagram
from services.database import database_for_instagram_posts, removing_duplicates_from_the_database

logger.add("log/log.log")


def initialize_driver() -> webdriver:
    """Инициализация браузера"""
    browser = webdriver.Chrome(seleniumwire_options=proxy_options)  # Открываем браузер

    return browser


def main() -> None:
    """Основная функция"""
    print('[1] - Парсинг постов со страницы\n'
          '[2] - Скачать посты со страницы')

    user_input = input("Выбери действие ")
    if user_input == "1":

        logger.info('Запуск скрипта')
        browser = initialize_driver()
        logger.info('Запуск браузера')
        authorization_instagram(browser)  # Авторизация
        logger.info('Переходим на страницу профиля https://www.instagram.com/anji_kn/')
        browser.get("https://www.instagram.com/anji_kn/")
        time.sleep(5)
        # Ищем элемент, содержащий количество публикаций
        posts = browser.find_element(By.CLASS_NAME, 'html-span')
        logger.info(f'Всего публикаций у пользователя: {posts.text}')
        conn, cursor = database_for_instagram_posts()  # База данных для постов
        number_of_posts = math.ceil(
            int(posts.text) / 10)  # Считаем количество прокручиваний 382/10 = 38,2 (40 пролистываний)
        logger.info(f'Количество пролистываний страницы {number_of_posts}')
        for _ in range(number_of_posts):
            # Скроллим страницу вниз
            browser.execute_script("window.scrollBy(0, 920);")  # 920 - количество пикселей для прокрутки
            # Ждем некоторое время (может потребоваться для загрузки контента)
            time.sleep(3)
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')  # Инициализация BeautifulSoup
            # Находим все элементы с классом x1i10hfl, которые представляют собой ссылки на посты
            post_links = soup.find_all('a', class_='x1i10hfl')
            for post_link in post_links:  # Собираем все ссылки на посты
                # Используем два паттерна для поиска ссылок на посты и reels
                post_pattern = re.compile(r'/p/[\w\-]+/')
                reel_pattern = re.compile(r'/reel/[\w\-]+/')
                # Используем findall для поиска всех соответствующих ссылок
                post_links_found = post_pattern.findall(post_link['href'])
                reel_links_found = reel_pattern.findall(post_link['href'])
                for post_link_found in post_links_found:
                    logger.info(f'Пост: {post_link_found}')
                    post_url = f"https://www.instagram.com{post_link_found}"
                    cursor.execute('INSERT INTO posts (post_url) VALUES (?)', (post_url,))
                for reel_link_found in reel_links_found:
                    logger.info(f'Reel: {reel_link_found}')
                    reel_url = f"https://www.instagram.com{reel_link_found}"
                    cursor.execute('INSERT INTO posts (post_url) VALUES (?)', (reel_url,))
                conn.commit()

        removing_duplicates_from_the_database(cursor, conn)
        logger.info('Скролл страницы завершен')
        time.sleep(120)

    elif user_input == "2":

        logger.info('Запуск скрипта по скачиванию постов')
        post_url = 'https://www.instagram.com/p/CESBO8JltYb/'
        browser = initialize_driver()
        authorization_instagram(browser)  # Авторизация
        browser.get(post_url)  # Перейти на страницу поста
        time.sleep(2)
        posts_data = browser.find_element(By.CLASS_NAME, '_aaqe')
        date_value = posts_data.get_attribute("datetime")  # Получаем значение атрибута datetime
        folder_name = sanitize_folder_name(date_value)  # Преобразовываем в формат для имени папки
        logger.info(f'Дата публикации поста: {date_value}')  # Выводим значение даты
        time.sleep(1)
        folder_path = f'downloaded_content/{folder_name}/'  # Проверяем наличие папки
        os.makedirs(folder_path, exist_ok=True)

        video_src = ('/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/'
                     'div[1]/div/div/div/div/div/div/div/div/div/div/video')
        img_src = ("/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/"
                   "div[1]/div/div/div/div/div/div[1]/div[2]/div/div/div/ul/li[3]/div/div/div/div/div[1]/img")

        time.sleep(5)
        try:
            browser.find_element(By.XPATH, video_src)
            logger.info('Видео')
            download_from_instagram(post_url)
        except NoSuchElementException:  # Если видео нет, то скачиваем картинку

            browser.find_element(By.XPATH, img_src)

            logger.info('Изображение')
            html = browser.page_source
            soup = bs4.BeautifulSoup(html, 'lxml')
            img_url = soup.select('._aagv  img')[0].get('src')
            logger.info(img_url)

            download_image(url=img_url, folder=folder_path, filename=f'{folder_name}.jpg')

            for i in range(1, 4):  # Download next two images
                button_xpath = "//button[@aria-label='Далее']"
                if browser.find_elements(By.XPATH, button_xpath):
                    browser.find_element(By.XPATH, button_xpath).click()
                    time.sleep(2)
                    post = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/div/div/div[1]'
                                                          '/div[1]/div[2]/section/main/div/div[1]/div/div[1]/div/'
                                                          'div/div/div/div/div[1]/div[2]/div/div/div/ul/li[3]/div/'
                                                          'div/div/div/div[1]/img').get_attribute('src')
                    time.sleep(3)
                    download_image(post, folder_path, f'{folder_name}_next{i - 1}.jpg')

        logger.info("Выключение браузера через 200 сек.")
        time.sleep(200)


def sanitize_folder_name(folder_name):
    """Преобразование названия папки"""
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']  # Заменяем недопустимые символы
    for char in invalid_chars:
        folder_name = folder_name.replace(char, '_')
    logger.info(f'Название папки {folder_name}')
    return folder_name


def download_image(url, folder, filename) -> None:
    """Скачивание изображения по ссылке"""
    response = requests.get(url)
    response.raise_for_status()
    with open(os.path.join(folder, filename), 'wb') as file:
        file.write(response.content)
    logger.info(f"Image {filename} successfully downloaded.")


if __name__ == '__main__':
    main()
