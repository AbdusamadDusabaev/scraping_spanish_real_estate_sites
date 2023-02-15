from scrapers.enalquiler_com import main as enalquiler
from scrapers.fotocasa_es import main as fotocasa
from scrapers.habitaclia_com import main as habitaclia
from scrapers.idealista_com import main as idealista
from scrapers.pisos_com import main as pisos
from scrapers.yaencontre_com import main as yaencontre
from scrapers.propertytop import main as propertytop
from scrapers.propextra import main as propextra
from scrapers.facebook import main as facebook
from database import record_urls_to_buy, record_urls_to_rent, delete_data, get_urls_to_rent, get_urls_to_buy


variants = ["1 - парсер сайта enalquiler.com", "2 - парсер сайта fotocasa.es",
            "3 - парсер сайта habitaclia.com", "4 - парсер сайта idealista.com",
            "5 - парсер сайта pisos.com", "6 - парсер сайта yaencontre.com", "7 - парсинг сайта propertytop",
            "8 - парсинг сайта es.propextra.com", "9 - парсинг Marketplace Facebook",
            "0 - Парсинг часто используемых url"]
parsers = {1: enalquiler, 2: fotocasa, 3: habitaclia, 4: idealista,
           5: pisos, 6: yaencontre, 7: propertytop, 8: propextra, 9: facebook}


def parsing_urls():
    for start_data in [get_urls_to_rent(), get_urls_to_buy()]:
        for element in start_data:
            url = element["url"]
            city = element["city"]
            if "https://www.pisos.com/" in url:
                print(f"[INFO - Main] Парсер сайта pisos.com обрабатывает ссылку {url}")
                parsers[5](url=url, without_delete=True, city=city)
            elif "https://www.yaencontre.com/" in url:
                print(f"[INFO - Main] Парсер сайта yaencontre.com обрабатывает ссылку {url}")
                parsers[6](url=url, without_delete=True, city=city)
            elif "https://www.habitaclia.com/" in url:
                print(f"[INFO - Main] Парсер сайта habitaclia.com обрабатывает ссылку {url}")
                parsers[3](url=url, without_delete=True, city=city)
            elif "https://www.fotocasa.es/" in url:
                print(f"[INFO - Main] Парсер сайта fotocasa.es обрабатывает ссылку {url}")
                parsers[2](url=url, without_delete=True, city=city)
            elif "https://www.enalquiler.com/" in url:
                print(f"[INFO - Main] Парсер сайта enalquiler.com обрабатывает ссылку {url}")
                parsers[1](url=url, without_delete=True, city=city)
            elif "https://www.propertytop.com/" in url:
                print(f"[INFO - Main] Парсер сайте propertytop.com обрабатывает ссылку {url}")
                parsers[7](url=url, without_delete=True, city=city)
            elif "https://es.propextra.com/" in url:
                parsers[8](url=url, without_delete=True, city=city)
            else:
                print("[INFO - Main] Ссылки на сайт idealista.com и facebook не обрабатываются")
                print(f"[ERROR - Main] Сбор данных по ссылке {url} прерван")


def main():
    while True:
        mode_text = "(Введите 1 - включить парсер, 2 - добавить url в часто встречающиеся)"
        mode = input(f"[INPUT - Main] Выберете режим работы программы {mode_text}: >>> ")

        if mode == "1":
            while True:
                without_delete = input("[INPUT - Main] Выберете режим очистки данных (1 - нет, 0 - очистить): >>> ")
                if int(without_delete) == 1 or int(without_delete) == 0:
                    break
            if int(without_delete) == 1:
                without_delete = True
            else:
                without_delete = False
            print("[INFO - Main] Выберете, какой парсер вы хотите запустить")
            print("\n".join(variants))
            while True:
                variant = input("[INPUT - Main] Введите номер парсера: >>> ")
                if variant not in "1 2 3 4 5 6 7 8 9 0":
                    print("[ERROR - Main] Вы ввели что-то не то. Попробуйте еще раз")
                elif variant == "0":
                    print("[INFO - Main] Учтите, что ссылки на сайт idealista.com и facebook обрабатываться не будут")
                    print("[INFO - Main] Если вам нужно спарсить эти, используйте парсеры напрямую")
                    go_command = input("[INPUT - Main] Начинаем парсинг по часто встречающимся? (y/n): >>> ")
                    if go_command == "y":
                        if not without_delete:
                            delete_data()
                        parsing_urls()
                else:
                    if not without_delete:
                        delete_data()
                    variant = int(variant)
                    parsers[variant](without_delete=without_delete)
                    break
            break
        elif mode == "2":
            print("[INFO - Main] Для записи url адресов в часто встречающиеся, необходимо записать их в файлы:")
            print("[INFO - Main]  urls_to_buy.txt - для часто встречающихся на продажу")
            print("[INFO - Main] urls_to_rent.txt - для часто встречающихся на аренду")
            print('[INFO - Main] Обратите внимание, что url в файлах должны быть с новой строки.', end=" ")
            print("Без каких либо разделительных знаков")
            start = input("[INPUT - Main] Начать запись url-адресов ? (y/n): >>> ")
            if start == "y":
                record_urls_to_rent()
                record_urls_to_buy()
            break
        else:
            print('[ERROR - Main] Извините, похоже вы ввели неверные данные. Попробуйте еще раз')


if __name__ == "__main__":
    main()
