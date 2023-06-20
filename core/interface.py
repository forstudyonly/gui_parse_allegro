import dearpygui.dearpygui as dpg
import core.check_api.tests
from core.parser.parser import start_parse
from core.parser.parser_api import start_api_parse
import time
import threading
from selenium import webdriver
import json
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
import callback

code_verifier = ""


def start_interface(token_file_path):
    # Коллбэк функция для кнопки
    def check_token():
        with open(token_file_path, "r", encoding="utf-8") as file:
            access_token = file.read()
        res = core.check_api.tests.check_token(access_token)
        if res == 200:
            dpg.set_value("Output Text", "Токен рабочий!")

        elif res == 401:
            dpg.set_value("Output Text", "Токен устарел, нужно обновить!")
        else:
            dpg.set_value("Output Text", "Неизвестная ошибка")

    def link_token():
        global code_verifier
        dpg.set_value("Output Text", "Обновляем токен...")
        link_val, code_verifier = core.check_api.tests.get_link()

        firefox_service = Service(GeckoDriverManager().install())
        try:
            options = webdriver.FirefoxOptions()
            options.add_argument("--log-level=0")
            options.add_argument("--mute-audio")
            options.add_argument('no-sandbox')
            options.add_argument('--headless')
            with open("firefox_location.txt", "r", encoding="utf-8") as file:
                bin_loc_firefox = file.read()
            options.binary_location = bin_loc_firefox
            try:
                with webdriver.Firefox(service=firefox_service, options=options) as driver:
                    driver.set_page_load_timeout(10)
                    driver.get("https://allegro.pl")
                    with open("assets/cookies.txt", "r", encoding="utf-8") as file:
                        cookies = json.loads(file.read())
                    for cook in cookies:
                        if cook.get("sameSite", False):
                            del cook["sameSite"]
                        driver.add_cookie(cook)
                    driver.get(link_val)
                    time.sleep(2)
                    driver.close()
                    driver.quit()
            except:
                pass

        except Exception as ex:
            print(ex)

        time.sleep(1)
        with open("assets/code.txt", "r", encoding="utf-8") as file:
            code_from_allegro = file.read()

        response = core.check_api.tests.get_access_token(code_from_allegro, code_verifier)
        # print(response['access_token'])
        with open(token_file_path, "w", encoding="utf-8") as file:
            file.write(response['access_token'])
        with open(token_file_path, "r", encoding="utf-8") as file:
            access_token = file.read()
        res = core.check_api.tests.check_token(access_token)
        if res == 200:
            dpg.set_value("Output Text", "Токен рабочий!")

        elif res == 401:
            dpg.set_value("Output Text", "Токен устарел, нужно обновить!")
        else:
            dpg.set_value("Output Text", "Неизвестная ошибка")
        dpg.set_value("Output Text", "Успешно! Теперь проверьте токен.")

    def update_token():
        global code_verifier
        code_from_allegro = dpg.get_value("code_verif")
        response = core.check_api.tests.get_access_token(code_from_allegro, code_verifier)
        print(response['access_token'])
        with open(token_file_path, "w", encoding="utf-8") as file:
            file.write(response['access_token'])
        dpg.set_value("Output Text", "Успешно! Теперь проверьте токен.")

    def on_button_click():
        link = dpg.get_value("link")
        headless = dpg.get_value("headless_value")

        print("Input Text:", link)

        with open(token_file_path, "r", encoding="utf-8") as file:
            access_token = file.read()
        start_parse(link.strip(), access_token, dpg, headless)

        dpg.set_value("status_text", "Готово!")

    def api_parse():
        # Получаем значение link

        folder = dpg.get_value("needed_folder").strip()
        if "/sklep" in folder:
            folder = folder.replace("/sklep", "").split("/")[-1].strip()
            print(folder)

        with open(token_file_path, "r", encoding="utf-8") as file:
            access_token = file.read()

        start_api_parse(folder, dpg)

    def on_exit_button_click(sender, data):
        dpg.stop_dearpygui()

    def start_new_thread():
        thread = threading.Thread(target=on_button_click)
        thread.start()

    def start_api_parse_thread():
        thread = threading.Thread(target=api_parse)
        thread.start()

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.font_registry():
        with dpg.font(f'assets/ofont.ru_Montserrat Alternates.ttf', 18, default_font=True, id="Default font"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    dpg.bind_font("Default font")

    with dpg.window(label="Собрать страницы", width=1000, height=800):

        dpg.add_checkbox(label="Работать в фоновом режиме", default_value=False, id="headless_value")

        dpg.add_input_text(label="Введите ссылку для магазина который нужно спарсить", id="link", width=350)
        dpg.add_spacer(height=20)

        dpg.add_text(label="Output Text", id="status_text", default_value="", wrap=300)
        dpg.add_spacer(height=10)

        dpg.add_progress_bar(label="Progress Bar", default_value=0, id="Progress Bar")
        dpg.add_spacer(height=20)

        dpg.add_button(label="Начать парсинг!", callback=start_new_thread)
        dpg.add_spacer(height=20)
        dpg.add_button(label="Выход", callback=on_exit_button_click)

    with dpg.window(label="Парсинг", width=900, height=600):

        dpg.add_text(label="Output Text", id="Output Text", default_value="", wrap=300)
        dpg.add_spacer(height=10)

        dpg.add_button(label="Проверить API токен!", callback=check_token)
        dpg.add_spacer(height=10)
        dpg.add_button(label="Ссылка для обновления токена!", callback=link_token)
        dpg.add_spacer(height=10)
        dpg.add_input_text(label="Введите код для обновления токена и нажмите кнопку ниже", id="code_verif", width=300)
        dpg.add_spacer(height=10)
        dpg.add_button(label="Обновить токен!", callback=update_token)
        dpg.add_spacer(height=30)

        dpg.add_input_text(label="Введите ссылку для магазина или название, например 'the_book'", id="needed_folder",
                           width=350)
        dpg.add_spacer(height=20)

        dpg.add_text(label="Output Text", id="status_api_text", default_value="", wrap=300)
        dpg.add_spacer(height=10)

        dpg.add_progress_bar(label="Progress Bar", default_value=0, id="Progress Bar API")
        dpg.add_spacer(height=20)

        dpg.add_button(label="Начать парсинг!", callback=start_api_parse_thread)
        dpg.add_spacer(height=20)
        dpg.add_button(label="Выход", callback=on_exit_button_click)

        thread = threading.Thread(target=callback.main)
        thread.start()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
