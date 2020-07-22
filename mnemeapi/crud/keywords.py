from typing import List

from ..models.models import Keyword
from ..schemas import KeywordCreate


async def update_keywords(new_keywords: List[KeywordCreate], entry_id: int) -> None:
    await Keyword.filter(entry_id=entry_id).delete()
    _ = [await Keyword(word=kw.word.lower(), entry_id=entry_id).save() for kw in new_keywords]
