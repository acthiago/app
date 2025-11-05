"""
Scheduler para tarefas agendadas (limpeza automática de arquivos)
"""
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.file_storage import cleanup_expired_files, cleanup_orphan_files
from app.core.logging import get_logger
import os

logger = get_logger(__name__)

# Configurações
CLEANUP_ENABLED = os.getenv("FILE_CLEANUP_ENABLED", "true").lower() == "true"
CLEANUP_HOUR = int(os.getenv("FILE_CLEANUP_HOUR", "3"))  # 3h da manhã por padrão
CLEANUP_ORPHANS_ENABLED = os.getenv("FILE_CLEANUP_ORPHANS_ENABLED", "false").lower() == "true"

scheduler = None


async def scheduled_cleanup_expired():
    """Tarefa agendada para limpeza de arquivos expirados"""
    try:
        logger.info("scheduled_cleanup_started", type="expired")
        result = await cleanup_expired_files()
        logger.info(
            "scheduled_cleanup_completed",
            type="expired",
            deleted=result["deleted"],
            freed_mb=result["freed_mb"]
        )
    except Exception as e:
        logger.error("scheduled_cleanup_failed", type="expired", error=str(e))


async def scheduled_cleanup_orphans():
    """Tarefa agendada para limpeza de arquivos órfãos"""
    try:
        logger.info("scheduled_cleanup_started", type="orphans")
        result = await cleanup_orphan_files()
        logger.info(
            "scheduled_cleanup_completed",
            type="orphans",
            deleted=result["deleted"],
            freed_mb=result["freed_mb"]
        )
    except Exception as e:
        logger.error("scheduled_cleanup_failed", type="orphans", error=str(e))


def init_scheduler():
    """
    Inicializa scheduler de tarefas agendadas
    
    - Limpeza de arquivos expirados: diariamente às 3h
    - Limpeza de arquivos órfãos: semanalmente aos domingos às 4h (opcional)
    """
    global scheduler
    
    if not CLEANUP_ENABLED:
        logger.info("file_cleanup_disabled")
        return
    
    scheduler = AsyncIOScheduler()
    
    # Limpeza de arquivos expirados (diariamente)
    scheduler.add_job(
        scheduled_cleanup_expired,
        trigger=CronTrigger(hour=CLEANUP_HOUR, minute=0),
        id="cleanup_expired_files",
        name="Limpeza de arquivos expirados",
        replace_existing=True
    )
    logger.info(
        "scheduled_job_added",
        job="cleanup_expired_files",
        schedule=f"Diariamente às {CLEANUP_HOUR}:00"
    )
    
    # Limpeza de arquivos órfãos (semanalmente - opcional)
    if CLEANUP_ORPHANS_ENABLED:
        scheduler.add_job(
            scheduled_cleanup_orphans,
            trigger=CronTrigger(day_of_week='sun', hour=CLEANUP_HOUR + 1, minute=0),
            id="cleanup_orphan_files",
            name="Limpeza de arquivos órfãos",
            replace_existing=True
        )
        logger.info(
            "scheduled_job_added",
            job="cleanup_orphan_files",
            schedule=f"Domingos às {CLEANUP_HOUR + 1}:00"
        )
    
    scheduler.start()
    logger.info("scheduler_started", jobs=len(scheduler.get_jobs()))


def shutdown_scheduler():
    """Desliga scheduler graciosamente"""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("scheduler_shutdown")
