import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.player_currency import CurrencyType, PlayerCurrency
from app.models.player_inventory import PlayerInventory
from app.models.player_purchase_token import PlayerPurchaseToken
from app.repositories.player_currency_repository import PlayerCurrencyRepository
from app.repositories.player_inventory_repository import PlayerInventoryRepository
from app.repositories.player_purchase_token_repository import (
    PlayerPurchaseTokenRepository,
)
from app.schemas.purchase import (
    GooglePurchaseVerifyRequest,
    GooglePurchaseVerifyResponse,
    PurchaseRequest,
    PurchaseResponse,
)
from app.services.google_play_verifier import GooglePlayVerifier


# Server-side catalog: source of truth for (sku -> amount, currency_type).
# Must stay in sync with BillingService.SKU_TABLE in the Godot client.
GOOGLE_PLAY_SKU_CATALOG: dict[str, dict] = {
    "diamond_pack_10000": {"amount": 10000, "currency_type": CurrencyType.diamond},
    "diamond_pack_5000":  {"amount": 5000,  "currency_type": CurrencyType.diamond},
    "diamond_pack_1000":  {"amount": 1000,  "currency_type": CurrencyType.diamond},
    "diamond_pack_500":   {"amount": 500,   "currency_type": CurrencyType.diamond},
    "gold_pack_10000":    {"amount": 10000, "currency_type": CurrencyType.gold},
    "gold_pack_5000":     {"amount": 5000,  "currency_type": CurrencyType.gold},
}


class PurchaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.currency_repo = PlayerCurrencyRepository(db)
        self.inventory_repo = PlayerInventoryRepository(db)
        self.token_repo = PlayerPurchaseTokenRepository(db)
        self.google_verifier = GooglePlayVerifier()

    async def purchase(self, player_id: uuid.UUID, data: PurchaseRequest) -> PurchaseResponse:
        # Step 1: Deduct currency (raises 400 if insufficient)
        currency = await self.currency_repo.get_by_id(player_id, data.currency_type)
        if not currency:
            raise HTTPException(status_code=404, detail="Player currency not found")
        if currency.amount < data.price:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        currency = await self.currency_repo.update(currency, {"amount": currency.amount - data.price})

        # Step 2: Add to inventory (or increment quantity if already owned)
        existing_item = await self.inventory_repo.get_by_id(player_id, data.item_id, data.item_type)
        if existing_item:
            existing_item = await self.inventory_repo.update(
                existing_item, {"quantity": existing_item.quantity + 1}
            )
            quantity = existing_item.quantity
        else:
            new_item = PlayerInventory(
                player_id=player_id,
                item_id=data.item_id,
                item_type=data.item_type,
                quantity=1,
            )
            new_item = await self.inventory_repo.create(new_item)
            quantity = new_item.quantity

        return PurchaseResponse(
            item_id=data.item_id,
            item_type=data.item_type,
            quantity=quantity,
            currency_type=data.currency_type,
            amount_spent=data.price,
            currency_remaining=currency.amount,
        )

    async def verify_google_purchase(
        self, player_id: uuid.UUID, data: GooglePurchaseVerifyRequest
    ) -> GooglePurchaseVerifyResponse:
        # 1) SKU catalog lookup — never trust client-supplied amounts.
        sku_info = GOOGLE_PLAY_SKU_CATALOG.get(data.sku)
        if sku_info is None:
            raise HTTPException(status_code=400, detail="sku_unknown")

        amount: int = sku_info["amount"]
        currency_type: CurrencyType = sku_info["currency_type"]

        # 2) Idempotency check — if we've already redeemed this token, return current balance.
        existing = await self.token_repo.get_by_token(data.purchase_token)
        if existing is not None:
            currency = await self.currency_repo.get_by_id(player_id, currency_type)
            balance = currency.amount if currency else 0
            return GooglePurchaseVerifyResponse(
                credited=0,
                currency_type=currency_type,
                new_balance=balance,
                idempotent=True,
            )

        # 3) Verify with Google (or accept mock_ tokens in DEV_MODE).
        result = await self.google_verifier.verify(data.purchase_token, data.sku)
        if not result.valid:
            if result.error and result.error.startswith("google_status"):
                raise HTTPException(status_code=502, detail="google_api_error")
            raise HTTPException(status_code=402, detail="invalid_token")

        # 4) Credit currency + record token. Wrapped in a try to handle the race
        #    where a duplicate token slips past the get_by_token check above.
        currency = await self.currency_repo.get_by_id(player_id, currency_type)
        if currency is None:
            currency = PlayerCurrency(
                player_id=player_id,
                currency_type=currency_type,
                amount=0,
            )
            currency = await self.currency_repo.create(currency)

        currency = await self.currency_repo.update(
            currency, {"amount": currency.amount + amount}
        )

        token_record = PlayerPurchaseToken(
            player_id=player_id,
            purchase_token=data.purchase_token,
            sku=data.sku,
            platform=data.platform,
            credited_amount=amount,
            currency_type=currency_type,
        )
        try:
            await self.token_repo.create(token_record)
        except IntegrityError:
            # Concurrent redemption — roll back the credit by re-reading and adjusting.
            # The race winner already credited the player, so we just return their balance.
            await self.db.rollback()
            currency = await self.currency_repo.get_by_id(player_id, currency_type)
            balance = currency.amount if currency else 0
            return GooglePurchaseVerifyResponse(
                credited=0,
                currency_type=currency_type,
                new_balance=balance,
                idempotent=True,
            )

        return GooglePurchaseVerifyResponse(
            credited=amount,
            currency_type=currency_type,
            new_balance=currency.amount,
            idempotent=False,
        )
