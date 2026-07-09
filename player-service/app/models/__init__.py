from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.player_profile import PlayerProfile  # noqa: E402
from app.models.player_stats import PlayerStats  # noqa: E402
from app.models.player_currency import PlayerCurrency  # noqa: E402
from app.models.player_inventory import PlayerInventory  # noqa: E402
from app.models.player_equipment import PlayerEquipment  # noqa: E402
from app.models.player_selected_character import PlayerSelectedCharacter  # noqa: E402
from app.models.player_achievement import PlayerAchievement  # noqa: E402
from app.models.player_rank import PlayerRank  # noqa: E402
from app.models.player_auth import PlayerAuth  # noqa: E402
from app.models.player_session import PlayerSession  # noqa: E402
from app.models.player_purchase_token import PlayerPurchaseToken  # noqa: E402

__all__ = [
    "Base",
    "PlayerProfile",
    "PlayerStats",
    "PlayerCurrency",
    "PlayerInventory",
    "PlayerEquipment",
    "PlayerSelectedCharacter",
    "PlayerAchievement",
    "PlayerRank",
    "PlayerAuth",
    "PlayerSession",
    "PlayerPurchaseToken",
]
