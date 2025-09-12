from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def list_assets():
    return {"message": "Assets endpoint"}
