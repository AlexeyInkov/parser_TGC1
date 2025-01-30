import datetime
import os
import random

from typing import Dict
import json
import requests
from dotenv import load_dotenv, find_dotenv

from parser import Parser
from report import Report, get_path
from sys import argv

NODES = {
    "Ntog_9220": [
        3083,
        3236,
        4198,
        4326,
        4909,
        5173,
        7142,
        7147,
        7152,
        7183,
        7867,
        8569,
        9150,
        9153,
        9157,
        9162,
        9559,
        10761,
        13169,
        16449,
        16574,
        16880,
        18220,
        18224,
        26762,
        368907200,
        374864500,
        653668900,
        825685500,
        825685600,
        1553089000,
        1553089100,
        1718332600,
        1718346800,
        1773264200,
        1779600700,
        1843569400,
        2136760900,
        7673508700,
        7673508600
    ],
    "Ing_5050": [
        2036925500,
        2220821800,
        8692695266,
        8692694297
    ],
    "PrJ97v_15": [
        4342,
        12093,
        15828,
        15924
    ]
}
COOKIES = {
    "TGC1_Session": "4pooo82l4cncbqna7djgidi5qv",
    "session-cookie": "17c8f96630a1d0962dc95c5dbeb261f5210e724872387015865cc110dff5a0cc5ab259cbee7812b3a0fe3151b3f1524a",
    "_ga": "GA1.2.1491574608.1713893877",
    "_gid": "GA1.2.1727023081.1713893877",
    "csrf-token-name": "x_csrftoken",
    # "csrf-token-value": "17c9034a5a69d813e900b85e3249290746c64940b3c2e13803e6a3684cb920f281fc34b0541b9017"
}
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "TGC1_Session=4pooo82l4cncbqna7djgidi5qv; session-cookie=17c8f96630a1d0962dc95c5dbeb261f5210e724872387015865cc110dff5a0cc5ab259cbee7812b3a0fe3151b3f1524a; _ga=GA1.2.1491574608.1713893877; _gid=GA1.2.1727023081.1713893877; csrf-token-name=x_csrftoken",
    "Host": "portal.tgc1.ru",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows"
}

try:
    script, month_str, year = argv
except ValueError:
    month_str = datetime.date.today().month
    year = datetime.date.today().year


def get_accounts() -> Dict:
    if not find_dotenv():
        exit("Переменные окружения не загружены т.к отсутствует файл .env")
    else:
        load_dotenv()
    accounts_str = os.getenv("ACCOUNTS")
    accounts_dict = json.loads(accounts_str)
    return accounts_dict


def check_node(node):
    with open("Parser_TGC1/nodes.txt", "r", encoding="UTF-8") as file:
        while True:
            line = file.readline()
            if line and line.split("=")[0] == node:
                return True
            return False


def save_node(node, address):
    with open("nodes.txt", "a", encoding="UTF-8") as file:
        file.write("=".join((node, address, "\n")))


def main():
    session = requests.session()
    parser = Parser()
    month = int(month_str)

    session.cookies.clear_session_cookies()
    session.headers.update(HEADERS)
    cookies = requests.utils.cookiejar_from_dict(COOKIES)
    session.cookies.update(cookies)

    for login, password in get_accounts().items():
        parser.auth(session, login, password)
        try:
            company = parser.check_auth(session)
        except ConnectionError():
            print("ошибка Аутентификации")
            continue

        # nodes = NODES[login]
        nodes = parser.get_nodes(parser.get_page_with_nodes(session))  # TODO добавить пагинацию
        for node in nodes:
            file_path = parser.get_file_path(session, month, year, str(node))
            if file_path is None:
                print(f"{file_path=}")
                continue
            zipfile_path = parser.download_zipfile(session, file_path, node, month, login)
            if zipfile_path is None:
                continue
            report = Report(zipfile_path)
            if report.status is None:
                continue
            pdf = report.get_file_from_zip()
            os.remove(report.zipfile_path)
            image = report.get_image_from_pdf(pdf)
            text = report.get_text_from_image(image)
            os.remove(image)
            dir_name = os.path.join(
                os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),  # get_path()[2] # указать папку
                "parser_tgc1",
                str(month),
                company
            )
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            file_name, address = report.find_name(text)
            new_pdf = os.path.join(dir_name, file_name)

            if not check_node(node):
                save_node(node, address)

            if os.path.exists(new_pdf):
                new_pdf = f"{new_pdf[:-4]}_{str(random.randint(1000000, 10000000))}.pdf"
            os.rename(pdf, new_pdf)
            os.rmdir(report.zipfile_path[:-4])
        parser.logout(session)


if __name__ == '__main__':
    main()
    input("Press ENTER")
