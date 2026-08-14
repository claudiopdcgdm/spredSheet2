from apscheduler.schedulers.background import BackgroundScheduler

from dotenv import load_dotenv

import os

import inbound
import outbound

from logger import logger


load_dotenv()


scheduler = BackgroundScheduler()


def start():

    if scheduler.running:

        logger.warning(
            "Scheduler já está em execução."
        )

        return


    logger.info(
        "Configurando Scheduler..."
    )


    # ======================================================
    # RECEBIMENTO
    # ======================================================

    logger.info(
        "Rotina de Recebimento: OK"
    )

    scheduler.add_job(
        func=inbound.run,
        trigger="interval",
        hours=int(
            os.getenv(
                "TIME_UPDATE_JOB_RECEB",
                "1"
            )
        ),
        args=[
            os.getenv(
                "SPREDSHEET_REC"
            )
        ],
        id="recebimento",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )


    # ======================================================
    # DEVOLUÇÃO
    # ======================================================

    logger.info(
        "Rotina de Atualização: OK"
    )

    scheduler.add_job(
        func=outbound.run,
        trigger="interval",
        minutes=int(
            os.getenv(
                "TIME_UPDATE_JOB_BASE",
                "10"
            )
        ),
        id="devolucao",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )


    scheduler.start()


    logger.info(
        "Scheduler iniciado."
    )


def stop():

    logger.info(
        "Solicitando parada do Scheduler..."
    )


    if not scheduler.running:

        logger.info(
            "Scheduler já estava parado."
        )

        return


    scheduler.shutdown(
        wait=False
    )


    logger.info(
        "Scheduler parado."
    )