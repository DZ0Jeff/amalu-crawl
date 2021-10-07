from flask_socketio import emit
from src.models.aliexpress import crawl_aliexpress
from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce


def load_products(links, ROOT_DIR, namefile, button_text="Ver produto"):
    try:
        for index, link in enumerate(links):
            if link == "":
                continue

            emit("message", f"extraíndo {index + 1} de {len(links)} sites...")
            print(f"> Link: {link}")
            test_link = link.split('/')[2]
            print(f'> Base link: {test_link}')
            if (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
                crawl_amazon(link, ROOT_DIR, namefile, button_text)
            
            elif test_link == "www.magazinevoce.com.br":
                crawl_magazinevoce(link, namefile, button_text)
            
            elif test_link == "pt.aliexpress.com" or test_link == "www.aliexpress.com.br":
                crawl_aliexpress(url=link, root_path=ROOT_DIR, nameOfFile=namefile, button_text=button_text)
        
        return "success", 200

    except Exception as error:
        emit("message",error)
        return f"500: {error}"