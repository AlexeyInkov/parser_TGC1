# Скачивание и переименование отчетов с портала ПАО ТГК-1 portal.tgc1.ru

## Установка

#### Установка зависимостей

```pip install -r requirements.txt```

#### Установка ПО

- TESSERACT ORC
    - ```https://github.com/UB-Mannheim/tesseract/wiki```
- POPPLER-WINDOWS
    - ```https://github.com/oschwartz10612/poppler-windows/releases/```

#### создание .env файла по шаблону .env_template

1. словарь логин: пароль
2. путь установки TESSERACT ORC
3. путь установки POPPLER-WINDOWS
4. путь к результатам

#### Запуск

- ```python main.py month year```
- month порядковый номер месяца (int)
- year год 4 символа (int)