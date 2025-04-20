import aiohttp
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from typing import List
from .models import Post

async def fetch_posts():
    """Получает посты из API JSONPlaceholder.

    Returns:
        Список постов в формате JSON.

    Raises:
        Exception: Если запрос к API не удался.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Ошибка API: статус {response.status}")

async def fetch_joke():
    """Получает случайную шутку из API Chuck Norris.

    Returns:
        Данные шутки в формате JSON.

    Raises:
        Exception: Если запрос к API не удался.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.chucknorris.io/jokes/random") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Ошибка API: статус {response.status}")

def save_to_sheets(posts: List[Post]):
    """Сохраняет посты в Google Sheets.

    Args:
        posts: Список объектов Post для сохранения.

    Raises:
        Exception: Если операция с Google Sheets не удалась.
    """
    logging.info("Попытка сохранить в Google Sheets")
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("BotData").sheet1
        if not sheet.row_values(1):
            sheet.append_row(["ID", "Title", "Body", "User ID"])
        existing_ids = set(str(cell) for cell in sheet.col_values(1)[1:] if str(cell).isdigit())
        new_rows = [
            [post.id, post.title, post.body, post.user_id]
            for post in posts
            if str(post.id) not in existing_ids
        ]
        if new_rows:
            sheet.append_rows(new_rows)
            logging.info(f"Сохранено {len(new_rows)} постов в Google Sheets")
    except Exception as e:
        logging.error(f"Ошибка Google Sheets: {str(e)}")
        raise Exception(f"Ошибка Google Sheets: {str(e)}")
