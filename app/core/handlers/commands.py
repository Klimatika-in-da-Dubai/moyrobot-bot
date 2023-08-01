from aiogram import Router, types, Bot
from aiogram.filters import Command, CommandObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.services.database.dao.cleaning import CleaningDAO
from app.services.notifier.cleaning import CleaningNotifier

commands_router = Router(name="menu-router")


@commands_router.message(Command(commands=["id"]))
async def cmd_id(message: types.Message) -> None:
    await message.answer(f"Ваш id: *`{message.chat.id}`*")


@commands_router.message(Command(commands=["cleaning"]))
async def cleaning(
    message: types.Message,
    command: CommandObject,
    bot: Bot,
    session: async_sessionmaker,
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
