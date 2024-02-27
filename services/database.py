import sqlite3


def database_for_instagram_posts():
    """Создание таблицы для базы данных постов instagram"""
    conn = sqlite3.connect('instagram_posts.db')  # Подключаемся к базе данных SQLite
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS posts (post_url)''')  # Создаем таблицу, если её нет
    conn.commit()

    return conn, cursor


def removing_duplicates_from_the_database(cursor, conn) -> None:
    """Удаление дубликатов с базы данных"""
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


if __name__ == '__main__':
    database_for_instagram_posts()
