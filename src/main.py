from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from fastapi import FastAPI

from adapters.primary.router import create_api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chatbot API",
        description="FastAPI Chatbot with Hexagonal Architecture",
        version="1.0.0",
    )

    # API routes
    app.include_router(create_api_router())

    return app


app = create_app()

if __name__ == "__main__":
    import os
    import uvicorn

    port = os.getenv("PORT", 8000)

    uvicorn.run(app, host="0.0.0.0", port=port)
