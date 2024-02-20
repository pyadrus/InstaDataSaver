import math
import sqlite3
import time
import re
from bs4 import BeautifulSoup
from loguru import logger
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from seleniumwire import webdriver

from config import username, password

logger.add("log/log.log")
logger.info('Запуск скрипта')
proxy_options = {
    'proxy': {'http': 'http://PTUzxQ:0rTvyH@95.164.110.54:9128',
              'https': 'http://PTUzxQ:0rTvyH@95.164.110.54:9128',
              'no_proxy': 'localhost:127.0.0.1'}}
browser = webdriver.Chrome(seleniumwire_options=proxy_options)  # Открываем браузер
logger.info('Запуск браузера')
browser.get("https://www.instagram.com/accounts/login/")
time.sleep(5)
username_input = browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input')
username_input.clear()
logger.info(f'Запуск ввода логина: {username}')
username_input.send_keys(username)  # ввести логин
time.sleep(5)  # таймер до сна
password_input = browser.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
password_input.clear()
logger.info(f'Запуск ввода пароля: {password}')
password_input.send_keys(password)  # ввести пароль
password_input.send_keys(Keys.ENTER)  # после ввода заходим куда захотим
time.sleep(5)  # таймер до сна
logger.info('Переходим на страницу профиля https://www.instagram.com/anji_kn/')
browser.get("https://www.instagram.com/anji_kn/")
time.sleep(5)
# Ищем элемент, содержащий количество публикаций
posts = browser.find_element(By.CLASS_NAME, 'html-span')
logger.info(f'Всего публикаций у пользователя: {posts.text}')
# Подключаемся к базе данных SQLite
conn = sqlite3.connect('instagram_posts.db')
cursor = conn.cursor()
# Создаем таблицу, если её нет
cursor.execute('''CREATE TABLE IF NOT EXISTS posts (post_url)''')
conn.commit()
number_of_posts = math.ceil(int(posts.text) / 10)  # Считаем количество прокручиваний 382/10 = 38,2 (40 пролистываний)
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
        logger.info(post_link['href'])

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

# После завершения парсинга и вставки данных
# Шаг 1: Считать данные из базы данных
cursor.execute('SELECT DISTINCT post_url FROM posts')
all_posts = cursor.fetchall()
# Шаг 2: Удалить дубликаты
# Создать множество для хранения уникальных значений
unique_posts = set()
# Итерироваться по всем данным и добавлять их в множество
for post in all_posts:
    unique_posts.add(post[0])
# Шаг 3: Записать очищенные данные обратно в базу данных
# Очистить таблицу перед вставкой обновленных данных
cursor.execute('DELETE FROM posts')
# Вставить уникальные посты обратно в базу данных
for post_url in unique_posts:
    cursor.execute('INSERT INTO posts (post_url) VALUES (?)', (post_url,))
# Завершить транзакцию
conn.commit()
conn.close()  # Закрываем соединение с базой данных
logger.info('Скролл страницы завершен')
time.sleep(120)
