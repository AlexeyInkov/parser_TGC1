import re
import zipfile
import pytesseract as pt
import os
from typing import Tuple
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv, find_dotenv


def get_path() -> Tuple:
    if not find_dotenv():
        exit("Переменные окружения не загружены т.к отсутствует файл .env")
    load_dotenv()
    return os.getenv("TESSERACT"), os.getenv("POPPLER_PATH")


class Report:
    tesseract = get_path()[0]
    accept_rep = None
    deny_rep = None
    status = None

    def __init__(self, zipfile_path):
        self.zipfile_path = zipfile_path
        self.check_report()

    def check_report(self):
        zip_file = zipfile.ZipFile(self.zipfile_path)
        for text_file in zip_file.infolist():
            if text_file.filename == 'ÄΓ¬½«¡Ñ¡¡δÑ «ΓτÑΓδ.pdf':
                self.deny_rep = 'ÄΓ¬½«¡Ñ¡¡δÑ «ΓτÑΓδ.pdf'
            elif text_file.filename == 'Åα¿¡∩ΓδÑ «ΓτÑΓδ.pdf':
                self.accept_rep = 'Åα¿¡∩ΓδÑ «ΓτÑΓδ.pdf'
        if self.accept_rep:
            self.status = True
        if not self.accept_rep and self.deny_rep:
            self.status = False
        return self.status

    def get_file_from_zip(self):
        with zipfile.ZipFile(self.zipfile_path, 'r') as zip_file:
            if self.status:
                zip_file.extract(self.accept_rep, self.zipfile_path[:-4])
                self.accept_rep = os.path.join(self.zipfile_path[:-4], self.accept_rep)
                return self.accept_rep
            elif not self.status is None:
                zip_file.extract(self.deny_rep, self.zipfile_path[:-4])
                self.deny_rep = os.path.join(self.zipfile_path[:-4], self.deny_rep)
                return self.deny_rep

    def get_image_from_pdf(self, input_pdf_path):
        dir_name, filename = os.path.split(input_pdf_path)
        images = convert_from_path(
            input_pdf_path, 200, poppler_path=get_path()[1]
        )
        for image in images:
            image_path = os.path.join(dir_name, f"{filename[:-4]}.png")
            image.save(image_path)
            print(f"(Report.PDFtoImage) Создан файл {image_path}")
        return image_path

    def get_text_from_image(self, image_path):
        pt.pytesseract.tesseract_cmd = self.tesseract
        text = pt.image_to_string(Image.open(image_path), lang="rus")
        return text

    def find_name(self, text):
        list = text.split("\n")
        address_check = False
        period_check = False
        for line in list:
            if line.startswith("Адрес"):
                try:
                    n = line.index("Номер прибора")
                except:
                    address = line[7:]
                else:
                    address = line[7:n - 1]
                address_check = True
            if line.startswith("Отчет (акт)"):
                period = line[-7:]
                period_check = True
            if address_check and period_check:
                break
        else:
            address = "null"
            period = "null"

        newfilename = f'{self.status}_{period}_{address}.pdf'
        print(newfilename)
        newfilename = re.sub(r'[|*?<>:,\\\n\r\t\v]', "_", newfilename)
        newfilename = newfilename.replace(" ", "_").replace("__", "_")
        print(f'(report.find_name) новое имя: ', newfilename)
        return newfilename, address
