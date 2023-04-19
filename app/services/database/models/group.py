from sqlalchemy.orm import Mapped, mapped_column


from app.services.database.base import Base


class Group(Base):
    __tablename__ = "tg_group"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    name: Mapped[str]
