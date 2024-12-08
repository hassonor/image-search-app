import pytest
import httpx

@pytest.mark.asyncio
async def test_api_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://localhost:8003/health")
        assert resp.status_code == 200
        assert resp.json() == {"service": "downloader_service", "status": "ok"}
