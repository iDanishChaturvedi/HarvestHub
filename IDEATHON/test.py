from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session

# ================= CONFIG =================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= DATABASE =================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    farmer = db.Column(db.String(100))

# ================= FARMER PAGE =================
@app.route('/')
def farmer():
    return render_template("farmer.html")

# ================= ADD PRODUCT =================
@app.route('/add-product', methods=['POST'])
def add_product():
    product = Product(
        name=request.form['name'],
        price=int(request.form['price']),
        quantity=int(request.form['quantity']),
        farmer=request.form['farmer']
    )
    db.session.add(product)
    db.session.commit()
    return redirect('/products')

# ================= CUSTOMER PAGE =================
@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template("customer.html", products=all_products)

# ================= BUY PRODUCT =================
@app.route('/buy/<int:id>', methods=['POST'])
def buy_product(id):
    product = Product.query.get(id)
    if not product:
        return redirect('/products')

    if 'cart' not in session:
        session['cart'] = []

    # Get quantity from form
    quantity = request.form.get('quantity', '1')
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    # Add to cart
    session['cart'].append({
        'name': product.name,
        'price': product.price,
        'quantity': quantity
    })
    session.modified = True

    # Reduce quantity in DB
    if product.quantity > quantity:
        product.quantity -= quantity
    else:
        db.session.delete(product)
    db.session.commit()

    return redirect('/cart')

# ================= STORE PAGE =================
@app.route('/store')
def store():
    store_items = [
        {'name': 'Urea Fertilizer', 'price': 300},
        {'name': 'Tomato Seeds', 'price': 120},
        {'name': 'Pesticide Spray', 'price': 250},
    ]
    return render_template("store.html", store_items=store_items)

# ================= BUY STORE ITEM =================
@app.route('/buy-store-item', methods=['POST'])
def buy_store_item():
    name = request.form['name']
    price = int(request.form['price'])

    if 'cart' not in session:
        session['cart'] = []

    quantity = request.form.get('quantity', '1')
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    session['cart'].append({
        'name': name,
        'price': price,
        'quantity': quantity
    })
    session.modified = True

    return redirect('/cart')

# ================= CART PAGE =================
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total=total)

# ================= CHECKOUT =================
@app.route('/checkout', methods=['POST'])
def checkout():
    session.pop('cart', None)  # Clear cart
    return redirect('/success')

# ================= SUCCESS PAGE =================
@app.route('/success')
def success():
    return render_template("success.html")

# ================= RUN APP =================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
