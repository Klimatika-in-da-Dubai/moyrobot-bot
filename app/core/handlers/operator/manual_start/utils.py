from aiogram.fsm.context import FSMContext


async def clear_manual_start_data(state: FSMContext):
    await state.update_data(id=None)
    await state.update_data(description=None)
    await state.update_data(photo_file_id=None)
    await state.update_data(payment_method=None)
    await state.update_data(payment_amount=None)
    await state.update_data(corporation_id=None)
