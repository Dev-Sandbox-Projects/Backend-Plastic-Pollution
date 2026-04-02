import json
from fastapi import APIRouter, status, HTTPException
from app.database import r

router = APIRouter(tags=["Plastic Statistics"])


@router.get("/", status_code=status.HTTP_200_OK)
async def successful_response():
	return {"message": "Server running successful"}


@router.get("/stats/plastic", status_code=status.HTTP_200_OK)
async def get_plastic():
	data = r.get("plastic_data")
	if data:
		return json.loads(data)
	return {"debug": "Redis is empty, checking connection...", "ping": r.ping()}


@router.get("/stats/cards")
async def get_cards():
	data = r.get("plastic_cards")
	if data:
		return json.loads(data)
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail={"error": "data has not been loaded yet"})
