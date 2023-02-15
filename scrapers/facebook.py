import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import facebook_login, facebook_password
from database import insert_facebook_data, record_new_region


ua_chrome = " ".join(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                      "AppleWebKit/537.36 (KHTML, like Gecko)",
                      "Chrome/108.0.0.0 Safari/537.36"])
headers = {"user-agent": ua_chrome}
domain = "https://www.facebook.com"

options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={ua_chrome}")
options.add_argument("--disable-notifications")
# options.add_argument("--headless")


def get_mode(url):
    if "propertyforsale" in url:
        return "buy"
    return "rent"


def get_price(bs_object):
    price = bs_object.find(name="div", class_="x1anpbxc")
    if price is not None:
        price = price.text.strip()
    else:
        price = bs_object.find(name="div", class_="x1xmf6yo")
        if price is not None:
            price = price.text.strip()
        else:
            price = "Not Found"
    return price


def get_bedrooms_and_bathrooms(bs_object):
    try:
        characteristics = bs_object.find_all(name="div", class_="xu06os2 x1ok221b")
        bedrooms_and_bathrooms = str()
        for element in characteristics:
            if "спальня" in element.text or "санузел" in element.text:
                bedrooms_and_bathrooms = element.text.strip()
                break
        bedrooms_and_bathrooms_list = bedrooms_and_bathrooms.split("·")
        bedrooms = "Not Found"
        bathrooms = "Not Found"
        for element in bedrooms_and_bathrooms_list:
            if "спальня" in element:
                bedrooms = element.strip()
            elif "санузел" in element:
                bathrooms = element.strip()
        return {"bedrooms": bedrooms, "bathrooms": bathrooms}
    except Exception as ex:
        return {"bedrooms": "Not Found", "bathrooms": "Not Found"}


def authorization(browser):
    print("[INFO] Авторизуемся в системе...")
    browser.get(url="https://www.facebook.com/")
    login_input = browser.find_element(By.ID, "email")
    login_input.send_keys(facebook_login)
    password_input = browser.find_element(By.ID, "pass")
    password_input.send_keys(facebook_password)
    login_button = browser.find_element(By.TAG_NAME, "button")
    login_button.click()
    time.sleep(5)


def get_object_links(browser, url):
    print("[INFO] Собираем ссылки на объекты...")
    browser.get(url=url)
    old_bs_object = BeautifulSoup(browser.page_source, "lxml")
    index = 0
    while True:
        index += 1
        print(f"[INFO - Facebook] Ссылки со страницы {index} страницы успешно собраны")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        current_bs_object = BeautifulSoup(browser.page_source, "lxml")
        if current_bs_object == old_bs_object:
            break
        old_bs_object = current_bs_object
    bs_object = BeautifulSoup(browser.page_source, "lxml")
    product_link_objects = bs_object.find_all(name="div", class_="x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e xnpuxes x291uyu x1uepa24 x1iorvi4 xjkvuk6")
    product_links = list()
    for product_link_object in product_link_objects:
        if product_link_object.a is not None:
            product_link = domain + product_link_object.a["href"]
            product_links.append(product_link)
    return product_links


def get_object_info(browser, object_url, mode, region, city):
    print(f"[INFO] Обрабатываем объект {object_url}")
    browser.get(object_url)
    try:
        full_description = browser.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div[8]/div[2]/div/div/div/span/div")
        browser.execute_script("arguments[0].click();", full_description)
        time.sleep(1)
    except Exception as ex:
        pass
    bs_object = BeautifulSoup(browser.page_source, "lxml").find(name="div", attrs={"data-pagelet": "MainFeed"})
    try:
        title = bs_object.find(name="h1", class_="x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x193iq5w xeuugli").text.strip()
    except Exception as ex:
        title = "Not Found"
    price = get_price(bs_object=bs_object)
    try:
        description = bs_object.find(name="div", class_="xod5an3").find(name="span", class_="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u").text.strip()
    except Exception as ex:
        description = "Not Found"
    bedrooms_and_bathrooms = get_bedrooms_and_bathrooms(bs_object=bs_object)
    bedrooms = bedrooms_and_bathrooms["bedrooms"]
    bathrooms = bedrooms_and_bathrooms["bathrooms"]
    try:
        images = [image.img["src"] for image in bs_object.find_all(name="div", class_="xhk9q7s x1otrzb0 x1i1ezom x1o6z2jb x1rg5ohu x2lah0s x6ikm8r x10wlt62 xc9qbxq x14qfxbe x1mnrxsn x1w0mnb")]
        main_image = images[0]
    except Exception as ex:
        main_image = "Not Found"
    result = {"title": title, "price": price, "bedrooms": bedrooms,
              "bathrooms": bathrooms, "mode": mode, "object_url": object_url,
              "main_image": main_image, "description": description, "region": region, "city": city}
    print(result)
    return result


def main(without_delete=False):
    result = list()
    url = input("[INPUT - Facebook] Введите url категории на Marketplace Facebook: >>> ")
    city = int(input("[INPUT - Facebook] Введите id города: >>> "))
    region = input("[INPUT - Facebook] Введите регион (локацию): >>> ")
    region = record_new_region(region=region, city=city)
    mode = get_mode(url=url)
    browser = webdriver.Chrome(options=options)
    try:
        authorization(browser=browser)
        print("[INFO] Авторизация успешно завершена")
        object_links = get_object_links(browser=browser, url=url)
        for object_link in object_links:
            try:
                sub_result = get_object_info(browser=browser, object_url=object_link,
                                             mode=mode, region=region, city=city)
                result.append(sub_result)
            except Exception as ex:
                continue
        insert_facebook_data(objects=result, without_delete=without_delete)
    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    main()
