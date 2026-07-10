from config import POST_TEMPLATE, SOLD_LINE, ACTIVE_LINE
from models import Account


def build_caption(account: Account) -> str:
    status_line = SOLD_LINE if account.status == "sold" else ACTIVE_LINE
    return POST_TEMPLATE.format(
        id=account.id,
        price=account.price,
        privyazka=account.privyazka,
        description=account.description,
        status_line=status_line,
    )
