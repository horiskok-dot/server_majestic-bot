from ..database import Base, engine, ensure_database_schema
from ..utils.logging import setup_logging
from .telegram_bot import run_bot_forever


def main() -> None:
    setup_logging()
    Base.metadata.create_all(bind=engine)
    ensure_database_schema()
    run_bot_forever()


if __name__ == "__main__":
    main()
