from utils.file_handler import dataToExcel
from utils.parser_handler import init_crawler, remove_duplicates_on_list, remove_whitespaces
from bs4 import NavigableString


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
                print(image['src'])
                image = higher_resolution(image['src'])
                images.append(image)
        except (KeyError, TypeError):
            pass
    
    images = remove_duplicates_on_list(images)
    return '\n'.join(images)


def crawl_magazinevoce(url="https://www.magazinevoce.com.br/magazinei9bux/carga-para-aparelho-de-barbear-gillette-mach3-sensitive-16-cargas/p/218044400/ME/LADB/"):
    print('> iniciando AMALU...')
    soap = init_crawler(url)

    print('> extraíndo informações...')
    title = [element for element in soap.find('h3') if isinstance(element, NavigableString)][0].strip()
    raw_sku = soap.select_one('h3.hide-desktop span.product-sku').text
    sku = raw_sku.split(' ')[-1].replace(')','')
    price = soap.find('div', class_="p-price").text
    installments = soap.find('p', class_="p-installment").text
    description = soap.find('table', class_="tab descricao").text
    galery = find_images(soap)

    details = dict()
    details['Título'] = [title]
    details['sku'] = [sku]
    details['Preço'] = [remove_whitespaces(price)]
    details['Parcelas'] = [remove_whitespaces(installments)]
    details['Descrição'] = [remove_whitespaces(description)]
    details['Galeria'] = [galery]

    print('> Salvando resultados...')
    dataToExcel(details, 'magazinevoce.csv')


def main():
    """
    crawl magazinevoce.com and amazon.com to scrape prices
    """

    crawl_magazinevoce()


if __name__ == "__main__":
    main()
