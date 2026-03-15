import os

import uvicorn

from app import db


def main() -> None:
    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", "8000"))
    run_db_init = db.env_flag("RUN_DB_INIT_ON_STARTUP", default=True)
    create_db_if_missing = db.env_flag("CREATE_DB_IF_MISSING", default=False)

    db.wait_for_database()

    if run_db_init:
        db.initialize_database(create_database_if_missing=create_db_if_missing)

    uvicorn.run("api.main:app", host=api_host, port=api_port)


if __name__ == "__main__":
    main()
