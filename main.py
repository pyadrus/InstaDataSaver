import math
import re
import time

from bs4 import BeautifulSoup
from loguru import logger
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

from config import proxy_options
from instagram_pars.authorization import authorization_instagram
from services.database import database_for_instagram_posts, removing_duplicates_from_the_database


def main():
    logger.add("log/log.log")
    logger.info('Запуск скрипта')
    browser = webdriver.Chrome(seleniumwire_options=proxy_options)  # Открываем браузер
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
    logger.info(f'Колличество пролистываний страницы {number_of_posts}')
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


if __name__ == '__main__':
    main()
