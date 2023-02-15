import pymysql
from pymysql import cursors
from config import user, password, port, host, db_name
from config import table_objects_to_buy, table_objects_to_rent, table_urls_to_rent, table_urls_to_buy, table_regions
from config import table_objects_facebook, table_cities


# correct data section =================================================================================================

def correct_number(number):
    result = list()
    if number is None:
        return 0
    if len(number) > 0:
        for symbol in number:
            if symbol.isdigit():
                result.append(symbol)
        if len(result) > 0:
            result = int(("".join(result)).replace("²", ""))
        else:
            result = 0
        return result
    else:
        return 0


def correct_seller_type(seller_type):
    if seller_type == "particular":
        return 1
    else:
        return 0


def correct_object_type(object_type):
    if object_type == "Piso":
        return 1
    else:
        return 0


def correct_text(text):
    text = text.replace('"', "'")
    return f'"{text}"'


# get data section =====================================================================================================
def get_object_type(url):
    if "https://www.yaencontre.com/" in url:
        if "pisos" in url or "apartamentos" in url or "aticos" in url or "estudios" in url or "loft" in url:
            return 1
        else:
            return 0
    elif "https://www.pisos.com/" in url:
        if "piso-" in url or "aticos-" in url or "estudios-" in url or "lofts-" in url:
            return 1
        else:
            return 0
    elif "https://www.idealista.com/" in url:
        if "pisos" in url or "aticos" in url or "lofts" in url:
            return 1
        else:
            return 0
    elif "https://www.habitaclia.com/" in url:
        if "pisos" in url or "aticos" in url:
            return 1
        else:
            return 0
    elif "https://www.fotocasa.es/" in url:
        if ("apartamentos" in url or "estudios" in url or "propertySubtypeIds=2" in url or "propertySubtypeIds=6" in url
                or "propertySubtypeIds=54" in url or "aticos" in url or "lofts" in url or "propertySubtypeIds=8"):
            return 1
        else:
            return 0
    elif "https://www.enalquiler.com/" in url:
        if "tipo=2" in url or "tipo=6" in url or "tipo=3" in url or "tipo=5" in url:
            return 1
        else:
            return 0
    elif "https://www.propertytop.com/" in url:
        if "apartment" in url or "penthouse" in url:
            return 1
        else:
            return 0
    else:
        return "NULL"


def get_seller_type(url):
    if "https://www.yaencontre.com/" in url:
        if "particular" in url:
            return 1
        else:
            return 0
    elif "https://www.enalquiler.com/" in url:
        return 1
    elif "https://es.propextra.com/" in url or "https://www.propertytop.com/" in url:
        return 0
    else:
        return "NULL"


def get_urls_to_buy():
    query = f"""SELECT * FROM {table_urls_to_buy} WHERE active = 1;"""
    result = database(query=query)
    return result


def get_urls_to_rent():
    query = f"""SELECT * FROM {table_urls_to_rent} WHERE active = 1;"""
    result = database(query=query)
    return result


# connect to database section ==========================================================================================
def database(query, object_name=None):
    try:
        connection = pymysql.connect(port=port, host=host, user=user, password=password,
                                     database=db_name, cursorclass=cursors.DictCursor)
        try:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result
        except Exception as ex:
            if "Duplicate entry" in str(ex):
                print(f"[INFO - Database] Объект {object_name} дублируется в базе данных, поэтому он не будет записан")
            else:
                print(f"[ERROR - Database] {ex}")
            return "Error"
        finally:
            connection.close()
    except Exception as ex:
        print(f"[ERROR - Database] Connection was not completed because {ex}")
        return "Error"


# create table section =================================================================================================
def create_table_regions():
    query = f"""CREATE TABLE {table_regions.lower()} 
                (`region_id` INT UNIQUE AUTO_INCREMENT, `title` VARCHAR(200), `city` INT);"""
    result = database(query=query)
    if result != "Error":
        print("[INFO - Database] Таблица регионов успешно создана")


def create_table_cities():
    query = f"""CREATE TABLE {table_cities.lower()} (`city_id` INT UNIQUE AUTO_INCREMENT, `title` VARCHAR(50));"""
    result = database(query=query)
    if result != "Error":
        print("[INFO - Database] Таблица городов успешно создана")


def create_table_objects_to_buy():
    query = f"""CREATE TABLE {table_objects_to_buy.lower()} (favorite INT, 
    seller_type INT, title VARCHAR(500), object_type INT, price VARCHAR(50), square VARCHAR(50), 
    bedrooms VARCHAR(50), bathes VARCHAR(50), description TEXT, url VARCHAR(500) UNIQUE, 
    image_url VARCHAR(500), region INT, city INT, source VARCHAR(50));"""
    result = database(query=query)
    if result != "Error":
        print('[INFO - Database] Таблица объектов недвижимости на продажу успешно создана')


def create_table_objects_to_rent():
    query = f"""CREATE TABLE {table_objects_to_rent.lower()} (favorite INT, 
    seller_type INT, title VARCHAR(500), object_type INT, price VARCHAR(50), square VARCHAR(50), 
    bedrooms VARCHAR(50), bathes VARCHAR(50), description TEXT, url VARCHAR(500) UNIQUE, 
    image_url VARCHAR(500), region INT, city INT, source VARCHAR(50));"""
    result = database(query=query)
    if result != "Error":
        print('[INFO - Database] Таблица объектов недвижимости в аренду успешно создана')


def create_table_urls_to_buy():
    query = f"""CREATE TABLE {table_urls_to_buy.lower()} 
                (url VARCHAR(500) UNIQUE, seller_type INT, object_type INT, active INT, city INT);"""
    result = database(query=query)
    if result != "Error":
        print("[INFO - Database] Таблица часто встречающихся url-адресов на продажу успешно создана")


def create_table_urls_to_rent():
    query = f"""CREATE TABLE {table_urls_to_rent.lower()} 
                (url VARCHAR(500) UNIQUE, seller_type INT, object_type INT, active INT, city INT);"""
    result = database(query=query)
    if result != "Error":
        print("[INFO - Database] Таблица часто встречающихся url-адресов на аренду успешно создана")


def create_table_facebook():
    query = f"""CREATE TABLE {table_objects_facebook.lower()} (favorite INT, title VARCHAR(500), 
    price VARCHAR(50), bedrooms VARCHAR(50), bathes VARCHAR(50), 
    description TEXT, url VARCHAR(750) UNIQUE, image_url VARCHAR(750), region INT, city INT, mode VARCHAR(50));"""
    result = database(query=query)
    if result != "Error":
        print('[INFO - Database] Таблица объектов недвижимости на Facebook Marketplace успешно создана')


# delete data section ==================================================================================================
def delete_data():
    query = f"""DELETE FROM {table_objects_to_buy.lower()} WHERE favorite = 0;"""
    database(query=query)
    query = f"""DELETE FROM {table_objects_to_rent.lower()} WHERE favorite = 0;"""
    database(query=query)
    print("[INFO - Database] Таблица объектов на продажу и таблица объектов на аренду успешно очищены")


def delete_facebook_data():
    query = f"""DELETE FROM {table_objects_facebook.lower()} WHERE favorite = 0;"""
    database(query=query)
    print("[INFO - Database] Таблица объектов с Facebook Marketplace успешно очищена")


# record data section ==================================================================================================
def record_new_region(region, city):
    region = region.lower()
    query = f"SELECT * FROM {table_regions.lower()};"
    result = database(query=query)
    for element in result:
        if region == element["title"]:
            return element["region_id"]
    query = f"""INSERT INTO {table_regions.lower()} (`title`, `city`) VALUES ("{region}", {city});"""
    database(query=query)
    query = f"""SELECT * FROM {table_regions.lower()} WHERE `title` = "{region}";"""
    result = database(query=query)
    return result[0]["region_id"]


def add_city(city):
    query = f"""SELECT * FROM {table_cities.lower()};"""
    result = database(query=query)
    for element in result:
        if element["title"].lower() == city.lower():
            print(f"[INFO - Database] Такой город уже есть в базе данных. Его id = {element['city_id']}")
            return False
    query = f"INSERT INTO {table_cities.lower()} (`title`) VALUES ('{city}');"
    database(query=query)
    query = f"SELECT * FROM {table_cities.lower()} WHERE `title` = '{city}';"
    result = database(query=query)
    city_id = result[0]["city_id"]
    print(f"[INFO - Database] Город успешно добавлен в таблицу. Его id = {city_id}")


def record_urls_to_buy():
    with open("urls_to_buy.txt", "r", encoding="utf-8") as file:
        urls_text = file.read()
    url_objects = urls_text.split("\n")
    for url_object in url_objects:
        if len(url_object) > 0:
            url = url_object.split("|")[0].strip()
            city = int(url_object.split("|")[1])
            print(f"[INFO - Database] Добавляем {url} в базу данных часто встречающихся url на продажу")
            url = correct_text(text=url)
            seller_type = get_seller_type(url=url)
            object_type = get_object_type(url=url)
            active = 1
            query = f"""INSERT INTO {table_urls_to_buy.lower()}(url, seller_type, object_type, active, city)
                        VALUES({url}, {seller_type}, {object_type}, {active}, {city});"""
            database(query=query, object_name=url)
    print("[INFO - Database] Запись url-адресов на продажу успешно завершена")


def record_urls_to_rent():
    with open("urls_to_rent.txt", "r", encoding="utf-8") as file:
        urls_text = file.read()
    url_objects = urls_text.split("\n")
    for url_object in url_objects:
        if len(url_object) > 0:
            url = url_object.split("|")[0].strip()
            city = url_object.split("|")[1]
            print(f"[INFO - Database] Добавляем {url} в базу данных часто встречающихся url на аренду")
            url = correct_text(text=url)
            seller_type = get_seller_type(url=url)
            object_type = get_object_type(url=url)
            active = 1
            query = f"""INSERT INTO {table_urls_to_rent.lower()}(url, seller_type, object_type, active, city)
                        VALUES({url}, {seller_type}, {object_type}, {active}, {city});"""
            database(query=query, object_name=url)
    print("[INFO - Database] Запись url-адресов на аренду успешно завершена")


def insert_data(objects, without_delete, source):
    if not without_delete:
        delete_data()
    for object_dict in objects:
        mode = object_dict["mode"]
        seller_type = correct_seller_type(seller_type=object_dict["seller_type"])
        title = correct_text(text=object_dict["title"])
        object_type = correct_object_type(object_type=object_dict["object_type"])
        price = correct_number(number=object_dict["price"])
        square = correct_number(number=object_dict["square"])
        bedrooms = correct_number(number=object_dict["bedrooms"])
        bathes = correct_number(number=object_dict["bathes"])
        description = correct_text(text=object_dict["description"])
        url = correct_text(text=object_dict["url"])
        image_url = correct_text(text=object_dict["image_url"])
        region = object_dict["region"]
        city = object_dict["city"]
        if mode == "buy":
            table = table_objects_to_buy
        else:
            table = table_objects_to_rent
        query = f"""INSERT INTO {table.lower()}(favorite, seller_type, title, object_type, 
                                                price, square, bedrooms, bathes, description, url, 
                                                image_url, region, city, source)
                    VALUES (0, {seller_type}, {title}, {object_type}, {price}, {square}, 
                            {bedrooms}, {bathes}, {description}, {url}, {image_url}, '{region}', {city}, '{source}');"""
        database(query=query, object_name=object_dict["title"])


def insert_facebook_data(objects, without_delete):
    if not without_delete:
        delete_facebook_data()
    for object_dict in objects:
        mode = object_dict["mode"]
        title = correct_text(text=object_dict["title"])
        price = correct_number(number=object_dict["price"])
        bedrooms = correct_number(number=object_dict["bedrooms"])
        bathes = correct_number(number=object_dict["bathrooms"])
        description = correct_text(text=object_dict["description"])
        url = correct_text(text=object_dict["object_url"])
        image_url = correct_text(text=object_dict["main_image"])
        region = object_dict["region"]
        city = object_dict["city"]
        query = f"""INSERT INTO {table_objects_facebook.lower()}(favorite, title, 
                                                price, bedrooms, bathes, description, url, 
                                                image_url, region, city, mode)
                    VALUES (0, {title}, {price}, {bedrooms}, {bathes}, {description}, {url}, 
                           {image_url}, '{region}', {city}, '{mode}');"""
        database(query=query, object_name=object_dict["title"])


# run section ==========================================================================================================
if __name__ == "__main__":
    run_mode = input("[INPUT - Database] Выберете режим работы (1 - создать таблицы, 2 - добавить город): >>> ")
    if run_mode == "1":
        create_table_objects_to_buy()
        create_table_objects_to_rent()
        create_table_facebook()
        create_table_urls_to_buy()
        create_table_urls_to_rent()
        create_table_regions()
        create_table_cities()
    elif run_mode == "2":
        print("[INFO - Database] Чтобы завершить ввод городов, введите END")
        while True:
            city_name = input("[INPUT - Database] Введите название города: >>> ")
            if city_name.lower() == "end":
                break
            add_city(city=city_name)
