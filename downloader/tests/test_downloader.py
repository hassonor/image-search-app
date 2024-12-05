import os
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch

from downloader.downloader import (
    safe_move_file,
    download_image,
    download_with_retries,
    process_batch,
    chunked_iterable,
    TEMP_DIR,
    OUTPUT_DIR,
)

URL = "http://example.com/image1.jpg"
FILE_NAME = "image1.jpg"


@pytest.fixture(scope="module")
def setup_dirs():
    """
    Fixture to set up and clean up test directories.
    """
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    # Cleanup after tests
    for dir_path in [TEMP_DIR, OUTPUT_DIR]:
        if os.path.exists(dir_path):
            for file in os.listdir(dir_path):
                os.remove(os.path.join(dir_path, file))
            os.rmdir(dir_path)


@pytest.mark.asyncio
async def test_safe_move_file_success(setup_dirs):
    temp_file = os.path.join(TEMP_DIR, FILE_NAME)
    final_file = os.path.join(OUTPUT_DIR, FILE_NAME)

    with open(temp_file, "w") as f:
        f.write("test content")

    await safe_move_file(temp_file, final_file)

    assert os.path.exists(final_file), "File should be moved to the final directory"
    assert not os.path.exists(temp_file), "Temp file should no longer exist"


@pytest.mark.asyncio
async def test_download_image_success(setup_dirs):
    temp_file = os.path.join(TEMP_DIR, FILE_NAME)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.content.iter_chunked = AsyncMock(return_value=[b"chunk1", b"chunk2"])

    with patch("downloader.downloader.aiohttp.ClientSession.get", return_value=mock_response):
        async with aiohttp.ClientSession() as client:
            await download_image(client, URL)

    assert os.path.exists(os.path.join(OUTPUT_DIR, FILE_NAME)), "Downloaded file should exist"


@pytest.mark.asyncio
async def test_download_with_retries_success(setup_dirs):
    with patch("downloader.downloader.download_image", new_callable=AsyncMock) as mock_download:
        mock_download.return_value = None

        async with aiohttp.ClientSession() as client:
            await download_with_retries(client, URL)

        mock_download.assert_called_once_with(client, URL)


@pytest.mark.asyncio
async def test_process_batch(setup_dirs):
    urls = [f"{URL}?id={i}" for i in range(3)]
    with patch("downloader.downloader.download_with_retries", new_callable=AsyncMock) as mock_retries:
        async with aiohttp.ClientSession() as client:
            await process_batch(client, urls)

        assert mock_retries.call_count == len(urls), "Should process all URLs in the batch"


def test_chunked_iterable():
    data = list(range(10))
    chunks = list(chunked_iterable(data, 3))
    assert len(chunks) == 4, "Should create 4 chunks"
    assert chunks[0] == [0, 1, 2], "First chunk should contain first 3 elements"
