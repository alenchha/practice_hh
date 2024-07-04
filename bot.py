import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, utils, Router, F
from aiogram.filters.command import Command
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)
from main import save_vacancies_to_db, get_vacancies

form_router = Router()


class Form(StatesGroup):
    keyword = State()
    area_id = State()
    num = State()
    exp = State()
    shd = State()
    emp = State()


@form_router.message(Command("start"))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.keyword)
    await message.answer(
        "Привет! Я помогу тебе найти подходящие вакансии на сайте hh.ru!"
        "Для начала скажи по какой должности ты хочешь начать поиск?",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.keyword)
async def process_keyword(message: Message, state: FSMContext) -> None:
    await state.update_data(keyword=message.text)
    await state.set_state(Form.area_id)
    await message.answer(
        "Отлично! Теперь скажи в каком городе ты ищешь вакансии?"
        "Напиши цифру, соответсвующую id города или же None, если город не имеет значения!"
        "\nНапример:"
        "\nid Москвы - 1,"
        "\nid Санкт-Петербурга - 2,"
        "\nid нужного города можно узнать здесь:"
        "\nhttps://api.hh.ru/areas",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.area_id)
async def process_area_id(message: Message, state: FSMContext) -> None:
    await state.update_data(area_id=message.text)
    await state.set_state(Form.num)
    await message.answer(
        "Сколько вакансий ты хочешь посмотреть за раз?"
        "\nМаксимум - 50 вакансий.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.num)
async def process_area_num(message: Message, state: FSMContext) -> None:
    await state.update_data(num=message.text)
    await state.set_state(Form.exp)
    await message.answer(
        "Какой у тебя опыт работы?"
        "\nЕсли нет опыта - noExperience"
        "\nЕсли от 1 года до 3 лет - between1And3"
        "\nЕсли от 3 до 6 лет - between3And6"
        "\nЕсли более 6 лет - moreThan6"
        "\nЕсли данный фильтр не нужен - None",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.exp)
async def process_exp(message: Message, state: FSMContext) -> None:
    await state.update_data(exp=message.text)
    await state.set_state(Form.shd)
    await message.answer(
        "Какой график работы?"
        "\nЕсли полный день - fullDay"
        "\nЕсли сменный график - shift"
        "\nЕсли гибкий график - flexible"
        "\nЕсли удалённая работа - remote"
        "\nЕсли вахтовый метод - flyInFlyOut"
        "\nЕсли данный фильтр не нужен - None",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.shd)
async def process_shd(message: Message, state: FSMContext) -> None:
    await state.update_data(shd=message.text)
    await state.set_state(Form.emp)
    await message.answer(
        "Какой тип занятости?"
        "\nЕсли полная занятость - full"
        "\nЕсли частичная занятость - part"
        "\nЕсли проектная работа - project"
        "\nЕсли волонтерство - volunteer"
        "\nЕсли стажировка - probation"
        "\nЕсли данный фильтр не нужен - None",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Form.emp)
async def process_emp(message: Message, state: FSMContext) -> None:
    await state.update_data(emp=message.text)
    await message.answer(
        "Отлично! Сейчас найду подходящие вакансии!",
        reply_markup=ReplyKeyboardRemove(),
    )
    data = await state.get_data()
    for key, value in data.items():
        print(f"{key}: {value}")
    keyword = str(data['keyword'])
    area_id = data['area_id']
    num = data['num']
    if data['exp'] == "None":
        exp = None
    else:
        exp = data['exp']
    if data['shd'] == "None":
        shd = None
    else:
        shd = data['shd']
    if data['emp'] == "None":
        emp = None
    else:
        emp = data['emp']
    vacancies, total_cnt = get_vacancies(keyword, area_id, num, exp, shd, emp)
    await message.answer(f"Всего найдено вакансий: {total_cnt}")

    if vacancies is not None:
        save_vacancies_to_db(vacancies)
        for vacancy in vacancies:
            vacancy_id = vacancy.get("id")
            vacancy_title = vacancy.get("name")
            vacancy_url = vacancy.get("alternate_url")
            company_name = vacancy.get("employer", {}).get("name")
            ac = vacancy.get("employer", {}).get("accredited_it_employer")
            await message.answer(
                f"Вакансия: {vacancy_title}\nКомпания: {company_name}\nСсылка: {vacancy_url}\nЕсть ли IT аккредетация: {'да' if ac else 'нет'}\n",
                reply_markup=ReplyKeyboardRemove(),
            )


async def main():
    bot = Bot(token="7287571204:AAEA6wwm76wQ8Idl5NYYEExlUUGDI42LbWA")
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
