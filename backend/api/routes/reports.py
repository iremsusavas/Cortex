"""Reports API routes."""

from fastapi import APIRouter, HTTPException

from backend.orchestrator.state_manager import session_store, ResearchPhase

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
async def list_reports(limit: int = 20, offset: int = 0):
    """List all completed reports."""
    sessions = session_store.list_all(limit=limit * 2, offset=0)
    completed = [
        s.to_dict()
        for s in sessions
        if s.phase == ResearchPhase.COMPLETE and s.report
    ][offset : offset + limit]
    return {"reports": completed, "total": len(completed)}


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Get a single report by session ID."""
    session = session_store.get(report_id)
    if not session or session.phase != ResearchPhase.COMPLETE:
        raise HTTPException(status_code=404, detail="Report not found")
    return session.to_dict()
