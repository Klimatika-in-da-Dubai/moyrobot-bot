import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.dao.user import UserDAO


async def create_pincode_for_user(user_id: int, session: AsyncSession):
    userdao = UserDAO(session)
    pincode = generate_pincode()
    await userdao.set_pincode(user_id, pincode)


def generate_pincode() -> str:
    number = random.randint(10, 99)
    pincode = str(number)

    if do_flip():
        return pincode + pincode[::-1]

    return pincode + pincode


def do_flip():
    return random.random() < 0.5
