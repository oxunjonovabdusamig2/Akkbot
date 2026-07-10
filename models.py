from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    id: int
    price: str
    privyazka: str
    description: str
    photo_id: Optional[str]
    video_id: Optional[str]
    status: str  # "active" yoki "sold"
    message_id: Optional[int]
    created_at: str
    created_by: int
