from src.utils import convert_price
from utils.setup import setSelenium
from utils.webdriver_handler import smooth_scroll
from selenium.common.exceptions import NoSuchElementException
from utils.file_handler import dataToExcel


def crawl_shopee(url, root_path, nameOfFile):

    print('> Iniciando Shopee Crawler...')
    driver = setSelenium(root_path=root_path, console=False)
    try:
        print('> Driver inicializado! iniciando site...')
        driver.get(url)
        driver.implicitly_wait(220)

        print('> scrollando página...')
        smooth_scroll(driver)

        print('> Extraindo dados...')

        # print('Sku: ')
        sku = url.split('.')[3]

        print('> Extrair Nome...')
        title = driver.find_element_by_css_selector('.attM6y').text

        print('> Extrair preço...')
        price_container = driver.find_element_by_css_selector('.flex.items-center._3iPGsU')
        try:
            price = price_container.find_element_by_css_selector('._2MaBXe').text
        
        except NoSuchElementException:
            price = ''

        promotional_price = price_container.find_element_by_css_selector('.flex.items-center').find_element_by_tag_name('div').text
        
        print('> Extrair categoria...')
        category = str(driver.find_element_by_css_selector('.flex.items-center._1J-ojb.page-product__breadcrumb').text).replace('\n', ' > ')
        
        print('> Extrair descrição')
        description = driver.find_elements_by_css_selector('._3wdEZ5')
        short_description = description[0].text
        details = description[-1].text
        
        print('> Extrair galeria...')
        galery = driver.find_element_by_css_selector('._3k2CdZ')
        images = galery.find_elements_by_css_selector('._12uy03._2GchKS')
        extracted_images = []
        [extracted_images.append(image.get_attribute("style").split('"')[1]) for image in images]
        extracted_images = ','.join(extracted_images)

        print('\n')
        print('> Mostrar resultados...')
        print('Nome: ', title)
        print('Preço promocional: ', promotional_price)
        print('Preço: ', price)
        print('Sku: ', sku)
        print('Url Externa: ', url)
        print('Categoria: ', category)
        # print('Descrição curta: ', short_description)
        # print('Descrição: ', details)
        print('Galeria: \n')
        [print(image.get_attribute("style").split('"')[1]) for image in images]

        data = dict()

        data['Type'] = ["external"]
        data['SKU'] = [sku]
        data['Nome'] = [title]

        decimal_promotional_price = convert_price(promotional_price)
        decimal_price = convert_price(price)
        if price == '' or decimal_promotional_price > decimal_price:
            data['Preço'] = [promotional_price]
            data['Preço Promocional'] = [price]
        else:
            data['Preço Promocional'] = [promotional_price]
            data['Preço'] = [price]
        data['Categorias'] = [category]
        data['Url externa'] = [url]
        data['Texto do botão'] = ["Ver produto"]
        data['Short description'] = [short_description]
        data['Descrição'] = [details]
        data['Imagens'] = [extracted_images]
        dataToExcel(data, nameOfFile)

    except Exception:
        driver.quit()
        raise

    except KeyboardInterrupt:
        driver.quit()
        print('> Saindo volte sempre!')