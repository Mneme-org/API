from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String, index=True)

    username = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)

    journals = relationship("Journal", back_populates="owner")


class Journal(Base):
    __tablename__ = 'journals'

    id = Column(Integer, primary_key=True)
    pub_user_id = Column(String, ForeignKey('users.id'))
    name = Column(String, nullable=False)

    owner = relationship('User', back_populates='journals')
    entries = relationship('Entry', back_populates='journal')


class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    jrnl_id = Column(Integer, ForeignKey('journals.id'))
    short = Column(String, nullable=False)
    long = Column(String, nullable=True)

    date = Column(String, nullable=False)

    journal = relationship('Journal', back_populates='entries')
    keywords = relationship('Keyword', back_populates='entry')


class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id'))
    word = Column(String, nullable=False)

    entry = relationship('Entry', back_populates='keywords')