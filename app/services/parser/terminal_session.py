import aiohttp
import logging


class TerminalSession:
    def __init__(self, url: str, login: str, password: str) -> None:
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
        logging.debug(f"Login to terminal {self.url}")
        try:
            async with aiohttp.ClientSession(cookie_jar=self.__cookie_jar) as session:
                async with session.post(
                    self.__login_url,
                    data={"Login": self.__login, "Password": self.__password},
                ) as resp:
                    print(resp.status)
                    resp.raise_for_status()
                    self.active = True
        except Exception as e:
            logging.error(e)
            self.active = False

    async def get_table_sales_page(self) -> str:
        logging.debug(f"Getting table sales page {self.url}")
        if self.is_active is False:
            return ""
        try:
            async with aiohttp.ClientSession(cookie_jar=self.__cookie_jar) as session:
                async with session.get(self.__table_sales_url) as resp:
                    resp.raise_for_status()
                    return await resp.text()
        except Exception as e:
            logging.error(e)
            self.active = False
            return ""
