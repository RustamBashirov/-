# Специальная часть моей дипломной работы.

### Описание


### Установка и запуск:
Клонируйте репозиторий.
Создайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Установите зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

### Запуск проекта
Можно менять только данные параметры в main.py:
- GNSS_SYSTEM
- NUMBER_SATELLITES
- MEASUREMENT_FILE
- NAVIGATION_FILE_GPS
- NAVIGATION_FILE_GLONASS
- TIME_POINT_MEASUREMENT
- TIME_FINAL

Запускайте исполняемый скрипт main.py и проект запустится
