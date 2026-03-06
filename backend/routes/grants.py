"""
Grant program API routes.
"""
import json
from fastapi import APIRouter, HTTPException
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection
from scraper.scraper import SERBScraper

router = APIRouter()


@router.get("")
async def list_grants():
    """List all scraped grant programs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grant_programs ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    grants = []
    for row in rows:
        grants.append({
            "id": row["id"],
            "program_name": row["program_name"],
            "description": row["description"],
            "eligibility": row["eligibility"],
            "evaluation_criteria": row["evaluation_criteria"],
            "funding_limit": row["funding_limit"],
            "proposal_requirements": row["proposal_requirements"],
            "application_guidelines": row["application_guidelines"],
            "deadlines": row["deadlines"],
            "scraped_at": row["scraped_at"],
        })

    return {"grants": grants, "count": len(grants)}


@router.post("/scrape")
async def scrape_grants():
    """Trigger fresh scraping of SERB grant programs."""
    try:
        scraper = SERBScraper()
        programs = scraper.scrape_and_store()
        return {
            "message": f"Successfully scraped {len(programs)} grant programs",
            "count": len(programs),
            "programs": [p["program_name"] for p in programs],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/{grant_id}")
async def get_grant(grant_id: int):
    """Get a specific grant program by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM grant_programs WHERE id = ?", (grant_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Grant program not found")

    return {
        "id": row["id"],
        "program_name": row["program_name"],
        "description": row["description"],
        "eligibility": row["eligibility"],
        "evaluation_criteria": row["evaluation_criteria"],
        "funding_limit": row["funding_limit"],
        "proposal_requirements": row["proposal_requirements"],
        "application_guidelines": row["application_guidelines"],
        "deadlines": row["deadlines"],
        "scraped_at": row["scraped_at"],
    }
