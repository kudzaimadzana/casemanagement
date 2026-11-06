"""Background worker: runs the nightly ETL pipeline and queue generation on a cron schedule.

Runs as its own process/container, never inside Gunicorn workers, so a schedule fires once.
"""

from __future__ import annotations

import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app import create_app

log = logging.getLogger("mccms.worker")


def run_nightly_pipeline(app) -> None:
    with app.app_context():
        # The ETL pipeline (app/etl/pipeline.py) is built in M2.
        log.info("Nightly pipeline triggered; ETL not implemented yet (M2)")


def main() -> int:
    app = create_app()
    tz = app.config["TZ"]
    scheduler = BlockingScheduler(timezone=tz)

    if app.config["ETL_ENABLED"]:
        trigger = CronTrigger.from_crontab(app.config["ETL_CRON"], timezone=tz)
        scheduler.add_job(
            run_nightly_pipeline,
            trigger,
            args=[app],
            id="nightly_pipeline",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=3600,
        )
        log.info("Scheduled nightly pipeline", extra={"cron": app.config["ETL_CRON"], "tz": tz})
    else:
        log.warning("ETL_ENABLED is false; the worker is idle")

    def shutdown(signum, _frame):
        log.info("Worker stopping", extra={"signal": signum})
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    scheduler.start()
    return 0


if __name__ == "__main__":
    sys.exit(main())
