from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.user.api import router as api_router
from app.routers.admin.api import router as admin_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Travel Suggestion App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root API
@app.get("/")
def root():
    return {"message": "Travel Suggestion API is running"}

# Routers
app.include_router(api_router)
app.include_router(admin_router)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")