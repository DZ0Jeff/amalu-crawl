from src.models import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_product = db.Column(db.String, nullable=False)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    promotional_price = db.Column(db.String)
    price = db.Column(db.String)
    category = db.Column(db.String)
    external_url = db.Column(db.String)
    button_text = db.Column(db.String)
    short_description = db.Column(db.String)
    description = db.Column(db.String)
    images = db.Column(db.String)

    def __repr__(self):
        return '<Product %r>' % self.name