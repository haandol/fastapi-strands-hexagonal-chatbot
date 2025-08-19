import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from fastapi import FastAPI
from di.container import DIContainer

from adapters.primary import create_api_router


# Global DI container instance
di_container: DIContainer = DIContainer()


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("🚀 Application started - DI container initialized")

    yield

    # Shutdown
    di_container.cleanup()
    print("🧹 Application shutdown - resources cleaned up")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chatbot API",
        description="FastAPI Chatbot with Hexagonal Architecture",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(create_api_router(di_container))

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
