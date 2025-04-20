from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from .models import Post, Joke, ValidationError
from .services import fetch_posts, fetch_joke, save_to_sheets
from .repositories import PostRepository

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Получить посты", callback_data="get_posts")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

async def joke(update, context):
    logging.info(f"Запрос /joke от {update.effective_user.id}")
    try:
        data = await fetch_joke()
        try:
            joke_model = Joke(**data)
            await update.message.reply_text(f"😂 {joke_model.value}")
        except ValidationError as e:
            logging.error(f"ValidationError: {str(e)}")
            await update.message.reply_text(f"Ошибка валидации: {str(e)}")
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def get_posts(update, context, repo: PostRepository):
    logging.info(f"Запрос /get_posts от {update.effective_user.id}")
    try:
        posts = await fetch_posts()
        validated_posts = []
        for post in posts[:2]:
            try:
                validated_post = Post(**post)
                validated_posts.append(validated_post)
                await repo.save_post(validated_post)
            except ValidationError as e:
                logging.error(f"ValidationError: {str(e)}")
                await update.message.reply_text(f"Ошибка валидации поста: {str(e)}")
                return
        save_to_sheets(validated_posts)
        for post in validated_posts:
            await update.message.reply_text(
                f"Title: {post.title}\nBody: {post.body}\nUser ID: {post.user_id}"
            )
        await update.message.reply_text("Данные сохранены в базу и Google Sheets!")
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def list_posts(update, context, repo: PostRepository):
    logging.info(f"Запрос /list_posts от {update.effective_user.id}")
    try:
        posts = await repo.get_posts()
        if not posts:
            await update.message.reply_text("Нет постов в базе.")
            return
        for post in posts:
            await update.message.reply_text(
                f"ID: {post.id}\nTitle: {post.title}\nBody: {post.body}\nUser ID: {post.user_id}"
            )
    except Exception as e:
        logging.error(f"Ошибка: {str(e)}")
        await update.message.reply_text(f"Ошибка: {str(e)}")

async def button(update, context, repo: PostRepository):
    query = update.callback_query
    await query.answer()
    if query.data == "get_posts":
        try:
            posts = await fetch_posts()
            validated_posts = []
            for post in posts[:2]:
                try:
                    validated_post = Post(**post)
                    validated_posts.append(validated_post)
                    await repo.save_post(validated_post)
                except ValidationError as e:
                    logging.error(f"ValidationError: {str(e)}")
                    await query.message.reply_text(f"Ошибка валидации поста: {str(e)}")
                    return
            save_to_sheets(validated_posts)
            for post in validated_posts:
                await query.message.reply_text(
                    f"Title: {post.title}\nBody: {post.body}\nUser ID: {post.user_id}"
                )
            await query.message.reply_text("Данные сохранены в базу и Google Sheets!")
        except Exception as e:
            logging.error(f"Ошибка: {str(e)}")
            await query.message.reply_text(f"Ошибка: {str(e)}")
