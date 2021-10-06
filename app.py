import eventlet
eventlet.monkey_patch()

import os
from time import sleep

from flask import request, jsonify
from flask.helpers import send_file, url_for
from flask_executor import Executor
from werkzeug.utils import redirect
from src.utils import delete_product

from src.models import app, socketio
from src.models.Shopee import crawl_shopee
from src.models.aliexpress import crawl_aliexpress
from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce

from src.controllers.products import load_products
from flask_socketio import emit, namespace


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


executor = Executor(app)

app.config['EXECUTOR_MAX_WORKERS'] = 1
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True


@socketio.on('connection')
def init_connection(msg):
    print('Status: ', msg)
    socketio.emit('init', 'Resposta recebida!', broadcast=True, namespace="/")


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


@app.route('/products', methods=['POST'])
def products():
    links = request.json
    namefile = "products"
    delete_product('products.csv')

    executor.submit_stored('products', load_products, links, ROOT_DIR, namefile)
    return redirect(url_for('get_products')) # "redirect", 302  


@socketio.on('products')
def send_products(links):
    namefile = "products"
    delete_product('products.csv')
    emit('message', 'Iniciando importação...', broadcast=True, namespace="/")

    load_products(links, ROOT_DIR, namefile)
    emit('message', 'Importação concluída!')
    print('Importação concluída!')
    return redirect(url_for('download_products'))


@app.route('/get_products')
def get_products():
    filename = 'products.csv'

    if not executor.futures.done('products'):
        sleep(15)
        return redirect(url_for('get_products')) # "loading...", 302 

    future = executor.futures.pop('products')    
    if os.path.exists(filename):
        print(future.result())
        if future.result()[-1] == 500:
            return "Internal server error", 500

        return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', download_name=filename ,as_attachment=True, max_age=-1)
    
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"


@app.route('/download_products')
def download_products():
    filename = 'products.csv'
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

    executor.submit(crawl_amazon, link, ROOT_DIR, "Amazon")
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
    name_file = 'aliexpress.csv'
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


@app.route('/error')
def error_image():
    filename = 'error.png'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='image/png', download_name=filename, as_attachment=True, max_age=-1)
    
    return "Screenshot nao disponível!"


if __name__ == "__main__":
    # app.debug = True
    socketio.run(app, host='0.0.0.0')
