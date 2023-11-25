# Это приложение написано на python 3.11.
## Технологии Python311; Sqlite3; PyQt5
Чтобы его запустить нужно следовать след. порядку:

1. Нужно зайти в путь model/query/ и выбрать запрос и также созадть бд с названием 'products.db'
    > Можно изменить название бд в файле [model.py](model/model.py)

2. Создаем виртуальное окружение
```bash
python3.11 -m venv venv
```
3. Активируем его - venv/Scripts/activate
```bash
venv/Scripts/activate
```
4. Скачиваем все зависимости c файла requirements.txt
```bash
pip install -r requirements.txt
```
5. Запускаем main.py
```bash
python main.py
```