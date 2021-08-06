import os
import re
from bs4 import NavigableString
from flask import request
from flask.helpers import send_file

from src.utils import find_magalu_images, format_table, getAmazonImageGalery, get_links, get_specs, get_magazine_specs
from src.models import init_app
from utils.setup import setSelenium
from utils.file_handler import dataToExcel
from utils.parser_handler import init_crawler, init_parser, remove_whitespaces
from utils.webdriver_handler import dynamic_page
import fnmatch


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def crawl_magazinevoce(url, nameOfFile="Magazinevocê", verbose=False):
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
        # return

    details = dict()
    details['Sku'] = [remove_whitespaces(sku)]
    details['Type'] = ["external"]
    details['Nome'] = [title]
    details['Categorias'] = [f"{store} > {category}"]
    details['Preço'] = [f"{remove_whitespaces(price)} (Valor aproximado)"]
    details['Url Externa'] = [url]
    details['Texto do botão'] = ["Ver produto"]
    details['Short description'] = [specs]
    details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição\n\n{tecnical_details}"]
    details['Imagens'] = [galery]

    if verbose:
        [print(f"{title}: {detail[0]}") for title, detail in details.items()]
    
    print('> Salvando resultados...')
    dataToExcel(details, f'{nameOfFile}.csv')
    return f'{nameOfFile}.csv'


def crawl_amazon(url, nameOfFile="Amazon"):
    
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
            urlPrice = f"https://ws-na.amazon-adsystem.com/widgets/q?ServiceVersion=20070822&OneJS=1&Operation=GetAdHtml&MarketPlace=BR&source=ss&ref=as_ss_li_til&ad_type=product_link&tracking_id=vantajao0e-20&language=pt_BR&marketplace=amazon&region=BR&placement=B088HJ3FCX&asins={ean}&linkId=2113f78bf439002e072fcf867b4c8889&show_border=true&link_opens_in_new_window=true"
            adPrice = init_crawler(urlPrice)
            price = adPrice.find('span', class_="price").text
            
        except Exception:
            try:
                # raw_price = soap.find('tr', id="conditionalPrice").text
                raw_price = soap.find('span', id="price").text
                price = remove_whitespaces(raw_price)

            except Exception:
                price = ""


        details = dict()
        details['Type'] = ["external"]
        details['SKU'] = [remove_whitespaces(ean)]
        details['Nome'] = [remove_whitespaces(title)]
        details['Preço'] = [price]
        details['Categorias'] = [f"{store} > {remove_whitespaces(category)}"]
        details['Url externa'] = [url]
        details['Texto do botão'] = ["Ver produto"]
        details['Short description'] = [specs]
        details['Descrição'] = [f"{remove_whitespaces(description)}\n\nDescrição Técnica\n\n{tecnical_details}{aditional_info}"]
        details['Imagens'] = [galery]

        # [print(f"{title}: {detail[0]}") for title, detail in details.items()]
        print('> Salvando em arquivo...')
        dataToExcel(details, f'{nameOfFile}.csv')
        return f'{nameOfFile}.csv'

    
    except Exception:
        driver.quit()
        raise


def process_link(link):
    link = link.replace('"','')
    if link != '' or 'pd_rd_w' or "pf_rd_p" or "pf_rd_r" or "pd_rd_wg" or "pd_rd_i":
        if link.split('/')[2] == "www.amazon.com.br":
            return crawl_amazon(link, "Amazon")

        elif link.split('/')[2] == "www.magazinevoce.com.br":
            print(link)
            return crawl_magazinevoce(link,'Magalu')
        
        else:
            print('> Link inválido! insira um link válido de um produto da amazon ou magazinevocê...')
            return
    
    else:
        print('> Insira um link!')
        return


def main():
    """
    crawl magazinevoce.com and amazon.com to scrape prices
    """
    
    links = get_links()

    if len(links) == 0: print(f"Insira um link da Amazon ou Magalu em entrada.txt!"); return

    for link in links:
        process_link(link)


app = init_app()


@app.route('/')
def index():
    return "Welcome to Amalu"


@app.route('/product')
def load_product():
    targetLink = request.args.get('url')
    try:
        filename = process_link(targetLink)

        if not filename:
            return "Arquivo não baixado, contate o adminstrador!"

    except Exception as error:
        return f'Um erro Aconteceu, verifique cokm o administador do sistema <br/> Erro: {error}'
    
    return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, cache_timeout=-1)

@app.route('/delete')
def delete_product():
    for root, dirs, files in os.walk('.'):
        for name in files:
            if fnmatch.fnmatch(name, ".csv"):
                os.remove(name)

if __name__ == "__main__":
    app.run()
