from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pydantic import ValidationError
from webapp.logger import logger
from pymongo import AsyncMongoClient
from ..schemas.blog import BlogPost, BlogPostInDB
# from ..schemas.forms import UpdateBlogPost


class Post:

    def __init__(self, db: AsyncMongoClient):
        self.db = db["posts"]

    async def get_all_posts(self) -> List[BlogPostInDB]:
        blogs = []
        try:
            async for blog_data in self.db.find():
                blog = BlogPostInDB(**blog_data)
                blogs.append(blog)
            return blogs
        except Exception as e:
            print(f"Error fetching blogs: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch all posts")

    async def get_post_by_title(self, title: str) -> Optional[BlogPost]:
        post = await self.db.find_one({"title": title})
        return BlogPost(**post) if post else None

    async def get_post_by_id(self, post_id: str) -> Optional[BlogPostInDB]:
        try:
            # Validate the post_id
            object_id = ObjectId(post_id)
        except InvalidId:
            # raise ValueError(f"Invalid post_id: {post_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invalid post_id: {post_id}")

        post = await self.db.find_one({"_id": object_id})
        # logger.info(post)
        if post:
            # Convert ObjectId to string for compatibility with Pydantic
            post["_id"] = str(post["_id"])

            try:
                # Assuming 'comments' is a list of dictionaries with comment data
                # post['comments'] = [str(comment['_id']) for comment in post['comments']]  # Convert ObjectIds to strings
                post['comments'] = [str(comment) for comment in post['comments']]
                return BlogPostInDB(**post)
            except ValidationError as e:
                raise ValueError(f"Invalid data for BlogPostInDB: {e}")
        if not post:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f"Post not found: {post_id}")
        return None

    # get post by tag and tags
    async def get_posts_by_tags(self, tags: List[str]) -> List[BlogPostInDB]:
        query = {"tags": {"$in": tags}}
        posts_cursor = self.db.find(query)
        posts = []
        async for post in posts_cursor:
            posts.append(BlogPostInDB(**post))
        return posts

    # delete post
    async def delete_post(self, post_id: str) -> bool:
        result = await self.db.delete_one({"_id": ObjectId(post_id)})
        return result.deleted_count == 1


def get_post_model() -> Post:
    from webapp.database.db_engine import db

    """Dependency to inject a `Post` instance."""
    return Post(db)
