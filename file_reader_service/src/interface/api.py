from fastapi import FastAPI

app = FastAPI(
    title="File Reader Service API",
    description="API for health checks for the File Reader Service.",
    version="1.0.0",
)

@app.get("/health", summary="Health Check", description="Returns service health status.")
async def health_check():
    return {"status": "ok", "service": "file_reader_service"}

async def run_api_server(host: str = "0.0.0.0", port: int = 8006):
    import uvicorn
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
