"""Analytics API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/costs")
async def get_costs(days: int = 30):
    """Get cost analytics over time."""
    # TODO: Fetch from DB
    return {"costs": [], "total": 0}


@router.get("/usage")
async def get_usage(days: int = 30):
    """Get token usage analytics."""
    # TODO: Fetch from DB
    return {"usage": [], "total_tokens": 0}
