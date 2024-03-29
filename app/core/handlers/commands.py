from aiogram import Router, types, Bot, F
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.dao.cleaning import CleaningDAO
from app.services.database.dao.group import GroupDAO
from app.services.database.dao.user import UserDAO
from app.services.database.models.group import Group
from app.services.notifier.cleaning import CleaningNotifier
from app.utils.pincode import create_pincode_for_user

commands_router = Router(name="menu-router")


@commands_router.message(Command(commands=["id"]))
async def cmd_id(message: types.Message) -> None:
    await message.answer(f"Ваш id: *`{message.chat.id}`*")


@commands_router.message(Command(commands=["cleaning"]))
async def cleaning(
    message: types.Message,
    command: CommandObject,
    bot: Bot,
    session: AsyncSession,
) -> None:
    cleaningdao = CleaningDAO(session)
    cleaning_notifier = CleaningNotifier(bot, session)
    if command.args is None:
        await message.answer("No id's specified")
        return
    args = map(int, command.args.split())

    for id in args:
        cleaning = await cleaningdao.get_by_id(id)
        if cleaning is None:
            await message.answer(f"No cleaning with id \\= {id}")
            continue
        await cleaning_notifier.send_notify(message.chat.id, cleaning, debug=True)


@commands_router.message(
    Command(commands=["addgroup"]),
    F.chat.type.in_(["group", "supergroup"]),
)
async def addchat(message: types.Message, session: AsyncSession):
    userdao = UserDAO(session)
    if not await userdao.is_admin(message.from_user.id):  # type: ignore
        return

    groupdao = GroupDAO(session)
    group = Group(id=message.chat.id, name=message.chat.title)

    if await groupdao.get_by_id(group.id) is not None:
        await message.answer("Группа уже добавлена")
        return

    await groupdao.add_group(group)
    await message.answer("Группа успешно добавлена")


@commands_router.message(
    Command(commands=["pincode"]), F.chat.type.in_([ChatType.PRIVATE])
)
async def send_pincode(message: types.Message, session: AsyncSession):
    userdao = UserDAO(session)
    user = await userdao.get_by_id(id_=message.chat.id)
    if user is None:
        await message.answer("Вы не являетесь пользователем бота")
        return

    pincode = await userdao.get_pincode(user.id)

    if pincode is None:
        await create_pincode_for_user(user.id, session)
        pincode = await userdao.get_pincode(user.id)

    await message.answer(f"Ваш пинкод: {pincode}")
