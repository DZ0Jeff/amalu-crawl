import os
from time import sleep

from flask import request, jsonify
from flask.helpers import send_file, url_for
from flask_executor import Executor
from werkzeug.utils import redirect
from flask_cors import CORS
from src.models.aliexpress import crawl_aliexpress

from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce
from src.utils import delete_product
from src.models import init_app


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


app = init_app()
CORS(app, expose_headers=["Content-Disposition"])
executor = Executor(app)

app.config['EXECUTOR_MAX_WORKERS'] = 1
app.config['EXECUTOR_TYPE'] = 'thread'
app.config['EXECUTOR_PROPAGATE_EXCEPTIONS'] = True
# redirect_limit = []


@app.route('/')
def index():
    return jsonify(
        {
            'Routes': { 
                '/amazon': 'Crawl amazon products, args: link of product', 
                '/magazinevoce': 'Crawl magazinei9bux product details, args: link of product',
                '/aliexpress': 'Crawl aliexpress product details, args: link of product'
            } 
        }
    )


@app.route('/amazon')
def amazon_download():
    delete_product('Amazon.csv')
    link = request.args.get('url')

    if link == '':
        return 'Insira um link'

    if not link.split('/')[2] == "www.amazon.com.br":
        return "Insira o um link válido!"

    executor.submit(crawl_amazon, link, ROOT_DIR, "Amazon")
    return redirect(url_for('amazon_get'))


@app.route('/amazonget')
def amazon_get():
    filename = 'Amazon.csv'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, cache_timeout=-1)

    sleep(5)
    return redirect(url_for('amazon_get'))


@app.route('/magazinevoce')
def magazinei9bux_get():
    delete_product('Magalu.csv')
    link = request.args.get('url')

    if link == '' and not link.split('/')[2] == "www.magazinevoce.com.br":
       return 'Insira um link válido!'

    filename = crawl_magazinevoce(link,'Magalu')

    if not isinstance(filename, str):
        return f"Um erro aconteceu: {filename}"

    return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', attachment_filename=filename ,as_attachment=True, cache_timeout=-1)


@app.route('/aliexpress')
def aliexpress_download():
    name_file = 'aliexpress.csv'
    delete_product(name_file)
    link = request.args.get('url')

    if link == '' and link.split('/')[2] == "pt.aliexpress.com.br":
       return 'Insira um link válido!'

    print('A iniciar processo...')
    executor.submit_stored('aliexpress', crawl_aliexpress, url=link, root_path=ROOT_DIR, nameOfFile=name_file)
    return redirect(url_for('aliexpress_get'))


@app.get('/aliexpressget')
def aliexpress_get():
    filename = 'aliexpress.csv'

    if not executor.futures.done('calc_power'):
        sleep(10)
        # redirect_limit.append(0)
        # print('Limit: ', len(redirect_limit))
        return redirect(url_for('aliexpress_get')) 

    future = executor.futures.pop('calc_power')
    if not future.result():
        if os.path.exists(filename):
            return send_file(os.path.join(ROOT_DIR, filename), mimetype='application/x-csv', attachment_filename=filename ,as_attachment=True, cache_timeout=-1)
    else:
        return "Erro ao gerar arquivo! ou link inserido fora do ar, tente novamente!"

    # if len(redirect_limit) >= 10:
    #     return "Arquivo não achado ou algum erro aconteceu...."


@app.route('/error')
def error_image():
    filename = 'error.png'
    if os.path.exists(filename):
        return send_file(os.path.join(ROOT_DIR, filename), mimetype='image/png', attachment_filename=filename, as_attachment=True, cache_timeout=-1)
    
    return "Screenshot nao disponível!"


if __name__ == "__main__":
    app.debug = True
    app.run()    
