from fastapi import APIRouter, status, HTTPException
from app.database import db

router = APIRouter(tags=["Plastic Statistics"])


@router.get("/", status_code=status.HTTP_200_OK)
async def successful_response():
	return {"message": "Server running successful"}


@router.get("/stats/plastic", status_code=status.HTTP_200_OK)
async def get_plastic():
	data = db.get("plastic_data")
	if data:
		return data
	return {"debug": "Memory is empty, waiting for background task to fetch data..."}


@router.get("/stats/cards")
async def get_cards():
	data = db.get("plastic_cards")
	if data:
		return data
	raise HTTPException(
		status_code=status.HTTP_404_NOT_FOUND,
		detail={"error": "data has not been loaded yet"})
