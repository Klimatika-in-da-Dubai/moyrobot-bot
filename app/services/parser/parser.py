import pandas as pd
import asyncio
from datetime import datetime

from app.services.database.models.manual_start import ManualStart
from app.services.parser.terminal_session import TerminalSession

MANUAL_START_TEXT = "Ручной"


class Parser:
    def __init__(self, sessions: list[TerminalSession]) -> None:
        self.sessions: list[TerminalSession] = sessions

    async def get_manual_starts(self) -> list[ManualStart]:
        tasks = [
            asyncio.create_task(self.get_manual_starts_from_session(session))
            for session in self.sessions
        ]
        return [
            manual_start
            for manual_starts in await asyncio.gather(*tasks)
            for manual_start in manual_starts
        ]

    async def get_manual_starts_from_session(
        self, terminal_session: TerminalSession
    ) -> list[ManualStart]:
        async with terminal_session as session:
            table_sales_page = await session.get_table_sales_page()
        if table_sales_page is None:
            return []
        return self.__get_manual_starts_from_page(
            terminal_session.terminal_id, table_sales_page
        )

    def __get_manual_starts_from_page(
        self, terminal_id: int, table_sales_page: str
    ) -> list[ManualStart]:
        starts_df = self.__get_starts_datatframe(table_sales_page)
        if starts_df.empty:
            return []
        manual_starts = self.__filter_manual_starts(starts_df)

        return [
            self.__parse_row_to_manual_start(terminal_id, row)
            for _, row in manual_starts.iterrows()
        ]

    def __get_starts_datatframe(self, table_sales_page: str) -> pd.DataFrame:
        if table_sales_page == "":
            return pd.DataFrame()
        df = pd.read_html(table_sales_page)[0]
        return df

    def __filter_manual_starts(self, starts_df: pd.DataFrame) -> pd.DataFrame:
        return starts_df.loc[starts_df["Тип запуска  БУМ"] == MANUAL_START_TEXT]

    def __parse_row_to_manual_start(
        self, terminal_id: int, row: pd.Series
    ) -> ManualStart:
        return ManualStart(
            id=self.__get_id(row),
            terminal_id=terminal_id,
            date=self.__get_date(row),
            mode=self.__get_mode(row),
        )

    def __get_id(self, row) -> str:
        return row["Id"]

    def __get_date(self, row) -> datetime:
        return datetime.strptime(row["Дата"], "%d.%m.%Y %H:%M:%S")

    def __get_mode(self, row) -> int | None:
        if row["Режим  БУМ"] == "Режим":
            return None
        return int(row["Режим  БУМ"].split()[1])
