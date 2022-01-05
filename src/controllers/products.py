import eventlet
from flask_socketio import emit
from src.controllers.database import select_products_from_database
from src.models.aliexpress import crawl_aliexpress
from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce


def load_products(links, ROOT_DIR, namefile, button_text="Ver produto", update=False):

    try:
        links_database = [link.external_url for link in select_products_from_database()]

        for index, link in enumerate(links):
            if link == "":
                continue
            
            if link in links_database:
                emit("message", f"Link já existe no banco de dados...")
                print('Link já existe no banco de dados...')
                eventlet.sleep(2.5)
                continue

            if button_text == "":
                button_text="Ver produto"

            emit("message", f"extraíndo {index + 1} de {len(links)} sites...")

            print(f"> Link: {link}")
            test_link = link.split('/')[2]
            print(f'> Base link: {test_link}')
            if (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
                crawl_amazon(url=link, ROOT_DIR=ROOT_DIR, nameOfFile=namefile, button_text=button_text, update=update)
            
            elif test_link == "www.magazinevoce.com.br":
                crawl_magazinevoce(url=link, nameOfFile=namefile, button_text=button_text, update=update)
            
            elif test_link == "pt.aliexpress.com" or test_link == "www.aliexpress.com.br":
                print('Extraíndo aliexpress...')
                crawl_aliexpress(url=link, root_path=ROOT_DIR, nameOfFile=namefile, button_text=button_text, update=update)
                
            if len(select_products_from_database()) > 0:
                emit('check', 'ACK!', broadcast=True, namespace="/")
        
        return "success", 200

    except Exception as error:
        emit("error", error)
        return f"500: {error}"


def update_produts(ROOT_DIR, namefile, button_text="Ver produto", update=True):
    try:
        links = select_products_from_database()
        for index, link in enumerate(links):
            print("Link: ", link.external_url)
            if link.external_url == "":
                continue
            
            if button_text == "":
                button_text="Ver produto"

            emit("message", f"Atualizado {index + 1} de {len(links)} sites...")

            print(f"> Link: {link.external_url}")
            test_link = link.external_url.split('/')[2]
            # print(f'> Base link: {test_link}')
            if (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
                crawl_amazon(url=link.external_url, ROOT_DIR=ROOT_DIR, nameOfFile=namefile, button_text=button_text, update=update)
            
            elif test_link == "www.magazinevoce.com.br":
                crawl_magazinevoce(url=link.external_url, nameOfFile=namefile, button_text=button_text, update=update)
            
            elif test_link == "pt.aliexpress.com" or test_link == "www.aliexpress.com.br":
                print('Extraíndo aliexpress...')
                crawl_aliexpress(url=link.external_url, root_path=ROOT_DIR, nameOfFile=namefile, button_text=button_text, update=update)
        
            # if len(select_products_from_database()) > 0:
            #     emit('check', 'ACK!', broadcast=True, namespace="/")
            return "success", 200

    except Exception as error:
        emit("error", error)
        return f"500: {error}"
