from sqlalchemy import Column, DateTime, String, Integer

from app.services.database.base import Base


class Carwash(Base):
    __tablename__ = "carwashes"

    id = Column(String, primary_key=True, unique=True, autoincrement=False)
    date = Column(DateTime)
    type = Column(String)
    mode = Column(Integer)
