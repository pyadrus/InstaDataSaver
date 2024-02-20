import time

from loguru import logger
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from config import username, password


def authorization_instagram(browser):
    """
    Авторизация в instagram
    ввод username (логин)
    ввод password (пароль)
    """
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
