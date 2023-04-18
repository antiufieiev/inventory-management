from telegram import Update

from database.model import UserTable
from entity.entities import AccessLevel


def checkUserAccess(update: Update) -> int:
    query = UserTable.select().where(UserTable.user_id == update.effective_user.id)
    if query.exists():
        for user in query:
            return user.access_level
    else:
        return AccessLevel.NONE
