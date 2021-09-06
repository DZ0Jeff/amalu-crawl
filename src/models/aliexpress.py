from utils.parser_handler import init_parser
from utils.file_handler import dataToExcel
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page, smooth_scroll
from src.utils import convert_price

from time import sleep

from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def crawl_aliexpress(url, root_path, nameOfFile):


    def click_on_list(navlist, location, driver):
        try:
            print('Clicando...')
            target = navlist[location]
            sleep(3)
            target.click()

        except ElementClickInterceptedException:
            print('clicando 2 vez...')
            driver.execute_script("arguments[0].click();", WebDriverWait(navlist[location], 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.tab-inner-text"))))


    driver = setSelenium(root_path, False)
    driver.execute_cdp_cmd("Page.setGeolocationOverride", {"latitude": -23.5660791, "longitude": -46.652984, "accuracy": 100 })
    driver.get(url)
    try:
        print('> iniciando...')
        # select_region(driver)
        
        smooth_scroll(driver) 
        print('> selecionando ficha tecníca...')
        sleep(3)

        # select details
        navcontainer = driver.find_elements_by_css_selector('.detail-tab-bar')
        navbar = navcontainer[-1]
        navlist = navbar.find_elements_by_tag_name('li')
        click_on_list(navlist, 2, driver)
        sleep(3)
        tecnical_content = driver.find_element_by_css_selector('.product-specs-list.util-clearfix').text
        
        # return to description
        click_on_list(navlist, 0, driver)
        
        print('> procurando descrição...')
        smooth_scroll(driver)   
        src_code = dynamic_page(driver)
        driver.quit()
    
    except Exception as error:
        driver.quit()
        print(f'Elemento não achado {error}')
        raise


    print('> Extraíndo resultados...')
    soap = init_parser(src_code)

    product = {}

    # category
    category = url.split('/')[2].split('.')[1]

    # Sku
    try:
        sku = url.split('/')[-1].split('.')[0]
    
    except Exception as error:
        return f"Sku não localizada!, erro: {error} \ncontate o administrador!"

    # name
    try:
        title = soap.find('h1').get_text()
    
    except AttributeError:
        return "Erro ao extrair, contate o administrador!"

    #  price
    try:
        price = str(soap.find('div', class_="product-price-original").get_text())
        if price.find('-') != -1:
            price = price.split('-')[0].strip()

        promotiona_price = str(soap.find('div', class_="product-price-current").get_text())
        if promotiona_price.find('-') != -1:
            promotiona_price = promotiona_price.split('-')[0].strip()
    
    except AttributeError:
        try:
            price = str(soap.find('span', class_="product-price-value").get_text())
            if price.find('-') != -1:
                price = price.split('-')[0].strip()
            
            promotiona_price = ""

        except Exception:
            # Banner
            try:
                price = str(soap.find('span', class_='uniform-banner-box-price').get_text())
                if price.find('-') != -1:
                    price = price.split('-')[0].strip()
                
                promotiona_price = str(soap.find('span', class_="uniform-banner-box-discounts").get_text())
                if promotiona_price.find('-') != -1:
                    promotiona_price = promotiona_price.split('-')[0].strip()

            except AttributeError:
                price = ""
                promotiona_price = ''

    # descryption
    descryption = ""
    try:
        try:
            soap.find('div', class_='detailmodule_dynamic').decompose()
        except Exception:
            print('Falha ao deletar elemento....')
            pass

        descryption = soap.select_one('div#product-description').get_text(separator="\n")
    
    except Exception:
        descryption = ""
    
    # galery
    try:
        imagelist = soap.find('ul', class_="images-view-list")
        img_src = []
        for img in imagelist.find_all('img'):
            img_src.append(img['src'].replace("_50x50", "_Q90"))

    except Exception:
        img_src = []
    

    product['Tipo'] = ["external"]
    product["Categorias"] = [category]
    product["Sku"] = [sku]
    product["Nome"] = [title]

    decimal_price = convert_price(price)
    decimal_promotional_price = convert_price(promotiona_price)

    print('Preço: ', decimal_price)
    print('Preço promocional: ', decimal_promotional_price)

    if price == '' or decimal_promotional_price > decimal_price:
        print('> invertendo os preços')
        product["Preço promocional"] = [price] 
        product["Preço"] = [promotiona_price]
    else:
        print('> Preços originais')
        product["Preço promocional"] = [promotiona_price]
        product["Preço"] = [price]
    product['Texto do botão'] = ["Ver produto"]
    product["Url externa"] = [url]
    product["Descrição curta"] = [tecnical_content]
    product["Descrição"] = [descryption]
    product["Images"] = [", ".join(img_src)]
    
    # print('Price: ', product['Preço'])
    # print('Promotional price: ', product['Preço promocional'])

    print('> Salvando em arquivo...')
    # print(price)
    # print(promotiona_price)
    # [print(f"{index}: \t{content}") for index, content in product.items()]
    dataToExcel(product, nameOfFile)
    print(f'> Arquivo {nameOfFile} salvo com sucesso!')
    return nameOfFile
