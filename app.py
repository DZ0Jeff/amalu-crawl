import os

from flask import request, jsonify
from flask.helpers import send_file
from flask_executor import Executor

from src.models.Amazon import crawl_amazon
from src.models.magazinei9bux import crawl_magazinevoce

from src.utils import delete_product, get_links
from src.models import init_app
import fnmatch


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

app = init_app()
executor = Executor(app)


@app.route('/')
def index():
    return jsonify(
        {
            'Routes': { 
                '/amazon': 'Crawl amazon products, args: link of product', 
                '/magazinei9bux': 'crawl magazinei9bux product details, args: link of product' 
            } 
        }
    )


@app.route('/amazon')
def amazon_get():
    delete_product('Amazon.csv')
    link = request.args.get('url')

    if link == '' or not link.split('/')[2] == "www.amazon.com.br":
        return 'Insira um link válido!'

    future = executor.submit(crawl_amazon, link, ROOT_DIR, "Amazon")
    filename = future.result()
    return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, cache_timeout=-1)


@app.route('/magazinevoce')
def magazinei9bux_get():
    delete_product('Magalu.csv')
    link = request.args.get('url')

    if link == '' and not link.split('/')[2] == "www.magazinevoce.com.br":
       return 'Insira um link válido!'

    filename = crawl_magazinevoce(link,'Magalu')
    return send_file(os.path.join(ROOT_DIR, filename), as_attachment=True, cache_timeout=-1)


if __name__ == "__main__":
    app.debug = True
    app.run()

