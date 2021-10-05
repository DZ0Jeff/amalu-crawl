from src.models.aliexpress import crawl_aliexpress
from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce


def load_products(links, ROOT_DIR, namefile):
    try:
        for link in links:
            print("> Link: ", link)
            test_link = link.split('/')[2]
            print('> Base link: ', test_link)
            if (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
                crawl_amazon(link, ROOT_DIR, namefile)
            
            elif link != '' and link.split('/')[2] == "www.magazinevoce.com.br":
                crawl_magazinevoce(link, namefile)
            
            elif link != '' and link.split('/')[2] == "pt.aliexpress.com.br" or link != '' and link.split('/')[2] == "pt.aliexpress.com":
                print('> Iniciando Aliexpress...')
                crawl_aliexpress(url=link, root_path=ROOT_DIR, nameOfFile=namefile)
        
        return "success", 200

    except Exception as error:
        print(error)
        return f"500: {error}"