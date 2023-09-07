from app.services.database.models.manual_start import ManualStart


def get_manual_start_mode_text(manual_start: ManualStart) -> str:
    if manual_start.mode is None:
        return "Неизвестно"
    return str(manual_start.mode)
