from datetime import datetime
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.services.database.base import Base


class CorporateReport(Base):
    __tablename__ = "corporate_report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start: Mapped[datetime]
    end: Mapped[datetime]
    reported: Mapped[bool] = mapped_column(default=False)
