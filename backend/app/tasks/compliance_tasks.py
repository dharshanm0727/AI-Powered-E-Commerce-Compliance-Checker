from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.compliance_engine import run_full_compliance_workflow
import logging

logger = logging.getLogger(__name__)

@celery_app.task(name="process_compliance_pipeline")
def process_compliance_pipeline(report_id: int):
    db = SessionLocal()
    try:
        run_full_compliance_workflow(report_id, db)
    except Exception as e:
        logger.error(f"Error executing Celery pipeline task for report {report_id}: {e}")
    finally:
        db.close()
