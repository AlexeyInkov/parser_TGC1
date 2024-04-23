import datetime
import os
import random

from typing import Dict
import json
import requests
from dotenv import load_dotenv, find_dotenv

from parser import Parser
from report import Report
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
    for login, password in get_accounts().items():
        parser.auth(session, login, password)
        try:
            company = parser.check_auth(session)
        except ConnectionError():
            print("ошибка Аутентификации")
            continue

        # nodes = NODES[login]
        nodes = parser.get_nodes(parser.get_page_wiht_nodes(session))  # TODO добавить пагинацию
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
                os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),  # указать папку
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
