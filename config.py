import os

from dotenv import load_dotenv
from dotenv import set_key


ENV_FILE = ".env"


def configuration(
    spreedSheetRec,
    spreedSheetDev,
    sheetNameBaseBi,
    jobTimeReceb,
    jobTimeUpdate,
    daysLimitDev,
    daysLimitReceb
):

    set_key(
        ENV_FILE,
        "SPREDSHEET_REC",
        spreedSheetRec
    )

    set_key(
        ENV_FILE,
        "SPREDSHEET_DEV",
        spreedSheetDev
    )

    set_key(
        ENV_FILE,
        "SHEET_NAME_BASE_BI",
        sheetNameBaseBi
    )

    set_key(
        ENV_FILE,
        "TIME_UPDATE_JOB_RECEB",
        jobTimeReceb
    )

    set_key(
        ENV_FILE,
        "TIME_UPDATE_JOB_BASE",
        jobTimeUpdate
    )

    set_key(
        ENV_FILE,
        "DAYS_LIMIT_DEV",
        daysLimitDev
    )

    set_key(
        ENV_FILE,
        "DAYS_LIMIT_RECEB",
        daysLimitReceb
    )

    load_dotenv(
        ENV_FILE,
        override=True
    )