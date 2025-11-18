from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from src.web13hm.database.db import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    contacts = relationship("Contacts", back_populates="owner")
    created_at = Column("crated_at", DateTime, default=func.now())


class Contacts(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(50))
    number = Column(String(50))
    birthday = Column(Date(), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    extra_data = Column(String(150), nullable=True, default=None)
    created_at = Column("crated_at", DateTime, default=func.now())

    owner = relationship("User", back_populates="contacts")


Base.metadata.create_all(bind=engine)
