from app.services.database.models.shift import CloseShift, OpenShift


def get_text(shift: OpenShift | CloseShift) -> str:
    if isinstance(shift, OpenShift):
        head = "Открытие смены"
    else:
        head = "Закрытие смены"

    antifreeze_message = ""
    if shift.antifreeze_count != 0:
        antifreeze_message = f"*Незамерзайка:* {shift.antifreeze_count}\n"

    chemistry_check_message = ""
    if shift.chemistry_check:
        chemistry_check_message = "*Нужно больше\\!*"

    problems = get_problems_text(shift)

    cleaning_message = ""

    if isinstance(shift, OpenShift):
        cleaning = "👍" if shift.cleaning_check else "👎"
        cleaning_message = f"*Качество уборки:* {cleaning}"

    return (
        f"{head}\n\n"
        f"*Касса:* {shift.money_amount}\n"
        f"{antifreeze_message}"
        f"*Химия:* {shift.chemistry_count} {chemistry_check_message}\n"
        f"{problems}"
        f"{cleaning_message}"
    )


def get_problems_text(shift: OpenShift | CloseShift) -> str:
    if all([shift.robot_leak_check, shift.robot_movement_check, shift.gates_check]):
        return ""

    robot_movement = "\t\t__Хода робота__\n" if not shift.robot_movement_check else ""
    robot_leak = "\t\t__Протечка робота__\n" if not shift.robot_leak_check else ""
    gates_check = "\t\t__Работа ворот__\n" if not shift.gates_check else ""

    return "*Проблемы:*\n" + robot_movement + robot_leak + gates_check
