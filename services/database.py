import sqlite3


def database_for_instagram_posts():
    """Создание таблицы для базы данных постов instagram"""
    conn = sqlite3.connect('instagram_posts.db')  # Подключаемся к базе данных SQLite
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (post_url)''')  # Создаем таблицу, если её нет
    conn.commit()

    return conn, cursor


if __name__ == '__main__':
    database_for_instagram_posts()
