from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Lumen CV API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Lumen CV API is running"}


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
