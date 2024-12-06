import logging
from typing import Optional
import asyncpg
from config import settings

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL database handler with connection pooling."""

    def __init__(self):
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def connect(self):
        """Establish a connection pool to the PostgreSQL database."""
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
            logger.info("Connected to PostgreSQL.")
        except Exception as e:
            logger.exception("Failed to connect to PostgreSQL: %s", e)
            raise

    async def init_db(self):
        """Initialize the database by creating the images table if it does not exist."""
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
            logger.info("Database initialized and ready.")

    async def store_image_record(self, url: str, file_path: str) -> Optional[int]:
        """Store a record of the downloaded image in PostgreSQL and return the image ID."""
        insert_query = """
            INSERT INTO images (url, file_path) VALUES ($1, $2)
            ON CONFLICT (url) DO NOTHING
            RETURNING id;
        """
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetchrow(insert_query, url, file_path)
                if result:
                    image_id = result['id']
                    logger.debug("Stored image record for URL: %s with ID: %s", url, image_id)
                    return image_id
                else:
                    # If the URL already exists, fetch its ID
                    select_query = "SELECT id FROM images WHERE url = $1;"
                    existing = await connection.fetchrow(select_query, url)
                    if existing:
                        image_id = existing['id']
                        logger.debug("URL already exists. Retrieved image ID: %s", image_id)
                        return image_id
                    else:
                        logger.error("Failed to retrieve image ID for URL: %s", url)
                        return None
        except Exception as e:
            logger.exception("Error storing image record for URL %s: %s", url, e)
            raise

    async def close(self):
        """Close the connection pool."""
        await self.pool.close()
        logger.info("PostgreSQL connection pool closed.")


database = Database()
