import requests
import logging


class TerminalSession:
    def __init__(self, url: str, login: str, password: str) -> None:
        self.url = url
        self.user_login = login
        self.user_password = password
        self.login_url = url + "/Account/Login"
        self.table_sales_url = url + "/Admin/_TableSales"
        self.active = False
        self.__session = requests.Session()

    def login(self) -> bool:
        logging.debug("Try to login")

        data = {"Login": self.user_login, "Password": self.user_password}
        timeout = 60

        try:
            response = self.__session.post(self.login_url, data=data, timeout=timeout)
        except requests.Timeout:
            self.active = False
            logging.error("Login timeout")
            return False
        except requests.ConnectionError:
            self.active = False
            logging.error("Login ConnectionError")
            return False

        if response.url == self.login_url:
            self.active = False
            logging.error("Login Failed")
            return False

        logging.debug("Login successful")
        self.active = True
        return True

    def get_table_sales(self) -> str | None:
        logging.debug("Getting table sales")
        timeout = 60
        try:
            response = self.__session.get(self.table_sales_url, timeout=timeout)
        except requests.Timeout:
            self.active = False
            logging.error("Tables sales get Timeout")
            return None
        except requests.ConnectionError:
            self.active = False
            logging.error("Table sales ConnectionError")
            return None

        logging.debug("Getting table sales successful")
        return response.text
