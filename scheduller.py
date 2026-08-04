from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
import os
import inbound
import outbound
from logger import logger

load_dotenv()

scheduler = BlockingScheduler()

def start():

    logger.info("Rotina de Recebimento: OK")
    scheduler.add_job(
        func=inbound.run,
        trigger="interval",
        hours=int(os.getenv("TIME_UPDATE_JOB_RECEB")),
        args=[os.getenv("SPREDSHEET_REC")],
        id="recebimento",
        replace_existing=True
    )

    logger.info("Rotina de Atualização: OK")
    scheduler.add_job(
        func=outbound.run,
        trigger="interval",
        minutes=int(os.getenv("TIME_UPDATE_JOB_BASE")),
        id="devolucao",
        replace_existing=True
    )

    logger.info("Scheduler iniciado...")
    scheduler.start()