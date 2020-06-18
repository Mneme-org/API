from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, index=True)

    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)

    journals = relationship("Journal", back_populates="owner", cascade="delete")


class Journal(Base):
    __tablename__ = 'journals'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    name_lower = Column(String, nullable=False, index=True)

    owner = relationship('User', back_populates='journals')
    entries = relationship('Entry', back_populates='journal', cascade="delete")


class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True, index=True)
    jrnl_id = Column(Integer, ForeignKey('journals.id'))
    short = Column(String, nullable=False)
    long = Column(String, nullable=True)

    # YYYY-MM-DD HH:MM format in UTC timezone
    date = Column(DateTime, nullable=False)

    journal = relationship('Journal', back_populates='entries')
    keywords = relationship("Keyword", backref="entry", cascade="delete")

class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id'))
    word = Column(String, nullable=False)
