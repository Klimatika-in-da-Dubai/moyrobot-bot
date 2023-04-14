import pandas as pd
import numpy as np

from datetime import datetime

from app.services.database.models.manual_start import ManualStart
from app.services.parser.terminal_session import TerminalSession

MANUAL_START_TEXT = "Автоматический"


class Parser:
    def __init__(self, sessions: list[TerminalSession]) -> None:
        self.sessions: list[TerminalSession] = sessions

    async def get_manual_starts(self) -> list[ManualStart]:
        manual_starts = list()
        for session in self.sessions:
            if session.is_active() is False:
                await session.login()
            manual_starts.extend(await self.get_manual_starts_from_session(session))
        return manual_starts

    async def get_manual_starts_from_session(
        self, session: TerminalSession
    ) -> list[ManualStart]:
        table_sales_page = await session.get_table_sales_page()
        if table_sales_page is None:
            return []
        return self.__get_manual_starts_from_page(table_sales_page)

    def __get_manual_starts_from_page(self, table_sales_page: str) -> list[ManualStart]:
        starts_df = self.__get_starts_datatframe(table_sales_page)
        if starts_df.empty:
            return []
        manual_starts = self.__filter_manual_starts(starts_df)

        return [self.__parse_row_to_manual_start(row) for row in manual_starts.values]

    def __get_starts_datatframe(self, table_sales_page: str) -> pd.DataFrame:
        if table_sales_page == "":
            return pd.DataFrame()
        df = pd.read_html(table_sales_page)[0]
        return df

    def __filter_manual_starts(self, starts_df: pd.DataFrame) -> pd.DataFrame:
        return starts_df.loc[starts_df["Тип запуска  БУМ"] == MANUAL_START_TEXT]

    def __parse_row_to_manual_start(self, row: np.ndarray) -> ManualStart:
        return ManualStart(
            id=self.__get_id(row),
            date=self.__get_date(row),
            mode=self.__get_mode(row),
        )

    def __get_id(self, row) -> str:
        return str(row[1])

    def __get_date(self, row) -> datetime:
        return datetime.strptime(row[2], "%d.%m.%Y %H:%M:%S")

    def __get_mode(self, row) -> int | None:
        if row[8] == np.nan:
            return None
        return int(row[8].split()[1])
