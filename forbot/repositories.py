from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import DBPost, Post
from .database import AsyncSessionLocal

class PostRepository:
    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        print(f"PostRepository initialized with session_factory: {session_factory}")

    async def save_post(self, post: Post):
        print(f"Saving post: {post}")
        async with self.session_factory() as session:
            existing = await session.get(DBPost, post.id)
            if not existing:
                db_post = DBPost(id=post.id, title=post.title, body=post.body, user_id=post.user_id)
                session.add(db_post)
                await session.commit()

    async def get_posts(self, limit: int = 2):
        print(f"Getting posts with limit: {limit}")
        async with self.session_factory() as session:
            result = await session.execute(select(DBPost).limit(limit))
            return result.scalars().all()
