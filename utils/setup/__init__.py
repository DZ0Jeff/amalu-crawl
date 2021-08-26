import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from fake_useragent import UserAgent
from utils.build import resource_path
from utils.proxy import init_proxy
from dotenv import load_dotenv


def setSelenium(root_path, console=True, proxy=False):
    # configuração do selenium
    chrome_options = Options()
    load_dotenv(os.path.join(root_path, '.env'), verbose=True)

    if not console:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument("--start-maximized")

    # Desabilitar notificações
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2
    })
    
    # adicionar idioma
    chrome_options.add_argument("--lang=pt-BR")
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'pt-BR'})

    # evitar detecção anti-bot
    chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36')
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)
    
    # desabilitar o log do chrome
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    # maximizar janela
    

    # driver paths
    # path = os.path.join(root_path, os.getenv('CHROMEDRIVER_PATH'))
    path = os.getenv('CHROMEDRIVER_PATH')
    # chrome_options.binary_location = resource_path(os.path.join(root_path, os.getenv('CHROME_LOCATION')))
    chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

    if proxy:
        PROXY = init_proxy()
        chrome_options.add_argument('--proxy-server=%s' % PROXY)

    return webdriver.Chrome(chrome_options=chrome_options, executable_path=resource_path(path), service_log_path='NUL')
