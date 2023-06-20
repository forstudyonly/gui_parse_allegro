import random
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
import os
import json
import requests
import glob
from openpyxl import Workbook

wb = Workbook()
ws = wb.active


manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""


def get_category_value(category_path, access_token):
    category_value = []
    for categoryId in category_path:
        url = f"https://api.allegro.pl/sale/categories/{categoryId}"
        headers = {
            "authorization": f"Bearer {access_token}",
            "accept": "application/vnd.allegro.public.v1+json"
        }
        response = requests.get(url=url, headers=headers)
        #print(response.text)
        json_val = json.loads(response.text)
        category_value.append(json_val["name"])
    return category_value


def edit_proxy():
    with open("assets/proxy_old.txt", "r", encoding="utf-8") as file:
        proxy_old = file.read()
    #proxies = ['arseniiy:arseniiy@185.183.160.11:8761', 'arseniiy:arseniiy@185.183.160.156:8761', 'arseniiy:arseniiy@185.183.160.160:8761', 'arseniiy:arseniiy@185.183.160.164:8761', 'arseniiy:arseniiy@185.183.160.238:8761', 'arseniiy:arseniiy@185.183.160.241:8761', 'arseniiy:arseniiy@185.183.160.254:8761', 'arseniiy:arseniiy@185.183.160.6:8761', 'arseniiy:arseniiy@185.183.160.9:8761', 'arseniiy:arseniiy@185.183.161.156:8761']
    with open("assets/proxy.txt", "r", encoding="utf-8") as file:
        proxies = file.read().strip().strip("\n")
    proxies = proxies.split("\n")
    if proxy_old:
        check = False
        proxy = 0
        for prox in proxies:
            if check:
                proxy = prox
                break
            if prox == proxy_old:
                check = True
        if proxy == 0:
            proxy = proxies[0]
    else:
        proxy = proxies[0]
    check = False

    PROXY_HOST = proxy
    PROXY_PORT = os.getenv("PORT")
    PROXY_USER = os.getenv("USER")
    PROXY_PASS = os.getenv("PASS")

    background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "http",
                    host: "%(host)s",
                    port: parseInt(%(port)d)
                  },
                  bypassList: ["foobar.com"]
                }
              };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%(user)s",
                    password: "%(pass)s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
            """ % {
        "host": PROXY_HOST,
        "port": int(PROXY_PORT),
        "user": PROXY_USER,
        "pass": PROXY_PASS,
    }
    plugin_file = "proxy_auth_plugin.zip"
    try:
        manifest_file = os.path.join(os.getcwd() + os.sep + "plugin", "manifest.json")
        with open(manifest_file, mode="w") as f:
            f.write(manifest_json)

        background_file = os.path.join(os.getcwd() + os.sep + "plugin", "background.js")
        with open(background_file, mode="w") as f:
            f.write(background_js)
    except Exception as es:
        print(es)


class Client:

    def __init__(self, access_token, dpg, headless):
        with open("assets/ua.txt", "r", encoding="utf-8") as file:
            ua = file.read().split("\n")
        self.access_token = access_token
        self.dpg = dpg
        self.headless = headless
        plugin_file = "proxy_auth_plugin.zip"
        chrome_options = uc.ChromeOptions()

        ua_new = ua[random.randint(0, len(ua) - 1)]
        chrome_options.add_argument(f'user-agent={ua_new}')

        with open("assets/chrome_location.txt", "r", encoding="utf-8") as file:
            bin_loc = file.read()
        chrome_options.binary_location = bin_loc

        if os.path.exists(plugin_file):
            chrome_options.add_argument(f"--load-extension={os.getcwd() + os.sep + 'plugin' + os.sep}")
        if self.headless:
            chrome_options.headless = True

        chrome_options.add_argument("--log-level=0")
        chrome_options.add_argument("--mute-audio")
        chrome_service = Service(ChromeDriverManager().install())
        self.driver = uc.Chrome(service=chrome_service, options=chrome_options)
        self.driver.set_page_load_timeout(40)

    def scrape(self, base_url):
        try:
            self.driver_get(url=base_url)
        except BaseException as ex:
            self.reload(url=base_url)

        time.sleep(3)
        while True:
            try:
                page_count = self.driver.find_element(By.XPATH, "//span[@class='_1h7wt mgmw_wo mh36_8 mvrt_8 _6d89c_wwgPl _6d89c_oLeFV']").text
                break
            except BaseException as ex:
                self.reload(url=base_url)
                time.sleep(3)
                continue
        folder_name = base_url.strip("/").split("/")[-1]

        while True:
            try:
                categories_a = self.driver.find_elements(By.XPATH,
                                                         "//li[@class='mpof_ki myre_zn mp4t_0 m3h2_0 mryx_0 munh_0 mg9e_2 mj7a_2 mh36_0 mvrt_0']//a")
                urls = []
                for cat in categories_a:
                    urls.append(cat.get_attribute("href"))
                categories_name = []
                for url in urls:
                    cat_name = url.strip().split("/")[-1]
                    categories_name.append(cat_name)
                    if not os.path.exists(f"data/{folder_name}/{cat_name}"):
                        os.makedirs(f"data/{folder_name}/{cat_name}")
                self.dpg.set_value("status_text", "Собрали категории")
                break
            except BaseException as ex:
                self.reload(url=base_url)
                time.sleep(3)
                continue

        print(categories_name)
        for cat in categories_name:
            try:
                self.dpg.set_value("Progress Bar", 0)
                self.dpg.set_value("status_text", f"Собираем: {cat} категорию")
                start_url = base_url + f"/{cat}"
                self.driver_get(url=start_url)
            except BaseException as ex:
                self.reload(url=start_url)
                time.sleep(3)
                continue
            while True:
                try:
                    page_count = self.driver.find_element(By.XPATH,
                                                          "//span[@class='_1h7wt mgmw_wo mh36_8 mvrt_8 _6d89c_wwgPl _6d89c_oLeFV']").text
                    break
                except BaseException as ex:
                    self.reload(url=start_url)
                    time.sleep(3)
                    continue

            count = 2
            start_page = 2
            try:
                all_exist_data = [i.replace(os.getcwd(), "").replace("/data", "") for i in
                                  glob.glob(os.getcwd() + f"/data/{folder_name}/{cat}/*.json")]
                all_exist_data = [int(i[i.find("data") + 4: i.find(".")]) for i in all_exist_data]
                start_page = max(all_exist_data) + 1 if len(all_exist_data) > 1 else 2
            except BaseException as ex:
                print(ex)
            if len(all_exist_data) == int(page_count):
                self.dpg.set_value("Progress Bar", 1)
                time.sleep(0.5)
                continue
            else:
                try:
                    id_script = self.driver.find_element(By.XPATH,
                                                         '//div[@data-prototype-id="allegro.listing"]').get_attribute(
                        "data-box-id")
                    xpath = f'//script[@data-serialize-box-id="{id_script.strip()}"]'
                    script_info2 = self.driver.find_element(By.XPATH, xpath).get_attribute("textContent")
                    with open(f"data/{folder_name}/{cat}/data0.json", "w", encoding="utf-8") as file:
                        file.write(script_info2)
                except BaseException as ex:
                    print(ex)
                self.dpg.set_value("Progress Bar", start_page / (int(page_count) + 1))
                for i in range(start_page, int(page_count) + 1):
                    try:

                        val = self.dpg.get_value("Progress Bar")
                        self.dpg.set_value("Progress Bar", val + 1 / int(page_count))
                        while True:
                            try:
                                id_script = self.driver.find_element(By.XPATH,
                                                                     '//div[@data-prototype-id="allegro.listing"]').get_attribute(
                                    "data-box-id")
                                xpath = f'//script[@data-serialize-box-id="{id_script.strip()}"]'
                                script_info2 = self.driver.find_element(By.XPATH, xpath).get_attribute("textContent")

                                if not os.path.exists(f"data/{folder_name}"):
                                    os.makedirs(f"data/{folder_name}")
                                with open(f"data/{folder_name}/{cat}/data{i - 1}.json", "w", encoding="utf-8") as file:
                                    file.write(script_info2)

                            except BaseException as ex:
                                # print(f"Не можем получить script - релоадим и пробуем заново")
                                if i > 2:
                                    self.reload(url=f'{start_url}?p={i - 1}')
                                else:
                                    self.reload(url=f'{start_url}?p={i}')
                                time.sleep(2)
                                continue
                            # print(f"Сохранили {i - 1} страниц(у)")
                            while True:
                                try:
                                    self.refresh_cookie()

                                    self.driver_get(url=f'{start_url}?p={i}')
                                    time.sleep(1)
                                    break
                                except BaseException as ex:
                                    self.reload(url=f'{start_url}?p={i}')
                                    continue
                            break
                    except BaseException as ex:
                        if i > 2:
                            self.reload(url=f'{start_url}?p={i - 1}')
                        else:
                            self.reload(url=f'{start_url}?p={i}')
                        continue


    def driver_get(self, url):
        self.driver.get(url)

    def refresh_cookie(self):
        self.driver.delete_all_cookies()

    def reload(self, url):
        self.close()
        edit_proxy()
        self.__init__(self.access_token, self.dpg, self.headless)
        self.driver.get(url)

    def close(self):
        self.driver.close()
        self.driver.quit()


def start_parse(url, access_token, dpg, headless):
    while True:
        try:
            dpg.set_value("status_text", "Начали работу...")
            parse = Client(access_token, dpg, headless)
            url = url.replace("/sklep", "")
            parse.scrape(base_url=url)
            try:
                parse.close()
            except BaseException as ex:
                pass
            finally:
                break
        except BaseException as ex:
            # print(f"{ex}\nПерешли в самый старт")
            try:
                parse.close()
            except BaseException as ex:
                pass
            continue
    dpg.set_value("status_text", "Готово!")
