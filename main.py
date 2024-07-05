import requests
from mysql.connector import connect, Error
from config import host, user, password, db_name


def get_vacancies(keyword, area_id, num, exp, shd, emp):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": keyword,
        "area": area_id,
        "per_page": num,
        "experience": exp,
        "schedule": shd,
        "employment": emp,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        vacancies = data.get("items", [])
        return (vacancies, data['found'])
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None


def save_vacancies_to_db(vacancies):
    try:
        with connect(
                host=host,
                user=user,
                password=password,
                database=db_name,
                port=3306,
        ) as connection:
            with connection.cursor() as cursor:
                for vacancy in vacancies:
                    cursor.execute(
                        "INSERT INTO vacansies_hh (vacancy_id, vacancy_title, vacancy_url, company_name) VALUES (%s, %s, %s, %s)",
                        (vacancy['id'], vacancy['name'], vacancy['alternate_url'], vacancy['employer']['name']))

                select_vacansies_query = "SELECT * FROM vacansies_hh"
                with connection.cursor() as cursor:
                    cursor.execute(select_vacansies_query)
                    result = cursor.fetchall()
                    for row in result:
                        print(row)

                connection.commit()
            cursor.close()
            connection.close()
    except Error as e:
        print(f"Ошибка подключения к серверу:\n{e}")
