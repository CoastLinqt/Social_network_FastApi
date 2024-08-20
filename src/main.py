from contextlib import asynccontextmanager

from fastapi import FastAPI

from models import create_tables  # type: ignore
from routers import router  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    print("Database created")


app = FastAPI(title="Twitter Clone", lifespan=lifespan)

app.include_router(router=router)
