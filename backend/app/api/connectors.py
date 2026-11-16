from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import SourceConnector, SourceSyncLog
from app.schemas.schemas import ConnectorOut
from app.connectors import get_connector

router = APIRouter(prefix="/connectors", tags=["Source Connectors & Ingestion"])

@router.get("", response_model=List[ConnectorOut])
def get_connectors(db: Session = Depends(get_db)):
    return db.query(SourceConnector).order_by(SourceConnector.name.asc()).all()

@router.post("/{platform}/sync")
async def trigger_connector_sync(platform: str, db: Session = Depends(get_db)):
    connector_model = db.query(SourceConnector).filter_by(platform=platform.lower()).first()
    if not connector_model:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector_model.status = "SYNCING"
    db.commit()

    try:
        connector_instance = get_connector(platform)
        results = await connector_instance.sync()
        count = len(results)

        connector_model.status = "IDLE"
        connector_model.last_synced_at = datetime.now(timezone.utc)
        connector_model.total_items_fetched += count

        log = SourceSyncLog(
            connector_id=connector_model.id,
            status="SUCCESS" if connector_instance.is_configured() else "DEMO_MODE",
            items_ingested=count,
            error_message="Completed via verified connector pipeline." if connector_instance.is_configured() else "Synchronized in permitted demo curation mode."
        )
        db.add(log)
        db.commit()

        return {
            "platform": platform,
            "status": "SUCCESS",
            "items_ingested": count,
            "mode": "live_api" if connector_instance.is_configured() else "demo_curated",
            "message": f"Successfully synchronized {count} architectural references from {platform}."
        }
    except Exception as e:
        connector_model.status = "ERROR"
        log = SourceSyncLog(
            connector_id=connector_model.id,
            status="FAILED",
            items_ingested=0,
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Synchronization failed: {str(e)}")
