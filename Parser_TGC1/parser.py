import os
import re
import requests


class Parser:
    url = "https://portal.tgc1.ru/"

    def auth(self, session: requests.Session, login, password):
        data = {
            "login": login,
            "password": password
        }
        x_csrftoken = session.cookies.get("x_csrftoken", default=None)
        if x_csrftoken is not None:
            data["x_csrftoken"] = x_csrftoken

        auth = session.post(
            self.url + "auth/makeLogin",
            data=data)

    def check_auth(self, session: requests.Session):
        check = session.get(self.url)
        print(check.status_code)
        if check.status_code == 200:
            company = re.compile(r"(?:cabinet\">)(.+)(?:<)").search(check.text).group(1)
            print(f"Вы аутентифицированы как {company}")
            return company.replace('"', "").replace(' ', "_").replace('__', "_")
        raise ConnectionError

    def get_page_with_nodes(self, session: requests.Session):
        return session.post(self.url + "directorate/nodes", data={"onpage": 100}).text

    def get_nodes(self, html_page: str):
        nod = re.compile(r"(?:<tr data-id=\")(\d+)(?:\">)")
        nodes = nod.findall(html_page)
        print(nodes)
        return nodes

    def get_file_path(self, session: requests.Session, month: int, year: int, node: str):
        data = {
            "type": "1",  # 1-pdf, 2-cvs
            "nodes[]": node,  # внутренний номер узла
            "from": f"01.{month}.{year}",
            "to": f"15.{month}.{year}",
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
