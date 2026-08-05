# from apscheduler.schedulers.blocking import BlockingScheduler
# from dotenv import load_dotenv
# import os
# import inbound
# import outbound
# from logger import logger

# load_dotenv()

# scheduler = BlockingScheduler()

# def start():

#     logger.info("Rotina de Recebimento: OK")
#     scheduler.add_job(
#         func=inbound.run,
#         trigger="interval",
#         hours=int(os.getenv("TIME_UPDATE_JOB_RECEB")),
#         args=[os.getenv("SPREDSHEET_REC")],
#         id="recebimento",
#         replace_existing=True
#     )

#     logger.info("Rotina de Atualização: OK")
#     scheduler.add_job(
#         func=outbound.run,
#         trigger="interval",
#         minutes=int(os.getenv("TIME_UPDATE_JOB_BASE")),
#         id="devolucao",
#         replace_existing=True
#     )

#     logger.info("Scheduler iniciado...")
#     scheduler.start()

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.base import JobLookupError
from dotenv import load_dotenv
import os

import inbound
import outbound

from logger import logger

load_dotenv()

scheduler = BlockingScheduler()


def job_recebimento():
    logger.info("########## INÍCIO RECEBIMENTO ##########")

    try:
        # Pausa a rotina de devolução enquanto o recebimento estiver executando
        try:
            scheduler.pause_job("devolucao")
            logger.info("Job 'devolucao' pausado.")
        except JobLookupError:
            logger.warning("Job 'devolucao' não encontrado para pausa.")

        inbound.run(os.getenv("SPREDSHEET_REC"))

    except Exception:
        logger.exception("Erro durante a rotina de recebimento.")

    finally:
        # Reativa a rotina de devolução
        try:
            scheduler.resume_job("devolucao")
            logger.info("Job 'devolucao' reativado.")
        except JobLookupError:
            logger.warning("Job 'devolucao' não encontrado para reativação.")

        logger.info("########## FIM RECEBIMENTO ##########")


def job_devolucao():
    logger.info("########## INÍCIO DEVOLUÇÃO ##########")

    try:
        outbound.run()
    except Exception:
        logger.exception("Erro durante a rotina de devolução.")

    logger.info("########## FIM DEVOLUÇÃO ##########")


def start():

    logger.info("Configurando Scheduler...")

    # Recebimento
    scheduler.add_job(
        func=job_recebimento,
        trigger="interval",
        hours=int(os.getenv("TIME_UPDATE_JOB_RECEB", "6")),
        id="recebimento",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    # Atualização Base BI / Devolução
    scheduler.add_job(
        func=job_devolucao,
        trigger="interval",
        minutes=int(os.getenv("TIME_UPDATE_JOB_BASE", "10")),
        id="devolucao",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    logger.info("Scheduler iniciado.")
    scheduler.start()