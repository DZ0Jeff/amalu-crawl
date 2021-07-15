import sys
from utils.setup import setSelenium
from utils.file_handler import dataToExcel
from utils.parser_handler import init_crawler, init_parser, remove_duplicates_on_list, remove_whitespaces
from bs4 import NavigableString
from utils.webdriver_handler import dynamic_page


def find_images(soap):
    def sanitize_image(image):
        return image['src'].split('/')[-1]

    def higher_resolution(image):
        try:
            return image.replace('88x66','618x463')
        
        except TypeError:
            return

    galery = soap.find('div', class_="pgallery")
    images = []

    for image in galery.find_all('img'):
        try:
            image_test = sanitize_image(image)
            if not image_test.endswith('.svg'):
                image = higher_resolution(image['src'])
                images.append(image)
        except (KeyError, TypeError):
            pass
    
    images = remove_duplicates_on_list(images)
    return '\n'.join(images)


def crawl_magazinevoce(url="https://www.magazinevoce.com.br/magazinei9bux/carga-para-aparelho-de-barbear-gillette-mach3-sensitive-16-cargas/p/218044400/ME/LADB/"):
    print('> iniciando magazinei9bux crawler...')
    soap = init_crawler(url)

    print('> extraíndo informações...')
    title = [element for element in soap.find('h3') if isinstance(element, NavigableString)][0].strip()
    raw_sku = soap.select_one('h3.hide-desktop span.product-sku').text
    sku = raw_sku.split(' ')[-1].replace(')','')
    category = soap.find('a', class_="category").text
    price = soap.find('div', class_="p-price").text
    installments = soap.find('p', class_="p-installment").text
    description = soap.find('table', class_="tab descricao").text
    galery = find_images(soap)

    details = dict()
    details['Título'] = [title]
    details['Categoria'] = [category]
    details['sku'] = [remove_whitespaces(sku)]
    details['Preço'] = [remove_whitespaces(price)]
    details['Parcelas'] = [remove_whitespaces(installments)]
    details['Descrição'] = [remove_whitespaces(description)]
    details['Galeria'] = [galery]

    print('> Salvando resultados...')
    dataToExcel(details, 'magazinevoce.csv')


def crawl_amazon(url="https://www.amazon.com.br/Smart-Monitor-LG-Machine-24TL520S/dp/B07SSCKJJ3/ref=sr_1_7?__mk_pt_BR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&dchild=1&keywords=smart+tv&qid=1626360552&sr=8-7"):
    
    print('> Iniciando Amazon crawler...')
    driver = setSelenium(False)
    html = dynamic_page(driver, url)
    driver.quit()
    soap = init_parser(html)
    # soap = init_crawler(url)

    print('> Extraíndo dados...')
    title = soap.select_one('h1 span')
    try:
        price = soap.find('span', id="priceblock_ourprice")
    except Exception:
        price = "Não disponível..."

    breadcrumb = soap.find('ul', class_="a-unordered-list a-horizontal a-size-small")
    category = breadcrumb.select('span.a-list-item')[-1]
    description = soap.find('div', id="feature-bullets")
    galery = soap.find('div', id="imgTagWrapperId").find('img')['src']

    details = dict()
    details['Título'] = [remove_whitespaces(title.text)]
    details['Preço'] = [price.text]
    details['Categoria'] = [remove_whitespaces(category.text)]
    details['Descrição'] = [remove_whitespaces(description.get_text(separator="\n"))]
    details['Galeria'] = [galery]

    # [print(f"{title}: {detail}") for title, detail in details.items()]
    print('> Salvando em arquivo...')
    dataToExcel(details, 'amazon-amostra.csv')

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
