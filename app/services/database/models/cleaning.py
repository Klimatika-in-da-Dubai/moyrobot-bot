from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import BigInteger


from app.services.database.base import Base


class Cleaning(Base):
    """
    {
        "places": [
            {
                "place_name": "name",
                "works": [
                    {


                    }
                ]
            }
        ]
    }
    """

    __tablename__ = "cleaning"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, autoincrement=False
    )
    date: Mapped[datetime]
    cleaning: Mapped[JSON]
    approved: Mapped[bool] = mapped_column(default=False)
    notified: Mapped[bool] = mapped_column(default=False)
