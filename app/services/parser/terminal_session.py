import aiohttp
import logging


class TerminalSession:
    def __init__(self, terminal_id: int, url: str, login: str, password: str) -> None:
        self.terminal_id = terminal_id
        self.url = url
        self.__login = login
        self.__password = password
        self.__login_url = url + "/Account/Login"
        self.__table_sales_url = url + "/Admin/_TableSales"
        self.__cookie_jar = aiohttp.CookieJar()
        self.active = False

    def is_active(self) -> bool:
        return self.active

    async def login(self):
        logging.debug("Login to terminal id=%s url=%s", self.terminal_id, self.url)
        try:
            async with aiohttp.ClientSession(cookie_jar=self.__cookie_jar) as session:
                async with session.post(
                    self.__login_url,
                    data={"Login": self.__login, "Password": self.__password},
                ) as resp:
                    resp.raise_for_status()
                logging.debug("Login successfull id=%s url=%s", self.terminal_id, self.url)
                self.active = True
        except Exception as e:
            logging.error(e)
            self.active = False

    async def get_table_sales_page(self) -> str | None:
        logging.debug("Getting table sales page id=%s url=%s", self.terminal_id, self.url)
        if self.is_active is False:
            return None
        try:
            async with aiohttp.ClientSession(cookie_jar=self.__cookie_jar) as session:
                async with session.get(self.__table_sales_url) as resp:
                    resp.raise_for_status()
                    logging.debug("Getting table sales page successfull id=%s url=%s", self.terminal_id, self.url)
                    return await resp.text()
        except Exception as e:
            logging.error(e)
            self.active = False
            return None
