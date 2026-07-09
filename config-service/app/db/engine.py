import asyncpg
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


def _build_connect_args(app_name: str) -> dict:
    args: dict = {
        "timeout": 10,
        "command_timeout": 30,
        "server_settings": {"application_name": app_name},
    }
    hosts = settings.db_host_list
    if len(hosts) > 1:
        args["host"] = hosts
        args["target_session_attrs"] = "read-write"
    return args


_DISCONNECT_ERRORS = (
    asyncpg.exceptions.ConnectionDoesNotExistError,
    asyncpg.exceptions.InterfaceError,
    asyncpg.exceptions.PostgresConnectionError,
    asyncpg.exceptions.CannotConnectNowError,
    asyncpg.exceptions.ReadOnlySQLTransactionError,
)


def _attach_disconnect_handler(engine_) -> None:
    @event.listens_for(engine_.sync_engine, "handle_error")
    def _flag_disconnects(ctx):
        if isinstance(ctx.original_exception, _DISCONNECT_ERRORS):
            ctx.is_disconnect = True


engine = create_async_engine(
    settings.async_database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_reset_on_return="rollback",
    connect_args=_build_connect_args("config-service"),
    echo=False,
)

_attach_disconnect_handler(engine)
