import logging
import random
import uuid

import asyncpg
from fastapi import HTTPException
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.models.player_currency import CurrencyType
from app.models.player_inventory import PlayerInventory, ItemType
from app.repositories.player_currency_repository import PlayerCurrencyRepository
from app.repositories.player_inventory_repository import PlayerInventoryRepository
from app.schemas.spin import SpinRequest, SpinResponse, SpinResultItem

logger = logging.getLogger(__name__)

SPIN_COST = 1000


def _economy_connect_args() -> dict:
    args: dict = {
        "timeout": 10,
        "command_timeout": 30,
        "server_settings": {"application_name": "player-service-spin"},
    }
    hosts = settings.db_host_list
    if len(hosts) > 1:
        args["host"] = hosts
        args["target_session_attrs"] = "read-write"
    return args


_economy_engine = create_async_engine(
    settings.async_economy_database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_reset_on_return="rollback",
    connect_args=_economy_connect_args(),
)


_DISCONNECT_ERRORS = (
    asyncpg.exceptions.ConnectionDoesNotExistError,
    asyncpg.exceptions.InterfaceError,
    asyncpg.exceptions.PostgresConnectionError,
    asyncpg.exceptions.CannotConnectNowError,
    asyncpg.exceptions.ReadOnlySQLTransactionError,
)


@event.listens_for(_economy_engine.sync_engine, "handle_error")
def _flag_disconnects(ctx):
    if isinstance(ctx.original_exception, _DISCONNECT_ERRORS):
        ctx.is_disconnect = True


class SpinService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.currency_repo = PlayerCurrencyRepository(db)
        self.inventory_repo = PlayerInventoryRepository(db)

    async def spin(
        self, player_id: uuid.UUID, data: SpinRequest
    ) -> SpinResponse:
        total_cost = data.spin_count * SPIN_COST

        # Step 1: Deduct currency
        currency = await self.currency_repo.get_by_id(player_id, data.wheel_type)
        if not currency:
            raise HTTPException(status_code=404, detail="Player currency not found")
        if currency.amount < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        currency = await self.currency_repo.update(
            currency, {"amount": currency.amount - total_cost}
        )

        # Step 2: Fetch wheel items directly from economy_db
        wheel_items = await self._fetch_wheel_items(data.wheel_type)
        if not wheel_items:
            raise HTTPException(status_code=500, detail="No wheel items configured")

        # Step 3: Perform spins
        results: list[SpinResultItem] = []
        for _ in range(data.spin_count):
            result = await self._do_single_spin(player_id, wheel_items, data.wheel_type)
            results.append(result)

        # Step 4: Get final currency balance
        await self.db.refresh(currency)

        return SpinResponse(
            results=results,
            currency_type=data.wheel_type,
            total_cost=total_cost,
            currency_remaining=currency.amount,
        )

    async def _fetch_wheel_items(self, wheel_type: CurrencyType) -> list[dict]:
        query = text(
            "SELECT id, wheel_type, slot_index, item_id, item_type, "
            "currency_reward, shop_price, weight, display_name, image "
            "FROM lucky_wheel_item WHERE wheel_type = :wt ORDER BY slot_index"
        )
        async with _economy_engine.connect() as conn:
            result = await conn.execute(query, {"wt": wheel_type.value})
            rows = result.mappings().all()
            return [dict(row) for row in rows]

    async def _do_single_spin(
        self,
        player_id: uuid.UUID,
        wheel_items: list[dict],
        wheel_type: CurrencyType,
    ) -> SpinResultItem:
        # Weighted random selection
        weights = [item["weight"] for item in wheel_items]
        selected = random.choices(wheel_items, weights=weights, k=1)[0]

        result = SpinResultItem(
            slot_index=selected["slot_index"],
            item_id=selected.get("item_id"),
            item_type=selected.get("item_type"),
            currency_reward=selected.get("currency_reward"),
            display_name=selected["display_name"],
            image=selected["image"],
        )

        if selected.get("currency_reward"):
            # Currency reward: add to player balance
            currency = await self.currency_repo.get_by_id(player_id, wheel_type)
            if currency:
                await self.currency_repo.update(
                    currency, {"amount": currency.amount + selected["currency_reward"]}
                )
        elif selected.get("item_id") and selected.get("item_type"):
            # Item reward: check for duplicate
            item_type_enum = ItemType(selected["item_type"])
            existing = await self.inventory_repo.get_by_id(
                player_id, selected["item_id"], item_type_enum
            )

            if existing:
                # Duplicate: compensate with currency (50% of shop_price)
                shop_price = selected.get("shop_price", 0)
                compensation = max(int(shop_price * 0.5), 1)
                result.is_duplicate = True
                result.compensation_amount = compensation

                currency = await self.currency_repo.get_by_id(player_id, wheel_type)
                if currency:
                    await self.currency_repo.update(
                        currency, {"amount": currency.amount + compensation}
                    )
            else:
                # New item: add to inventory
                new_item = PlayerInventory(
                    player_id=player_id,
                    item_id=selected["item_id"],
                    item_type=item_type_enum,
                    quantity=1,
                )
                await self.inventory_repo.create(new_item)

        return result
