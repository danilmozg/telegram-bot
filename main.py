import asyncio
import os
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from forbot.handlers import start, get_posts, list_posts, joke
from forbot.database import init_db, DATABASE_URL
from dotenv import load_dotenv

load_dotenv()
print(f"Loaded .env: BOT_TOKEN={os.getenv('BOT_TOKEN')[:10]}..., DATABASE_URL={os.getenv('DATABASE_URL')}")

async def wait_for_ngrok(max_attempts=10, delay=10):
    print("Checking if ngrok is ready...")
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get("http://nginx:4040/api/tunnels", timeout=5)
            response.raise_for_status()
            print("Ngrok is ready!")
            return True
        except Exception as e:
            print(f"Ngrok not ready, attempt {attempt}/{max_attempts}: {e}")
            await asyncio.sleep(delay)
    raise Exception("Ngrok not ready after maximum attempts")

async def get_ngrok_url(max_attempts=30, delay=20):
    print("Шаг 4: Получение URL туннеля ngrok...")
    for attempt in range(1, max_attempts + 1):
        try:
            with open("/ngrok_data/ngrok_url.txt", "r") as f:
                url = f.read().strip()
                if not url:
                    print(f"Шаг 4: Файл ngrok_url.txt пуст, попытка {attempt}/{max_attempts}")
                    continue
                print(f"Шаг 4: Найден URL: {url}")
                return url
        except FileNotFoundError:
            print(f"Шаг 4: Файл ngrok_url.txt не найден, попытка {attempt}/{max_attempts}")
        except Exception as e:
            print(f"Шаг 4: Ошибка получения URL: {e}, попытка {attempt}/{max_attempts}")
        await asyncio.sleep(delay)
    raise Exception("Не удалось получить URL туннеля ngrok после максимума попыток")

async def main():
    print("Шаг 2: Начало main()")
    print(f"POSTGRES_PASSWORD from .env: {os.getenv('POSTGRES_PASSWORD')}")
    print(f"DATABASE_URL from database.py: {DATABASE_URL}")
    print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")
    print("Шаг 3: Создание таблиц в базе...")
    try:
        await init_db()
        print("Шаг 3 завершен: Таблицы созданы")
    except Exception as e:
        print(f"Ошибка в init_db: {e}")
        raise
    print("Шаг 4: Ожидание готовности ngrok...")
    await wait_for_ngrok()
    print("Шаг 4: Получение URL туннеля ngrok...")
    ngrok_url = await get_ngrok_url()
    print(f"Шаг 4: Найден URL: {ngrok_url}")
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("get_posts", get_posts))
    application.add_handler(CommandHandler("list_posts", list_posts))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_posts))
    print("Шаг 8: Запуск webhook...")
    await application.initialize()
    await application.start()
    await application.updater.start_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path="/webhook",
        webhook_url=f"{ngrok_url}/webhook"
    )
    print(f"Шаг 8 завершен: Вебхук запущен с URL: {ngrok_url}/webhook")
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("Шаг 0: Запуск программы...")
    print("Шаг 1: Загрузка переменных окружения...")
    print("Шаг 1 завершен: Переменные окружения загружены")
    asyncio.run(main())
