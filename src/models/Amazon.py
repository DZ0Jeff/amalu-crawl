import re
from src.controllers.database import insert_products_in_database, update_by_sku
from utils.parser_handler import init_parser, remove_whitespaces
from utils.file_handler import dataToExcel
from src.utils import convert_price, format_table, getAmazonImageGalery, get_specs
from utils.setup import setSelenium
from utils.webdriver_handler import dynamic_page
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import ProtocolError, MaxRetryError, NewConnectionError


def crawl_amazon(url, ROOT_DIR, nameOfFile, button_text="Ver produto", update=False):
    

    def amazon_iframe(ASIN):
        return f'<iframe style="width:120px;height:240px;" marginwidth="0" marginheight="0" scrolling="no" frameborder="0" src="//ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=BR&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=vantajao09-20&language=pt_BR&marketplace=amazon&region=BR&placement={ASIN}&asins={ASIN}&linkId=6858d32406831f34277d5845ffb9e683&show_border=true&link_opens_in_new_window=true"></iframe>'
        ""

    url = str(url)
    print('> Iniciando Amazon crawler...')
    try:
        driver = setSelenium(root_path=ROOT_DIR, console=False)
    
    except WebDriverException:
        print('Falha o conectar ao driver... :(')
        return
    
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
            print("1 price: ", price)

        except Exception:
            try:
                price = soap.find('span', id="price_inside_buybox").get_text()
                print("2 price: ", price)

            except Exception:
                try:
                    raw_price = soap.select('div#corePrice_feature_div span span.a-offscreen')[0].text
                    print("3 raw_price: ", raw_price)
                    price = raw_price.split('R$')[-1]
                    print("3 preço: ", price)

                except Exception:
                    price = ""

        # promotional price
        try:
            promotional_price = soap.find('span', class_="priceBlockStrikePriceString a-text-strike").text
            print("promotional_price 1: ", promotional_price)

        except Exception:
            try:
                promotional_price = soap.find('td', class_="a-span12 a-color-secondary a-size-base").select_one('span.a-offscreen').text   
                print("promotional_price 2: ", promotional_price)

            except Exception:
                print('Not found...')
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
                print('preço se maior: ')
                details['Preço'] = [remove_whitespaces(promotional_price)]
            else:
                details['Preço Promocional'] = [remove_whitespaces(promotional_price)]
                print('preço se menor: ')
                details['Preço'] = [remove_whitespaces(price)] 
        except Exception:
            print('Exceção...')
            details['Preço Promocional'] = [remove_whitespaces(promotional_price)]
            details['Preço'] = [remove_whitespaces(price)] 
        
        details['Categorias'] = [f"{store} > {remove_whitespaces(category)}"]
        details['Url externa'] = [url]
        details['Texto do botão'] = [button_text]
        asin_final = amazon_iframe(remove_whitespaces(ean))
        details['Short description'] = [f"{asin_final}\n\n{specs}"]
        details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição Técnica\n\n{tecnical_details}{aditional_info}"]
        details['Imagens'] = [galery]

        [print(f"{title}: {detail[0]}") for title, detail in details.items()]
        print('> Salvando em arquivo...')
        if update:
            update_by_sku(details['SKU'][0], details)
        else:
            insert_products_in_database(details)
        # dataToExcel(details, f'{nameOfFile}.csv')
        print(f'> Arquivo {nameOfFile} salvo com sucesso!')
        return f'{nameOfFile}.csv'

    
    except (AttributeError, TypeError) as error:
        driver.quit()
        print(error)
        return str(error)

    except (ProtocolError, MaxRetryError, NewConnectionError):
        driver.quit()
        return

    except:
        driver.quit()
        raise

