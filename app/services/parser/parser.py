import pandas as pd
import numpy as np

from datetime import datetime

from app.services.database.models.carwash import Carwash
from app.services.parser.terminal_session import TerminalSession


class Parser:
    def __init__(self, sessions: list[TerminalSession]) -> None:
        self.sessions: list[TerminalSession] = sessions

    def get_carwashes(self) -> list[Carwash]:
        carwashes = list()
        for session in self.sessions:
            if session.active is False:
                session.login()

            table_sales = session.get_table_sales()
            if table_sales is None:
                continue

            df = pd.read_html(table_sales)[0]
            if df.empty:
                continue
            for row in df.values:
                carwashes.append(self.__parse_row_to_carwash(row))

        return carwashes

    def __parse_row_to_carwash(self, row: np.ndarray) -> Carwash:
        return Carwash(
            id=str(row[1]),
            date=datetime.strptime(row[2], "%d.%m.%Y %H:%M:%S"),
            type=row[3],
            mode=int(row[8].split()[1]),
        )
