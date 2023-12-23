﻿import os
import re
import requests


class Parser:
    url = "https://portal.tgc1.ru/"

    def auth(self, session: requests.Session, login, password):
        session.post(
            self.url + "auth/makeLogin",
            data={
                "login": login,
                "password": password
            })

    def check_auth(self, session: requests.Session):
        check = session.get(self.url)
        if check.status_code == 200:
            company = re.compile(r"(?:cabinet\">)(.+)(?:<)").search(check.text).group(1)
            print(f"Вы аутентифицированы как {company}")
            return company.replace('"', "").replace(' ', "_").replace('__', "_")
        raise ConnectionError

    def get_page_wiht_nodes(self, session: requests.Session):
        return session.get(self.url + "directorate/nodes").text

    def get_nodes(self, html_page: str):
        nod = re.compile(r"(?:<tr data-id=\")(\d+)(?:\">)")
        nodes = nod.findall(html_page)
        print(nodes)
        return nodes

    def get_file_path(self, session: requests.Session, month: int, node: str):
        data = {
            "type": "1",  # 1-pdf, 2-cvs
            "nodes[]": node,  # внутренний номер узла
            "from": "25." + str(month - 1) + ".2023",
            "to": "22." + str(month) + ".2023",
            "encoding": "Windows1251"
        }
        response_file_path = session.post(self.url + "directorate/reports/downloadPost", data)
        if response_file_path.status_code == 200 and response_file_path.text != '[]':
            return "".join(response_file_path.text.split("\"")[3].split("\\"))  # убрал лишнее

    def download_zipfile(self, session: requests.Session, file_path: str, node: str, month: int, login):
        response = session.post(self.url + "files/tmp/" + file_path, stream=True)
        dir_name = f"report/{month}/{login}"
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_name = f"report{node}_2023_{month}.zip"
        zipfile_path = os.path.join(dir_name, file_name)
        with open(zipfile_path, "wb") as file:
            if response.content != b'':
                for chunk in response.iter_content(chunk_size=512):
                    if chunk:
                        file.write(chunk)
                return zipfile_path
        os.remove(zipfile_path)

    def logout(self, session: requests.Session):
        session.get(self.url + "auth/logout")
