import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # noqa: E402

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from di.container import DIContainer
from adapters.primary import create_api_router
from middleware import LoggingMiddleware


# Global DI container instance
di_container: DIContainer = DIContainer()


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("🚀 Application started - DI container initialized")

    yield

    await di_container.cleanup()
    print("🧹 Application shutdown - resources cleaned up")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Chatbot API",
        description="FastAPI Chatbot with Hexagonal Architecture",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LoggingMiddleware)

    app.include_router(create_api_router(di_container))

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
