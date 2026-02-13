"""Research API routes."""

import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from backend.orchestrator.engine import orchestrator
from backend.orchestrator.state_manager import session_store

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    """Research request body."""

    query: str
    depth: int = 2
    language: str = "en"


class ResearchResponse(BaseModel):
    """Research creation response."""

    session_id: str
    status: str = "queued"


@router.post("", response_model=ResearchResponse)
async def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Create a new research session and start orchestration in background."""
    session_id = str(uuid.uuid4())
    background_tasks.add_task(
        orchestrator.run_research,
        query=request.query,
        session_id=session_id,
        depth=request.depth,
        language=request.language,
    )
    return ResearchResponse(session_id=session_id, status="queued")


@router.get("/{session_id}")
async def get_research(session_id: str):
    """Get research session state (polling alternative to WebSocket)."""
    session = session_store.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.get("")
async def list_research(limit: int = 20, offset: int = 0):
    """List all research sessions (paginated)."""
    sessions = session_store.list_all(limit=limit, offset=offset)
    return {
        "sessions": [s.to_dict() for s in sessions],
        "total": len(sessions),
    }


@router.delete("/{session_id}")
async def delete_research(session_id: str):
    """Delete a research session."""
    from backend.rag.vector_store import vector_store

    session_store.delete(session_id)
    await vector_store.delete_collection(session_id)
    return {"status": "deleted"}
