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


#  подгрузка месяца
try:
    script, first = argv
except ValueError:
    first = datetime.date.today().month


def get_accounts() -> Dict:
    if not find_dotenv():
        exit("Переменные окружения не загружены т.к отсутствует файл .env")
    else:
        load_dotenv()
    accounts_str = os.getenv("ACCOUNTS")
    accounts_dict = json.loads(accounts_str)
    return accounts_dict


def main():
    session = requests.session()
    parser = Parser()
    month = int(first)
    for login, password in get_accounts().items():
        parser.auth(session, login, password)
        try:
            company = parser.check_auth(session)
        except ConnectionError():
            print("ошибка Аутентификации")
        else:
            nodes = parser.get_nodes(parser.get_page_wiht_nodes(session))
            for node in nodes:
                file_path = parser.get_file_path(session, month, str(node))
                if file_path is not None:
                    zipfile_path = parser.download_zipfile(session, file_path, node, month, login)
                    if zipfile_path:
                        report = Report(zipfile_path)
                        if report.status is not None:
                            pdf = report.get_file_from_zip()
                            os.remove(report.zipfile_path)
                            image = report.get_image_from_pdf(pdf)
                            text = report.get_text_from_image(image)
                            os.remove(image)
                            dir_name = os.path.join(
                                os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop'),   # указать папку
                                "parser_tgc1",
                                str(month),
                                company
                                )
                            if not os.path.exists(dir_name):
                                os.makedirs(dir_name)
                            new_pdf = os.path.join(dir_name, report.find_name(text))
                            if os.path.exists(new_pdf):
                                new_pdf = f"{new_pdf[:-4]}_{str(random.randint(1000000,10000000))}.pdf"
                            os.rename(pdf, new_pdf)
                            os.rmdir(report.zipfile_path[:-4])
#                            with open(f"{new_pdf[:-3]}txt", "w") as txt:
#                                txt.write(text)
            parser.logout(session)


if __name__ == '__main__':
    main()
    input("Press ENTER")
