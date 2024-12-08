"""
Database module managing PostgreSQL interactions.

Handles:
- Creating a connection pool.
- Initializing the database schema.
- Inserting and retrieving image records.
"""

import logging
from typing import Optional
import asyncpg
from infrastructure.config import settings


logger = logging.getLogger(__name__)

class Database:
    """Handles PostgreSQL database connections and queries."""
    def __init__(self):
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def connect(self) -> None:
        """Establish a connection pool to PostgreSQL and initialize the schema."""
        try:
            self.pool = await asyncpg.create_pool(
                user=settings.PG_USER,
                password=settings.PG_PASSWORD,
                database=settings.PG_DATABASE,
                host=settings.PG_HOST,
                port=settings.PG_PORT,
                min_size=10,
                max_size=20
            )
            await self.init_db()
            logger.info("Connected to PostgreSQL and database initialized.")
        except Exception as e:
            logger.exception("Failed to connect/init PostgreSQL: %s", e)
            raise

    async def init_db(self) -> None:
        """Create the images table if it does not exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS images (
            id SERIAL PRIMARY KEY,
            url TEXT UNIQUE NOT NULL,
            file_path TEXT NOT NULL,
            downloaded_at TIMESTAMP DEFAULT NOW()
        );
        """
        async with self.pool.acquire() as connection:
            await connection.execute(create_table_query)
            logger.info("Database schema ensured.")

    async def store_image_record(self, url: str, file_path: str) -> Optional[int]:
        """
        Store a record of the downloaded image.
        If the URL already exists, returns the existing ID.

        Args:
            url (str): Image URL.
            file_path (str): Local file path of downloaded image.

        Returns:
            Optional[int]: The image ID if successful, else None.
        """
        insert_query = """
            INSERT INTO images (url, file_path) VALUES ($1, $2)
            ON CONFLICT (url) DO NOTHING
            RETURNING id;
        """
        select_query = "SELECT id FROM images WHERE url = $1;"

        async with self.pool.acquire() as connection:
            # Try to insert a new record
            result = await connection.fetchrow(insert_query, url, file_path)
            if result:
                image_id = result["id"]
                logger.debug("Inserted new image record URL: %s, ID: %d", url, image_id)
                return image_id

            # If insert didn't return an ID, the URL might already exist
            existing = await connection.fetchrow(select_query, url)
            if existing:
                logger.debug("URL already existed, retrieved ID: %d", existing["id"])
                return existing["id"]

            logger.error("Failed to store or retrieve image record for URL: %s", url)
            return None

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool is not None:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed.")

database = Database()
