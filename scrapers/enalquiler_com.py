# На сайте есть фильтр по particular, поэтому дополнительную фильтрацию можно не применять
# В обоих случаях данные получаем из каталога объектов

import time
import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from database import insert_data, record_new_region


headers = {"user-agent": UserAgent().chrome}
errors = 0
max_local_errors = 5
timeout = 5


def get_response(url):
    global errors
    local_errors = 0
    while True:
        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
            if len(response.content) > 0:
                break
            else:
                errors += 1
                local_errors += 1
                if local_errors == max_local_errors:
                    print(f"[ERROR - Enalquiler] Превышено максимальное количество попыток ({max_local_errors})")
                    return False
                else:
                    print("[INFO - Enalquiler] Пробуем еще раз")
        except ConnectTimeout:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Enalquiler] Сервер не дает ответ более {timeout} секунд на странице {url}")
            if local_errors == max_local_errors:
                print(f"[ERROR - Enalquiler] Превышено максимальное количество попыток ({max_local_errors})")
                return False
            else:
                print("[INFO - Enalquiler] Пробуем еще раз")
        except ConnectionError:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Enalquiler] Ошибка подключения на странице {url}")
            if local_errors == max_local_errors:
                return False
            else:
                print("[INFO - Enalquiler] Пробуем еще раз")
        except ReadTimeout:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Enalquiler] Сервер выдал сломанные данные на странице {url}")
            if local_errors == max_local_errors:
                return False
            else:
                print("[INFO - Enalquiler] Пробуем еще раз")

    return response


def get_info_from_site(start_url, object_type, city):
    page = 1
    result = list()
    url = f"{start_url}&page={page}"
    response = get_response(url=url)
    bs_object = BeautifulSoup(response.content, "lxml")
    try:
        max_page = int(bs_object.find(name="ul", class_='pagination pull-right').find_all(name="li")[-2].text.strip())
    except Exception as ex:
        max_page = 1

    for page in range(1, max_page + 1):
        url = f"{start_url}&page={page}"
        response = get_response(url=url)
        if response:
            bs_object = BeautifulSoup(response.content, "lxml")
            cards = bs_object.find_all(name="li", id=True)
            index = 0
            for card in cards:
                try:
                    price = card.find(name="span", class_='propertyCard__price--value').text.strip().replace("\x80", " €")
                    image_url = card.div.picture
                    if image_url is None:
                        image_url = "No information"
                    else:
                        image_url = image_url.find(name="source", attrs={"image-extension": "or"})["srcset"]
                    characteristics = card.find(name="ul", class_="propertyCard__details").find_all(name="li")
                    square = characteristics[0].text.strip()
                    bedrooms = characteristics[1].text.strip()
                    if bedrooms == "Piso":
                        bedrooms = "No information"
                    if len(characteristics) > 2:
                        bathes = characteristics[2].text.strip()
                    else:
                        bathes = "No information"
                    title = card.find(name="div", class_='propertyCard__description hidden-xs').a.text.strip()
                    object_url = card.find(name="div", class_='propertyCard__description hidden-xs').a["href"]
                    description = card.find(name="p", class_='propertyCard__description--txt').text.strip()
                    region = card.find(name="div", class_="propertyCard__location").text.strip()
                    region = record_new_region(region=region, city=city)
                    data = {"mode": "rent", "title": title, "object_type": object_type, "price": price,
                            "square": square, "bedrooms": bedrooms, "bathes": bathes, "description": description,
                            "url": object_url, "image_url": image_url, "seller_type": "particular", "region": region,
                            "city": city}
                    result.append(data)
                except Exception as ex:
                    continue
            print(f"[INFO - Enalquiler] Страница {url} обработана. Было собрано {len(cards)} объектов")

    return result


def get_object_type(url):
    if "tipo=2" in url or "tipo=6" in url or "tipo=3" in url or "tipo=5" in url:
        object_type = "Pico"
    else:
        object_type = "Casa"
    return object_type


def main(url=None, without_delete=False, city=None):
    if url is None:
        example = "https://www.enalquiler.com/search?tipo=2&query_string=Malaga"
        text = "[INFO - Enalquiler] Выберете город и укажите фильтры поиска на сайте enalquiler.com."
        input_text = f"{text} Вставьте полученный URL ({example}):\n[INPUT - Enalquiler] >>>   "
        url = input(input_text).strip()
        city = int(input("[INPUT - Enalquiler] Введите id города: >>> "))
    object_type = get_object_type(url=url)
    start_time = time.time()
    result = get_info_from_site(start_url=url, object_type=object_type, city=city)
    print(f"[INFO - Enalquiler] Программа собрала {len(result)} объектов")
    print("[INFO - Enalquiler] Идет запись в базу данных")
    insert_data(objects=result, without_delete=without_delete, source="enalquiler")
    stop_time = time.time()
    print(f"[INFO - Enalquiler] На работу программы потребовалось {stop_time - start_time} секунд")
    print(f"[INFO - Enalquiler] Количество ошибок сервера: {errors}")


if __name__ == "__main__":
    main()
