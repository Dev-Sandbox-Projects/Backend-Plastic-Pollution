import json
from fastapi import APIRouter
from app.database import r

router = APIRouter(prefix="/stats", tags=["Plastic Statistics"])


@router.get("/plastic")
async def get_plastic():
    data = r.get("plastic_data")
    if data:
        return json.loads(data)
    return {"error": "данные еще не загружены"}
