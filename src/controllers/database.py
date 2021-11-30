from src.models.product_schema import Product
from src.models import db


def insert_products_in_database(product_info):
    db.create_all()
    # products = select_products_from_database()
    # for product in products:
    #     if product.sku == product_info["SKU"][0] and product.price == product_info["Preço"][0]:
    #         print('Não inserindo, já existe!')
    #         return

    product = Product(
        type_product=product_info["Type"][0], 
        sku=product_info["SKU"][0], 
        name=product_info["Nome"][0],
        promotional_price=product_info["Preço Promocional"][0], 
        price=product_info["Preço"][0], 
        category=product_info["Categorias"][0], 
        external_url=product_info["Url externa"][0], 
        button_text=product_info['Texto do botão'][0], 
        short_description=product_info['Short description'][0], 
        description=product_info["Descrição"][0], 
        images=product_info['Imagens'][0]
    )

    db.session.add(product)
    db.session.commit()
    

def select_products_from_database():
    db.create_all()
    products = Product.query.all()
    return products


def delete_all_database():    
    try:
        db.session.query(Product).delete()
        db.session.commit()
    except:
        db.session.rollback()


def delete_by_sku(sku):
    try:
        db.session.query(Product).filter(Product.sku==sku).delete()
        db.session.commit()
    except:
        db.session.rollback()
        

def update_by_sku(sku, product_info):
    product = Product.query.filter_by(sku=sku).first()
    product.type_product            = str(product_info["Type"][0])
    product.sku                     = str(product_info["SKU"][0])
    product.name                    = str(product_info["Nome"][0])
    product.promotional_price       = str(product_info["Preço Promocional"][0]) 
    product.price                   = str(product_info["Preço"][0]) 
    product.category                = str(product_info["Categorias"][0])
    product.external_url            = str(product_info["Url externa"][0]) 
    product.button_text             = str(product_info['Texto do botão'][0]) 
    product.short_description       = str(product_info['Short description'][0]) 
    product.description             = str(product_info["Descrição"][0])
    product.images                  = str(product_info['Imagens'][0])
    
    db.session.commit()
