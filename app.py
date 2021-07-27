import sys
import re
from bs4 import NavigableString

from src.utils import find_magalu_images, getAmazonImageGalery, get_specs, get_magazine_specs
from utils.setup import setSelenium
from utils.file_handler import dataToExcel
from utils.parser_handler import init_crawler, init_parser, remove_whitespaces
from utils.webdriver_handler import dynamic_page


def crawl_magazinevoce(url="https://www.magazinevoce.com.br/magazinei9bux/carga-para-aparelho-de-barbear-gillette-mach3-sensitive-16-cargas/p/218044400/ME/LADB/"):
    print('> iniciando magazinei9bux crawler...')
    soap = init_crawler(url)

    print('> extraíndo informações...')
    try:
        store = url.split('/')[3]
        title = [element for element in soap.find('h3') if isinstance(element, NavigableString)][0].strip()
        raw_sku = soap.select_one('h3.hide-desktop span.product-sku').text
        sku = raw_sku.split(' ')[-1].replace(')','').strip()
        category = soap.find('a', class_="category").text
        price = str(soap.find('div', class_="p-price").find('strong').text).replace("por", '')
        installments = soap.find('p', class_="p-installment").text
        specs = get_magazine_specs(soap)
        description = soap.find('table', class_="tab descricao").text
        galery = find_magalu_images(soap) # soap.find('div', class_="pgallery").find('img')['src'] 
        print(galery)

    except Exception: 
        print('> Falha ao extrair dados! contate do administrador do sistema...')
        return

    details = dict()
    details['Sku'] = [remove_whitespaces(sku)]
    details['Type'] = ["external"]
    # details['Loja'] = [store]
    details['Nome'] = [title]
    details['Categorias'] = [f"{store} > {category}"]
    details['Preço'] = [remove_whitespaces(price)]
    # details['Parcelas'] = [remove_whitespaces(installments)]
    details['Url Externa'] = [url]
    details['Texto do botão'] = ["Ver produto"]
    details['Short description'] = [specs]
    details['Descrição'] = [remove_whitespaces(description)]
    details['Imagens'] = [galery]

    # [print(f"{title}: {detail[0]}") for title, detail in details.items()]
    print('> Salvando resultados...')
    dataToExcel(details, 'magazinevoce-image.csv')


def crawl_amazon(url="https://www.amazon.com.br/Smart-Monitor-LG-Machine-24TL520S/dp/B07SSCKJJ3/ref=sr_1_7?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=smart+tv&qid=1626360552&sr=8-7"):
    
    url = str(url)
    print('> Iniciando Amazon crawler...')
    driver = setSelenium(False)
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
        
        # price of product
        try:
            price = soap.find('span', id="priceblock_ourprice").text
        except Exception:
            try:
                # raw_price = soap.find('tr', id="conditionalPrice").text
                raw_price = soap.find('span', id="price").text
                price = remove_whitespaces(raw_price)

            except Exception:
                price = "Não disponível..."

        # installments of price
        try:
            installments = soap.find('span', class_="best-offer-name a-text-bold").text
        
        except AttributeError:
            installments = ''

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

        # manufactory
        try:
            manufactor = str(soap.find('a', id="bylineInfo").text).replace('Marca:','')

        except AttributeError:
            manufactor = ""

        # description
        try:
            description = soap.find('div', id="feature-bullets").get_text(separator="\n")

        except AttributeError:
            try:
                description = soap.find('div', id="bookDescription_feature_div").text

            except Exception:
                description = ""

        # ean/sku
        try:
            ean = soap.find('th', string=re.compile("EAN")).findNext('td').text
        
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

        print(galery)
        details = dict()
        # details['Loja'] = [store]
        details['Type'] = ["external"]
        details['SKU'] = [remove_whitespaces(ean)]
        details['Nome'] = [remove_whitespaces(title)]
        # details['Marca'] = [remove_whitespaces(manufactor)]
        details['Preço'] = [price]
        # details['Parcelas'] = [remove_whitespaces(installments)]
        details['Categorias'] = [f"{store} > {remove_whitespaces(category)}"]
        details['Url externa'] = [url]
        details['Texto do botão'] = ["Ver produto"]
        details['Short description'] = [specs]
        details['Descrição'] = [remove_whitespaces(description)]
        details['Imagens'] = [galery]

        # [print(f"{title}: {detail[0]}") for title, detail in details.items()]
        print('> Salvando em arquivo...')
        dataToExcel(details, 'amazon-image.csv')
    
    except Exception:
        driver.quit()
        raise


def main():
    """
    crawl magazinevoce.com and amazon.com to scrape prices
    """
    link = sys.argv[1]
    if link != '' or 'pd_rd_w' or "pf_rd_p" or "pf_rd_r" or "pd_rd_wg" or "pd_rd_i":
        if link.split('/')[2] == "www.amazon.com.br":
            crawl_amazon(link)

        elif link.split('/')[2] == "www.magazinevoce.com.br":
            crawl_magazinevoce(link)
        else:
            print('> Link inválido! insira um link válido de um produto da amazon ou magazinevocê...')
    
    else:
        print('> Insira um link!')


if __name__ == "__main__":
    main()
