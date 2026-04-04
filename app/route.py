from fastapi import APIRouter, status
from app import parser

router = APIRouter(tags=["Plastic Statistics"])


@router.api_route("/", methods=["GET", "HEAD"], status_code=status.HTTP_200_OK)
async def successful_response():
	return {"message": "Server running successful"}


@router.get("/stats/plastic", status_code=status.HTTP_200_OK)
async def get_plastic():
	return parser.GLOBAL_PLASTIC_GRAPH


@router.get("/stats/cards")
async def get_cards():
	return parser.GLOBAL_PLASTIC_CARDS
