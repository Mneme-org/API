from typing import List

from sqlalchemy.orm import Session

from ..models.models import Keyword
from ..schemas import KeywordCreate


def update_keywords(db: Session, new_keywords: List[KeywordCreate], entry_id: int) -> None:
    db.query(Keyword).filter(Keyword.entry_id == entry_id).delete()
    db.add_all([Keyword(word=kw.word.lower(), entry_id=entry_id) for kw in new_keywords])
    db.commit()
