from src.utils import convert_price, find_magalu_images, get_magazine_specs, get_specs
from utils.parser_handler import init_crawler, remove_whitespaces
from utils.file_handler import dataToExcel
from bs4 import NavigableString
from src.controllers.database import insert_products_in_database, update_by_sku


def crawl_magazinevoce(url, nameOfFile, button_text="Ver produto", verbose=False, update=False):
    print('> iniciando magazinei9bux crawler...')
    soap = init_crawler(url)

    print('> extraíndo informações...')
    try:
        store = "Magalu" # url.split('/')[3]
        title = [element for element in soap.find('h3') if isinstance(element, NavigableString)][0].strip()
        raw_sku = soap.select_one('h3.hide-desktop span.product-sku').text
        sku = raw_sku.split(' ')[-1].replace(')','').strip()
        category = soap.find('a', class_="category").text
        try:
            price = str(soap.find('small', class_="p-through").get_text()).replace('de', '')
            promotional_price = str(soap.find('div', class_="p-price").find('strong').text).replace("por", '')
        
        except AttributeError:
            try:
                promotional_price = ''
                price = str(soap.find('div', class_="p-price").find('strong').text).replace("por", '')
            
            except Exception:
                print('> Erro ao extraír o preço!')
                return
        
        try:
            raw_tecnical_details = soap.find('table', class_="tab ficha-tecnica")
            tecnical_details = get_specs(raw_tecnical_details)
        
        except Exception:
            tecnical_details = ""

        specs = get_magazine_specs(soap)
        description = soap.find('table', class_="tab descricao").text
        galery = find_magalu_images(soap) # soap.find('div', class_="pgallery").find('img')['src'] 

    except Exception: 
        print('> Falha ao extrair dados! contate do administrador do sistema...')
        raise

    details = dict()
    details['Type'] = ["external"]
    details['SKU'] = [remove_whitespaces(sku)]
    details['Nome'] = [title]
    details['Preço Promocional'] = [remove_whitespaces(promotional_price)]
    details['Preço'] = [remove_whitespaces(price)]
    details['Categorias'] = [f"{store} > {category}"]
    details['Url externa'] = [url]
    details['Texto do botão'] = [button_text]
    details['Short description'] = [specs]
    details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição\n\n{tecnical_details}"]
    details['Imagens'] = [galery]

    
    # [print(f"{title}: {detail[0]}") for title, detail in details.items()]
    # print(price)
    # print(promotional_price)
    print('> Salvando resultados...')
    if update:
        update_by_sku(details['SKU'][0], details)

    else:
        insert_products_in_database(details)
    
    # dataToExcel(details, f'{nameOfFile}.csv')
    return f'{nameOfFile}.csv'
