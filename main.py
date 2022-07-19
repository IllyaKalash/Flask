from peewee import *
from flask import Flask, render_template, request, redirect, url_for

from config import db

app = Flask(__name__)


class BaseModel(Model):
    class Meta:
        database = db


class Customer(BaseModel):
    class Meta:
        db_table = "customers"

    cust_id = TextField(primary_key=True)
    cust_name = TextField()
    cust_address = TextField()
    cust_state = TextField()
    cust_zip = TextField()
    cust_country = TextField()
    cust_contact = TextField()
    cust_email = TextField()
    cust_city = TextField()


class Vendor(BaseModel):
    class Meta:
        db_table = "vendors"

    vend_id = TextField(primary_key=True)
    vend_name = TextField(null=False)
    vend_address = TextField()
    vend_city = TextField()
    vend_state = TextField()
    vend_zip = TextField()
    vend_country = TextField()


class Product(BaseModel):
    class Meta:
        db_table = "products"

    prod_id = TextField(primary_key=True)
    vend_id = ForeignKeyField(Vendor)
    prod_name = TextField()
    prod_price = FloatField()
    prod_desc = TextField()


class Order(BaseModel):
    class Meta:
        db_table = "orders"

    order_id = TextField(primary_key=True)
    order_date = TextField()
    cust_id = ForeignKeyField(Customer)


class OrderItem(BaseModel):
    class Meta:
        db_table = "orderitems"
        primary_key = CompositeKey("order_id", "order_item")

    order_id = ForeignKeyField(Order)
    order_item = IntegerField()
    prod_id = ForeignKeyField(Product)
    quantity = IntegerField()
    item_price = FloatField()


@app.route("/customers")
def customers():
    all_customers = Customer.select()
    return render_template("customer.html", customers=all_customers)


@app.route("/orders")
def orders():
    all_orders = Order.select()
    return render_template("order.html", orders=all_orders)


@app.route("/order_items")
def order_items():
    all_order_items = OrderItem.select()
    return render_template("order_item.html", order_items=all_order_items)


@app.route("/products")
def products():
    all_products = Product.select()
    return render_template("product.html", products=all_products)


@app.route("/vendors")
def vendors():
    all_vendors = Vendor.select()
    return render_template("vendor.html", vendors=all_vendors)


@app.route("/")
def index():
    return render_template("base.html")


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    vendors = Vendor.select(Vendor.vend_id, Vendor.vend_name)
    if request.method == "GET":
        return render_template("add_product.html", vendors=vendors, product=None)

    elif request.method == "POST":
        data = request.form

        Product.create(
            prod_id=data["prod_id"],
            vend_id=data["vend_id"],
            prod_name=data["prod_name"],
            prod_price=int(data["prod_price"]),
            prod_desc=data["prod_desc"],
        )

        return redirect(url_for("products"))


@app.route("/add_vendor", methods=["GET", "POST"])
def add_vendor():
    if request.method == "GET":
        return render_template("add_vendor.html", vendor=None)

    elif request.method == "POST":
        data = request.form

        vendor = Vendor.select().where(Vendor.vend_id == data["vend_id"]).get_or_none()
        if vendor is not None:
            return render_template("add_vendor.html", error="vendor_id is exist")
        Vendor.create(
            vend_id=data["vend_id"],
            vend_name=data["vend_name"],
            vend_address=data["vend_address"],
            vend_city=data["vend_city"],
            vend_state=data["vend_state"],
            vend_zip=data["vend_zip"],
            vend_country=data["vend_country"],
        )
        return redirect(url_for("vendors"))


@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "GET":
        return render_template("add_customer.html", customers=customers, customer=None)

    elif request.method == "POST":
        data = request.form

        customer = (
            Customer.select().where(Customer.cust_id == data["cust_id"]).get_or_none()
        )
        if customer is not None:
            return render_template("add_customer.html", error="customer_id is exist")

        Customer.create(
            cust_id=data["cust_id"],
            cust_name=data["cust_name"],
            cust_address=data["cust_address"],
            cust_state=data["cust_state"],
            cust_zip=data["cust_zip"],
            cust_country=data["cust_country"],
            cust_contact=data["cust_contact"],
            cust_email=data["cust_email"],
            cust_city=data["cust_city"],
        )

        return redirect(url_for("customers"))


@app.route("/add_order_item", methods=["GET", "POST"])
def add_order_item():
    orders = Order.select(Order.order_id)
    products = Product.select(Product.prod_id, Product.prod_name)
    if request.method == "GET":
        return render_template(
            "add_order_item.html", orders=orders, products=products, order_item=None
        )

    elif request.method == "POST":
        data = request.form

        order_item = (
            OrderItem.select()
            .where(
                (OrderItem.order_id == data["order_id"])
                & (OrderItem.order_item == data["order_item"])
            )
            .get_or_none()
        )
        if order_item is not None:
            return render_template(
                "add_order_item.html",
                error="this primary key already exist",
                orders=orders,
                products=products,
            )

        OrderItem.create(
            order_id=data["order_id"],
            order_item=data["order_item"],
            prod_id=data["prod_id"],
            quantity=data["quantity"],
            item_price=data["item_price"],
        )

        return redirect(url_for("order_items"))


@app.route("/add_order", methods=["GET", "POST"])
def add_order():
    customers = Customer.select(Customer.cust_id)
    if request.method == "GET":
        return render_template("add_order.html", customers=customers, order=None)

    elif request.method == "POST":
        data = request.form

        order = Order.select().where(Order.order_id == data["order_id"]).get_or_none()
        if order is not None:
            return render_template(
                "add_order.html", error="order_id is exist", customers=customers
            )

        Order.create(
            order_id=data["order_id"],
            order_date=data["order_date"],
            cust_id=data["cust_id"],
        )

        return redirect(url_for("orders"))


@app.route("/remove_product/<prod_id>")
def remove_product(prod_id):
    product = Product.get(Product.prod_id == prod_id)
    product.delete_instance()

    return redirect(url_for("products"))


@app.route("/remove_vendor/<vend_id>")
def remove_vendor(vend_id):
    vendor = Vendor.get(Vendor.vend_id == vend_id)
    vendor.delete_instance()

    return redirect(url_for("vendors"))


@app.route("/remove_customer/<cust_id>")
def remove_customer(cust_id):
    customer = Customer.get(Customer.cust_id == cust_id)
    customer.delete_instance()

    return redirect(url_for("customers"))


@app.route("/remove_order/<order_id>")
def remove_order(order_id):
    order = Order.get(Order.order_id == order_id)
    order.delete_instance()

    return redirect(url_for("orders"))


@app.route("/remove_order_item/<order_item>/<order_id>")
def remove_order_item(order_item, order_id):
    order_item = OrderItem.get(
        (OrderItem.order_item == order_item) & (OrderItem.order_id == order_id)
    )
    order_item.delete_instance()

    return redirect(url_for("order_items"))


@app.route("/update_product/<prod_id>", methods=["GET", "POST"])
def update_product(prod_id):
    if request.method == "GET":
        product = Product.select().where(Product.prod_id == prod_id).first()
        vendors = Vendor.select(Vendor.vend_id)
        return render_template("add_product.html", product=product, vendors=vendors)

    elif request.method == "POST":
        data = request.form

        product = Product.select().where(Product.prod_id == data["prod_id"]).first()

        # product.prod_id = data["prod_id"]
        product.vend_id = data["vend_id"]
        product.prod_name = data["prod_name"]
        product.prod_price = float(data["prod_price"])
        product.prod_desc = data["prod_desc"]

        product.save()

        return redirect(url_for("products"))


@app.route("/update_vendor/<vend_id>", methods=["GET", "POST"])
def update_vendor(vend_id):
    if request.method == "GET":
        vendor = Vendor.select().where(Vendor.vend_id == vend_id).first()
        return render_template("add_vendor.html", vendor=vendor)

    elif request.method == "POST":
        data = request.form

        vendor = Vendor.select().where(Vendor.vend_id == data["vend_id"]).first()

        vendor.vend_name = data["vend_name"]
        vendor.vend_address = data["vend_address"]
        vendor.vend_city = data["vend_city"]
        vendor.vend_state = data["vend_state"]
        vendor.vend_zip = data["vend_zip"]
        vendor.vend_country = data["vend_country"]

        vendor.save()

        return redirect(url_for("vendors"))


@app.route("/update_customer/<cust_id>", methods=["GET", "POST"])
def update_customer(cust_id):
    if request.method == "GET":
        customer = Customer.select().where(Customer.cust_id == cust_id).first()
        return render_template("add_customer.html", customer=customer)

    elif request.method == "POST":
        data = request.form

        customer = Customer.select().where(Customer.cust_id == data["cust_id"]).first()

        customer.cust_name = data["cust_name"]
        customer.cust_address = data["cust_address"]
        customer.cust_state = data["cust_state"]
        customer.cust_zip = data["cust_zip"]
        customer.cust_country = data["cust_country"]
        customer.cust_contact = data["cust_contact"]
        customer.cust_email = data["cust_email"]
        customer.cust_city = data["cust_city"]

        customer.save()

        return redirect(url_for("customers"))


@app.route("/update_order/<order_id>", methods=["GET", "POST"])
def update_order(order_id):
    if request.method == "GET":
        order = Order.select().where(Order.order_id == order_id).first()
        customers = Customer.select(Customer.cust_id)
        return render_template("add_order.html", order=order, customers=customers)

    elif request.method == "POST":
        data = request.form

        order = Order.select().where(Order.order_id == data["order_id"]).first()

        order.order_id = data["order_id"]
        order.order_date = data["order_date"]
        order.cust_id = data["cust_id"]

        return redirect(url_for("orders"))


@app.route("/update_order_item/<order_item>/<order_id>", methods=["GET", "POST"])
def update_order_item(order_item, order_id):
    if request.method == "GET":
        current_order_item = (
            OrderItem.select()
            .where(
                (OrderItem.order_item == order_item) & (OrderItem.order_id == order_id)
            )
            .first()
        )
        orders = Order.select(Order.order_id)
        products = Product.select(Product.prod_id, Product.prod_name)
        return render_template(
            "add_order_item.html",
            order_item=current_order_item,
            orders=orders,
            products=products,
        )

    elif request.method == "POST":
        data = request.form

        order_item = (
            OrderItem.select()
            .where(
                (OrderItem.order_item == data["order_item"])
                & (OrderItem.order_id == data["order_id"])
            )
            .first()
        )

        order_item.order_id = data["order_id"]
        order_item.order_item = data["order_item"]
        order_item.prod_id = data["prod_id"]
        order_item.quantity = data["quantity"]
        order_item.item_price = data["item_price"]

        order_item.save()

        return redirect(url_for("order_items"))


if __name__ == "__main__":
    app.run()
