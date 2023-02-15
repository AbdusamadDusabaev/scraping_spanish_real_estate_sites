# На сайте есть фильтр по particular, поэтому дополнительную фильтрацию можно не применять.
# Собрать данные из каталога не получится, поэтому в обоих случаях алгоритм сбора данных одинаковый

import time
import requests
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
from database import insert_data, record_new_region


domain = "https://www.yaencontre.com"
headers = {"user-agent": UserAgent().chrome}
timeout = 5
errors = 0
max_local_errors = 5


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
                    print(f"[ERROR - Yaencontre] Превышено максимальное количество попыток ({max_local_errors})")
                    return False
                else:
                    print("[INFO - Yaencontre] Пробуем еще раз после 30-секундной паузы")
                    time.sleep(30)
        except ConnectTimeout:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Yaencontre] Сервер не дает ответ более {timeout} секунд на странице {url}")
            if local_errors == max_local_errors:
                print(f"[ERROR - Yaencontre] Превышено максимальное количество попыток ({max_local_errors})")
                return False
            else:
                print("[INFO - Yaencontre] Пробуем еще раз после 30-секундной паузы")
                time.sleep(30)
        except ConnectionError:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Yaencontre] Ошибка подключения на странице {url}")
            if local_errors == max_local_errors:
                return False
            else:
                print("[INFO - Yaencontre] Пробуем еще раз после 30-секундной паузы")
                time.sleep(30)
        except ReadTimeout:
            errors += 1
            local_errors += 1
            print(f"[ERROR - Yaencontre] Сервер выдал сломанные данные на странице {url}")
            if local_errors == max_local_errors:
                return False
            else:
                print("[INFO - Yaencontre] Пробуем еще раз после 30-секундной паузы")
                time.sleep(30)

    return response


def get_links_from_site(start_url):
    links = list()
    page = 0
    check_link = str()
    check = True

    response = get_response(url=start_url)
    if response:
        bs_object = BeautifulSoup(response.content, "lxml")
        script_load_page = bs_object.find(name="script", type="application/ld+json").text
        json_object = json.loads(script_load_page)
        cards = json_object["@graph"]
        for card in cards:
            if card["@type"] == "SingleFamilyResidence":
                check_link = card["url"]
                break

        while check:
            page += 1
            url = f"{start_url}pag-{page}"
            response = get_response(url=url)
            if response:
                bs_object = BeautifulSoup(response.content, "lxml")
                script_load_page = bs_object.find(name="script", type="application/ld+json").text
                json_object = json.loads(script_load_page)
                cards = json_object["@graph"]
                for card in cards:
                    if card["@type"] == "SingleFamilyResidence":
                        link = card["url"]
                        if link == check_link and page != 1:
                            check = False
                            break
                        else:
                            links.append(link)
                print(f"[INFO - Yaencontre] Страница {url} обработана")

        return set(links)


def get_info_from_page(url, object_type, mode, seller_type, city):
    response = get_response(url=url)

    if response:
        bs_object = BeautifulSoup(response.content, "lxml")
        title = bs_object.h1.text.strip()
        price = bs_object.find(name="div", class_='price-wrapper mb-sm').text.strip()
        region = bs_object.find(name="div", class_="details-address").text.strip()
        region = record_new_region(region=region, city=city)
        characteristics = bs_object.find(name="div", class_='iconGroup info-icons')

        description = bs_object.find(name="section", id="details-description")
        if description is None:
            description = "No information"
        else:
            description = description.div.div.text.strip()

        square = characteristics.find(name="div", class_="icon-meter")
        if square is None:
            square = "No information"
        else:
            square = square.text.strip()

        bedrooms = characteristics.find(name="div", class_="icon-room")
        if bedrooms is None:
            bedrooms = "No information"
        else:
            bedrooms = bedrooms.text.strip()

        bathes = characteristics.find(name="div", class_="icon-bath")
        if bathes is None:
            bathes = "No information"
        else:
            bathes = bathes.text.strip()

        image_url = bs_object.find(name="div", class_='gallery__panel no-image-placeholder')
        if image_url is None:
            image_url = "No information"
            print(f"[INFO - Yaencontre] У объекта {title} нет фотографии")
        else:
            image_url = image_url.picture
            if image_url is None:
                image_url = "No information"
                print(f"[INFO - Yaencontre] У объекта {title} нет фотографии")
            else:
                image_url = image_url.img["src"]

        result = {"mode": mode, "title": title, "object_type": object_type, "price": price,
                  "square": square, "bedrooms": bedrooms, "bathes": bathes, "description": description,
                  "url": url, "image_url": image_url, "seller_type": seller_type, "region": region, "city": city}

        return result


def get_object_type(url):
    if "pisos" in url or "apartamentos" in url or "aticos" in url or "estudios" in url or "loft" in url:
        object_type = "Piso"
    else:
        object_type = "Casa"
    return object_type


def correct_url(url):
    if url[-1] != "/":
        url = f"{url}/"
    return url


def get_mode(url):
    if "alquiler" in url:
        mode = "rent"
    else:
        mode = "buy"
    return mode


def get_seller_type(url):
    if "particular" in url:
        seller_type = "particular"
    else:
        seller_type = "agency"
    return seller_type


def main(url=None, without_delete=False, city=None):
    if url is None:
        example = "https://www.yaencontre.com/alquiler/pisos/malaga/f-2-banos"
        text = '[INFO - Yaencontre] Выберете город и укажите фильтры поиска на сайте www.yaencontre.com.'
        input_text = f"{text}\nВставьте полученный URL ({example}):\n[INPUT - Yaencontre] >>>   "
        url = input(input_text).strip()
        city = int(input("[INPUT - Yaencontre] Введите id города: >>> "))
    url = correct_url(url=url)
    print("[INFO - Yaencontre] Программа запущена...")
    start_time = time.time()
    mode = get_mode(url=url)
    object_type = get_object_type(url=url)
    seller_type = get_seller_type(url=url)
    result = list()
    links = get_links_from_site(start_url=url)
    for link in links:
        print(f"[INFO - Yaencontre] Обрабатывается страница {link}")
        sub_result = get_info_from_page(url=link, object_type=object_type, mode=mode,
                                        seller_type=seller_type, city=city)
        if sub_result is not None:
            print(f"[INFO - Yaencontre] Получен объект: {sub_result}")
            result.append(sub_result)
    print(f"[INFO - Yaencontre] Программа собрала {len(result)} объектов")
    print("[INFO - Yaencontre] Идет запись в базу данных")
    insert_data(objects=result, without_delete=without_delete, source="yaencontre")
    stop_time = time.time()
    print(f"[INFO - Yaencontre] На работу программы потребовалось {stop_time - start_time} секунд")
    print(f"[INFO - Yaencontre] Количество ошибок сервера: {errors}")


if __name__ == "__main__":
    main()
