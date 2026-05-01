import os
from datetime import datetime
from pathlib import Path

import requests

BASE_DIR = Path(__file__).parent
URL = 'https://api.thecatapi.com/v1/images/search'
CATS_DIR = CATS_DIR = BASE_DIR / 'cats'


def get_new_image_url():
    response = requests.get(URL).json()
    random_cat = response[0].get('url')
    return random_cat


def download_file(url):
    filename = url.split('/')[-1]
    response = requests.get(url)
    response.raise_for_status()  # Проверка, что запрос выполнен успешно
    with open(CATS_DIR / filename, 'wb') as file:
        file.write(response.content)


def download_new_cat_image():
    url = get_new_image_url()
    download_file(url)


def create_dir(dir_name):
    os.makedirs(dir_name, exist_ok=True)


def list_dir(dir_name):
    print(
        *os.listdir(dir_name),
        sep='\n'
    )


def main():
    create_dir(CATS_DIR)
    for _ in range(100):
        download_new_cat_image()


if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    print(f'Время выполнения программы: {end_time - start_time}.')
    list_dir(CATS_DIR)
