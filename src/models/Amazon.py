import re
from utils.parser_handler import init_crawler, init_parser, remove_whitespaces
from utils.file_handler import dataToExcel
from src.utils import convert_price, format_table, getAmazonImageGalery, get_specs
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page


def crawl_amazon(url, ROOT_DIR, nameOfFile="Amazon"):
    
    url = str(url)
    print('> Iniciando Amazon crawler...')
    driver = setSelenium(root_path=ROOT_DIR, console=False)
    try:
        driver.get(url)
        galery = getAmazonImageGalery(driver)
        html = dynamic_page(driver)
        driver.quit()
        soap = init_parser(html)

        print('> Extraíndo dados...')
        
        # name of product
        title = soap.select_one('h1 span').text

        # store target
        store = url.split("/")[2].split('.')[1]
        # specs
        try:
            raw_specs = soap.find('div', id="productOverview_feature_div")
            specs = get_specs(raw_specs)

        except AttributeError:
            specs = ""

        # category
        try:
            breadcrumb = soap.find('ul', class_="a-unordered-list a-horizontal a-size-small")
            category = breadcrumb.select('span.a-list-item')[-1].text
        except AttributeError:
            category = ""

        # description
        try:
            description = soap.find('div', id="feature-bullets").get_text(separator="\n")

        except AttributeError:
            try:
                description = soap.find('div', id="bookDescription_feature_div").text

            except Exception:
                description = ""

        # tecnical details
        try:
            raw_tecnical_details = soap.find('table', id="productDetails_techSpec_section_1")
            tecnical_details = format_table(raw_tecnical_details)

        except AttributeError:
            tecnical_details = ""

        try:
            raw_info = soap.find('table', id="productDetails_detailBullets_sections1")
            aditional_info = format_table(raw_info)

        except AttributeError:
            aditional_info = ""

        # ean/sku
        try:
            ean = soap.find('th', string=re.compile("ASIN")).findNext('td').text
        
        except AttributeError:
            ean = ""

        # images
        if not galery:
            try:
                galery = soap.find('div', id="imgTagWrapperId").find('img')['src']
            
            except AttributeError:
                try:
                    galery = soap.find('img', id="imgBlkFront")['src']
                
                except Exception:
                    galery = ""

        # price of product    
        try:
            # raw_price = soap.find('tr', id="conditionalPrice").text
            raw_price = soap.find('span', id="price").text
            price = remove_whitespaces(raw_price)

        except Exception:
            try:
                price = soap.find('span', id="price_inside_buybox").get_text()

            except Exception:
                price = ""

        # promotional price
        try:
            promotional_price = soap.find('span', class_="priceBlockStrikePriceString a-text-strike").text
            

        except AttributeError:
            try:
                promotional_price = soap.find('td', class_="a-span12 a-color-secondary a-size-base").text    

            except Exception:
                promotional_price = ""

        details = dict()
        details['Type'] = ["external"]
        details['SKU'] = [remove_whitespaces(ean)]
        details['Nome'] = [remove_whitespaces(title)]

        decimal_promotional_price = convert_price(remove_whitespaces(promotional_price))
        decimal_price = convert_price(remove_whitespaces(price))

        try:
            if decimal_promotional_price > decimal_price:
                details['Preço Promocional'] = [remove_whitespaces(price)]
                details['Preço'] = [remove_whitespaces(promotional_price)]
            else:
                details['Preço Promocional'] = [remove_whitespaces(price)]
                details['Preço'] = [remove_whitespaces(promotional_price)] 
        except Exception:
            details['Preço Promocional'] = [remove_whitespaces(promotional_price)]
            details['Preço'] = [remove_whitespaces(price)] 
        
        details['Categorias'] = [f"{store} > {remove_whitespaces(category)}"]
        details['Url externa'] = [url]
        details['Texto do botão'] = ["Ver produto"]
        details['Short description'] = [specs]
        details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição Técnica\n\n{tecnical_details}{aditional_info}"]
        details['Imagens'] = [galery]

        # [print(f"{title}: {detail[0]}") for title, detail in details.items()]
        print('> Salvando em arquivo...')
        dataToExcel(details, f'{nameOfFile}.csv')
        print(f'> Arquivo {nameOfFile} salvo com sucesso!')
        return f'{nameOfFile}.csv'

    
    except Exception as error:
        driver.quit()
        return str(error)
