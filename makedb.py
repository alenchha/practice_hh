from mysql.connector import connect, Error
import config

try:
    with connect(
            host=config.host,
            user=config.user,
            password=config.password,
    ) as connection:
        query = f"CREATE DATABASE {config.db_name}"
        with connection.cursor() as cursor:
            cursor.execute(query)
except Error as e:
    print(e)

try:
    with connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.db_name,
    ) as connection:
        create_movies_table_query = """
        CREATE TABLE vacansies_hh(
            id INT AUTO_INCREMENT PRIMARY KEY,
            vacancy_id INT,
            vacancy_title VARCHAR(200),
            vacancy_url VARCHAR(100),
            company_name VARCHAR(100)
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(create_movies_table_query)
        connection.commit()
except Error as e:
    print(f"Ошибка подключения к серверу:\n{e}")
