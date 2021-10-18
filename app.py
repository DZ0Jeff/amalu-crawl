import eventlet
eventlet.monkey_patch()

from src.controllers.database import delete_all_database, select_products_from_database

import os
from time import sleep

from flask import request, jsonify
from flask.helpers import send_file, url_for
from flask_executor import Executor
from werkzeug.utils import redirect
from src.utils import delete_product

from src.models import app, socketio, db
from src.models.Shopee import crawl_shopee
from src.models.aliexpress import crawl_aliexpress
from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce
from utils.file_handler import dataToExcel

from src.controllers.products import load_products, update_produts
from flask_socketio import emit


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

executor = Executor(app)

app.config['EXECUTOR_MAX_WORKERS'] = 1
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True


@app.route('/')
def index():
    return jsonify(
        {
            'Routes': { 
                '/amazon': 'Crawl amazon products, args: link of product', 
                '/magazinevoce': 'Crawl magazinei9bux product details, args: link of product',
                '/aliexpress': 'Crawl aliexpress product details, args: link of product',
                # '/shopee': 'Crawl shopee product details, args: link of product'
                '/products': "Crawl all selected stores, args: response.json"
            } 
        }
    )

@socketio.on('connection')
def init_connection(msg):
    print('Status: ', msg)
    socketio.emit('init', 'Resposta recebida!', broadcast=True, namespace="/")

    if len(select_products_from_database()) > 0:
        emit('check', 'ACK!', broadcast=True, namespace="/")


@socketio.on('products')
def send_products(links, button_text="Ver produto"):
    namefile = "products"
    # delete_product('products.csv')

    emit('message', 'Iniciando importação...', broadcast=True, namespace="/")
    load_products(links, ROOT_DIR, namefile, button_text)
    emit('message', 'Importação concluída!')
    print('Importação concluída!')
    return redirect(url_for('show_products'))


@socketio.on('update')
def update(button_text="Ver produto"):
    namefile = "products"
    emit('message', 'Iniciando atualização de produtos...', broadcast=True, namespace="/")
    update_produts(ROOT_DIR, namefile, button_text, update=True)
    emit('message', 'Atualização concluída!')
    print('Atualização concluída!')
    return redirect(url_for('show_products'))


@socketio.on('disconnect')
def disconnect():
    socketio.stop()
    

@app.route('/show')
def show_products():
    products = select_products_from_database()
    filename = 'products.csv'
    button_text_name = request.args.get('button')
    if button_text_name == "":
        button_text_name = "Ver produto"

    target = dict()
    for product in products:
        print('Before: ', [button_text_name])
        target.setdefault('type', [])
        target.setdefault('SKU', [])
        target.setdefault('Nome', [])
        target.setdefault('Preço Promocional', [])
        target.setdefault('Preço', [])
        target.setdefault('Categorias', [])
        target.setdefault('Url externa', [])
        target.setdefault('Texto do botão', [])
        target.setdefault('Short description', [])
        target.setdefault('Descrição', [])
        target.setdefault('Imagens', [])

        target['type'].append(product.type_product)
        target['SKU'].append(product.sku)
        target['Nome'].append(product.name)
        target['Preço Promocional'].append(product.promotional_price)
        target['Preço'].append(product.price)
        target['Categorias'].append(product.category)
        target['Url externa'].append(product.external_url)
        target['Texto do botão'].append(button_text_name)
        target['Short description'].append(product.short_description)
        target['Descrição'].append(product.description)
        target['Imagens'].append(product.images)
        print('After: ', target['Texto do botão'])
 
    dataToExcel(target, filename, custom=True)
    
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', download_name=filename ,as_attachment=True, max_age=-1)

    return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!", 500    


@app.route('/amazon')
def amazon_download():
    delete_product('Amazon.csv')
    link = request.args.get('url')

    if link == '':
        return 'Insira um link'

    test_link = link.split('/')[2]
    if not (test_link == "www.amazon.com.br" or test_link == "www.amazon.com"):
        return "Insira o um link válido!"

    print('> Iniciando...')
    # executor.submit(crawl_amazon, link, ROOT_DIR, "Amazon")
    crawl_amazon(link, ROOT_DIR, "Amazon")
    return redirect(url_for('amazon_get'))


@app.route('/amazonget')
def amazon_get():
    filename = 'Amazon.csv'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, max_age=-1)

    sleep(5)
    return redirect(url_for('amazon_get'))


@app.route('/magazinevoce')
def magazinei9bux_get():
    delete_product('Magalu.csv')
    link = request.args.get('url')

    if link == '' and link.split('/')[2] != "www.magazinevoce.com.br":
       return 'Insira um link válido!'

    filename = crawl_magazinevoce(link, 'Magalu')

    if not isinstance(filename, str):
        return f"Um erro aconteceu: {filename}"

    return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', download_name=filename ,as_attachment=True, max_age=-1)


@app.route('/aliexpress')
def aliexpress_download():
    name_file = 'aliexpress'
    delete_product(name_file)
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "pt.aliexpress.com.br":
       return 'Insira um link válido!'

    print('A iniciar processo...')
    try:
        executor.futures.pop('aliexpress_crawl')
    except Exception:
        pass
    
    executor.submit_stored('aliexpress_crawl', crawl_aliexpress, url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    return redirect(url_for('aliexpress_get'))


@app.get('/aliexpressget')
def aliexpress_get():
    filename = 'aliexpress.csv'

    if not executor.futures.done('aliexpress_crawl'):
        sleep(10)
        return redirect(url_for('aliexpress_get')) 

    future = executor.futures.pop('aliexpress_crawl')    
    if os.path.exists(filename):
        print(future.result())
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', download_name=filename ,as_attachment=True, max_age=-1)
    
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"


@app.get('/shopee')
def shopee_download():
    name_file = 'shopee.csv'
    delete_product(name_file)
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "www.shopee.com.br":
       return 'Insira um link válido!'

    print('A iniciar processo...')
    try:
        executor.futures.pop('shopee_crawl')
    except Exception:
        pass
    
    executor.submit_stored('shopee_crawl', crawl_shopee, url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    return redirect(url_for('shopee_get'))


@app.route('/shopeeget')
def shopee_get():
    filename = 'shopee.csv'

    if not executor.futures.done('shopee_crawl'):
        sleep(10)
        return redirect(url_for('shopee_get')) 

    future = executor.futures.pop('shopee_crawl')    
    if os.path.exists(filename):
        print(future.result())
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', download_name=filename ,as_attachment=True, max_age=-1)
    
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"

@app.route('/delete-products')
def delete_products():
    try:
        delete_all_database()
        return "Data deleted successsuly!"
    
    except Exception:
        raise

@app.route('/error')
def error_image():
    filename = 'error.png'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='image/png', download_name=filename, as_attachment=True, max_age=-1)
    
    return "Screenshot nao disponível!"


if __name__ == "__main__":
    db.create_all()
    socketio.run(app, host='0.0.0.0') # host='0.0.0.0'
    # app.run()