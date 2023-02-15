import requests
from bs4 import BeautifulSoup
from database import record_new_region, insert_data
import time


ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
headers = {"user-agent": ua}
domain = "https://www.propertytop.com"


def get_object_type(title):
    title = title.lower()
    if "apartment" in title or "penthouse" in title:
        return "Piso"
    return "Casa"


def get_characteristics(characteristic_lists):
    characteristics = list()
    for characteristic_list in characteristic_lists:
        characteristic_list = characteristic_list.find_all(name="li")
        for characteristic in characteristic_list:
            characteristics.append(characteristic.text.strip())
    return characteristics


def get_amount_bedrooms(characteristics):
    for characteristic in characteristics:
        if "Bedrooms" in characteristic:
            return characteristic.replace("Bedrooms", "").strip()


def get_amount_bathrooms(characteristics):
    for characteristic in characteristics:
        if "Bathrooms" in characteristic:
            return characteristic.replace("Bathrooms", "").strip()


def get_square(characteristics):
    for characteristic in characteristics:
        if "m²" in characteristic:
            return characteristic.replace("Built", "").replace("Plot", "").strip()


def get_object_links(url):
    print()
    object_links = list()
    page = 0
    while True:
        page += 1
        print(f"[INFO - Parser PropertyTop] Собираем ссылки на объекты со страницы {page}")
        if "?" in url:
            if url[-1] == "?":
                current_url = f"{url}ipage={page}"
            elif url[-1] == "=":
                current_url = f"{url}&ipage={page}"
            else:
                current_url = f"{url}&ipage={page}"
        else:
            current_url = f"{url}?ipage={page}"
        response = requests.get(url=current_url, headers=headers)
        bs_object = BeautifulSoup(response.content, "lxml")
        if "No properties have been found according to your search criteria." in bs_object.text:
            break
        current_links = [domain + card.a["href"] for card in bs_object.find_all(name="div", class_="col mb-3 mb-sm-0")]
        object_links.extend(current_links)
    print("[INFO - Parser PropertyTop] Сбор ссылок закончен")
    return object_links


def get_object_info(object_url, city):
    print(f"[INFO - Parser PropertyTop] Обрабатываем объект {object_url}")
    response = requests.get(url=object_url, headers=headers)
    bs_object = BeautifulSoup(response.content, "lxml")
    title = bs_object.find(name="h1").text.strip()
    object_type = get_object_type(title=title)
    price = bs_object.find(name="strong", class_="h4 d-block fw-semibold mb-0").text.strip()
    region = bs_object.find(name="div", class_="col-md-9 col-lg-8 col-xl-9").p.text.strip()
    region = record_new_region(region=region, city=city)
    image_url = bs_object.find(name="img", class_="image-fit")["src"]
    description = bs_object.find(name="div", id="collapseDesc").p.text.strip()
    characteristics = get_characteristics(characteristic_lists=bs_object.find_all(name="ul", class_='row-cols-md-2'))
    bedrooms = get_amount_bedrooms(characteristics=characteristics)
    bathrooms = get_amount_bathrooms(characteristics=characteristics)
    square = get_square(characteristics=characteristics)
    return {"mode": "buy", "title": title, "object_type": object_type, "price": price,
            "square": square, "bedrooms": bedrooms, "bathes": bathrooms, "description": description,
            "url": object_url, "image_url": image_url, "seller_type": "agency", "region": region, "city": city}


def main(url=None, without_delete=False, city=None):
    result = list()
    if url is None:
        url = input("[INPUT - Parser PropertyTop] Введите url для анализа на сайте https://www.propertytop.com/: >>> ")
        city = int(input("[INPUT - Parser PropertyTop] Введите id города: >>> "))
    print("[INFO - Parser PropertyTop] Парсер propertytop запущен")
    links = get_object_links(url=url)
    for link in links:
        start_time = time.time()
        try:
            object_info = get_object_info(object_url=link, city=city)
            result.append(object_info)
        except Exception as ex:
            try:
                print("[INFO - PropertyTop] Сервер выдал ошибку. Ждем 30 секунд и пробуем снова...")
                time.sleep(30)
                object_info = get_object_info(object_url=link, city=city)
                result.append(object_info)
            except Exception as ex:
                print(f"[INFO - PropertyTop] Не удалось собрать данные об объекте {link}")
        stop_time = time.time()
        print(f"[INFO - Parser PropertyTop] На обработку объекта {link} ушло {stop_time - start_time} секунд")
    print(f"[INFO - Parser PropertyTop] Парсер собрал {len(links)} объектов. Идет запись объектов в базу данных...")
    insert_data(objects=result, without_delete=without_delete, source="propertytop")
    print("[INFO - Parser PropertyTop] Запись объектов успешно завершена")


if __name__ == "__main__":
    main()
