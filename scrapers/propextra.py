import requests
from bs4 import BeautifulSoup
import time
from database import insert_data, record_new_region


ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
headers = {"user-agent": ua}
domain = "https://es.propextra.com/"


def get_object_type(title):
    title = title.lower()
    if "apartment" in title or "penthouse" in title or "studio" in title:
        return "Piso"
    return "Casa"


def get_object_links(url):
    print(f"[INFO - Parser PropExtra] Запущен сбор ссылок объектов по url = {url}")
    result = list()
    page = 0
    while True:
        page += 1
        print(f"[INFO - Parser PropExtra] Собираем ссылки на объекты со страницы {page}")
        current_url = f"{url}page={page}"
        response = requests.get(url=current_url, headers=headers)
        bs_object = BeautifulSoup(response.content, "lxml")
        check_url = bs_object.find(name="h3", class_="property-title").a["href"]
        if check_url in result:
            break
        else:
            current_object_list = [card.a["href"] for card in bs_object.find_all(name="h3", class_="property-title")]
            result.extend(current_object_list)
    print(f"[INFO - Parser PropExtra] Сбор ссылок на объекты по url = {url} завершен")
    return result


def get_object_info(object_url, city):
    print(f"[INFO - Parser PropExtra] Собираем информацию об объекте {object_url}")
    response = requests.get(url=object_url, headers=headers)
    bs_object = BeautifulSoup(response.content, "lxml")
    check = "This property is no longer available" in bs_object.text
    if check:
        print(f"[INFO - Parser PropExtra] Объект {object_url} больше недоступен. Продолжаем парсинг...")
        return "Not Available"
    title = bs_object.h1
    if title is None:
        return "Not Available"
    title = title.span.text.strip()
    object_type = get_object_type(title=title)
    price = bs_object.find(name="span", class_="property-price").text.strip()
    bedrooms = bs_object.find(name="span", itemprop="numberOfRooms")
    if bedrooms is not None:
        bedrooms = bedrooms.text.strip()
    else:
        bedrooms = "0"
    bathrooms = bs_object.find(name="span", class_="property-baths")
    if bathrooms is not None:
        bathrooms = bathrooms.text.strip()
    else:
        bathrooms = "0"
    description = bs_object.find(name="div", class_='description').text.replace("Show More", "").strip()
    square = bs_object.find(name="div", class_="col-sm-4 col-xs-6").find(name="span", class_="value").text.strip()
    image_url = bs_object.find(name="div", class_="item-picture").img
    if "src" in list(image_url.attrs):
        image_url = image_url["src"]
    else:
        image_url = image_url["src2"]
    region = bs_object.find(name="meta", itemprop="address")["content"]
    region = record_new_region(region=region, city=city)
    return {"mode": "buy", "title": title, "object_type": object_type, "price": price,
            "square": square, "bedrooms": bedrooms, "bathes": bathrooms, "description": description,
            "url": object_url, "image_url": image_url, "seller_type": "agency", "region": region, "city": city}


def main(url=None, without_delete=False, city=None):
    result = list()
    if url is None:
        url = input("[INPUT - Parser PropExtra] Введите url для анализа на сайте https://es.propextra.com/: >>> ")
        city = int(input("[INPUT - Parser PropExtra] Введите id города: >>> "))
    print("[INFO - Parser PropertyTop] Парсер propextra запущен")
    links = get_object_links(url=url)
    for link in links:
        start_time = time.time()
        try:
            object_info = get_object_info(object_url=link, city=city)
            if object_info != "Not Available":
                result.append(object_info)
        except Exception as ex:
            print(f"[ERROR - Parser PropExtra] Ошибка при сборе данных об объекте {link}")
            print(f"[ERROR - Parser PropExtra] {ex}")
        stop_time = time.time()
        print(f"[INFO - Parser PropExtra] На обработку объекта {link} ушло {stop_time - start_time} секунд")
    print(f"[INFO - Parser PropExtra] Парсер собрал {len(links)} объектов. Идет запись объектов в базу данных...")
    insert_data(objects=result, without_delete=without_delete, source="propextra")
    print("[INFO - Parser PropExtra] Запись объектов успешно завершена")


if __name__ == "__main__":
    main()
