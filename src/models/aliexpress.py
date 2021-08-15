from utils.parser_handler import init_parser
from utils.file_handler import dataToExcel
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page, scroll, smooth_scroll
from time import sleep
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def crawl_aliexpress(url, root_path, nameOfFile):


    def click_on_list(driver, location):
        try:
            navlist[location].click()
        
        except ElementClickInterceptedException:
            navlist[location].find_element_by_css_selector('tab-inner').click()


    driver = setSelenium(root_path, False)
    driver.get(url)
    print('> iniciando...')

    try:
        driver.execute_script("window.scrollTo(0, 1200);") 
        # smooth_scroll(driver)   
        print('> selecionando ficha tecníca...')
        sleep(3)

        # select details
        navbar = driver.find_elements_by_css_selector('.detail-tab-bar')[-1]
        navlist = navbar.find_elements_by_tag_name('li')
        click_on_list(driver, 2)
        tecnical_content = driver.find_element_by_css_selector('.product-specs-list.util-clearfix').text
        
        # return to description
        click_on_list(0)
        
        print('> procurando descrição...')
        smooth_scroll(driver)   
        src_code = dynamic_page(driver)
        driver.quit()
    
    except Exception:
        driver.quit()
        # print('Elemento não achado')
        # return
        raise

    print('> Extraíndo resultados...')
    soap = init_parser(src_code)

    product = {}

    # category
    category = url.split('/')[2].split('.')[1]

    # sku
    try:
        sku = url.split('sku_id')[-1].split('%22')[2]
    except Exception:
        return "Sku não localizada!, contate o administrador!"

    # name
    try:
        title = soap.find('h1').get_text()
    
    except AttributeError:
        return "Erro ao extrair, contate o administrador!"

    #  name
    try:
        price = soap.find('span', class_="product-price-value").get_text()
        price = price.split('-')[0]
    
    except Exception:
        price = ""

    # descryption
    descryption = ""
    try:
        descryption = soap.select_one('div#product-description').get_text() 
    
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
    product["Categoria"] = [category]
    product["Sku"] = [sku]
    product["Nome"] = [title]
    product["Preço"] = [price]
    product['Texto do botão'] = ["Ver produto"]
    product["Url externa"] = [url]
    product["Descrição curta"] = [tecnical_content]
    product["Descrição"] = [descryption]
    product["Images"] = [", ".join(img_src)]
    
    print('> Salvando em arquivo...')
    # [print(f"{index}: \t{content}") for index, content in product.items()]
    dataToExcel(product, nameOfFile)
    print('> Finalizado!')