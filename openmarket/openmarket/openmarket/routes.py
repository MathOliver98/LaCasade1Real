from flask import render_template, flash, redirect, url_for, request, abort, jsonify, Response

from flask_login import login_user, logout_user, login_required, current_user

from openmarket import app, db
from openmarket.forms import (
    SearchForm,
    LoginForm,
    RegisterForm,
    AdvancedSearchForm,
    AddProductForm,
    EditProfileForm,
    ChangePasswordForm,
    ChangeUsernameForm,
    ChangeEmailForm,
    EditProductForm,
)
from openmarket.models import User, Product, Favorites
from openmarket.utils import edit_user, load_form


@app.route("/home")
@app.route("/index")
@app.route("/", methods=["GET", "POST"])
def index():
    # flash("You have entered the index page!", "primary")
    # if request.method == "POST":
    #     username = request.form.get("username")
    #     query = (
    #         db.select(Product)
    #         .join(Product.seller)
    #         .where(User.username == username)
    #         .where(Product.is_pending.is_(False))
    #         .where(Product.is_rejected.is_(False))
    #     )
    # else:
    #     query = (
    #         db.select(Product)
    #         .where(Product.is_pending.is_(False))
    #         .where(Product.is_rejected.is_(False))
    #     )

    # products = db.session.execute(query).scalars().all()
    # print(products)
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for("index"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User(
            username=form.username.data,
            display_name=form.display_name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created with success!", "success")
        return redirect(request.args.get("next") or url_for("index"))
    elif form.is_submitted():
        flash("Problems occurred when creating your account!", "danger")

    return render_template("register.html", form=form)


@app.route("/products")
def products():
    search_form = SearchForm()
    advanced_search_form = AdvancedSearchForm()
    edit_form = EditProductForm()

    keyword = request.args.get("keyword")
    username = request.args.get("username")
    if keyword and username:
        query = (
            db.select(Product)
            .join(Product.seller)
            .where(User.username == username)
            .where(Product.name.like(f"%{keyword}%"))
            .where(Product.is_pending.is_(False))
            .where(Product.is_rejected.is_(False))
        )

    elif keyword:
        query = (
            db.select(Product)
            .where(Product.name.like(f"%{keyword}%"))
            .where(Product.is_pending.is_(False))
            .where(Product.is_rejected.is_(False))
        )

    elif username:
        query = (
            db.select(Product)
            .join(Product.seller)
            .where(User.username == username)
            .where(Product.is_pending.is_(False))
            .where(Product.is_rejected.is_(False))
        )

    else:
        query = (
            db.select(Product)
            .where(Product.is_pending.is_(False))
            .where(Product.is_rejected.is_(False))
        )

    products = db.session.execute(query).scalars().all()

    return render_template(
        "products.html",
        form=search_form,
        adv_form=advanced_search_form,
        edit_form=edit_form,
        products=products,
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(request.args.get("next") or url_for("index"))


@app.route("/account/delete", methods=["POST"])
@login_required
def delete_account():
    # Deleta os produtos do usuário
    for product in current_user.products:
        db.session.delete(product)

    # Delete o usuário em si
    db.session.delete(current_user)
    db.session.commit()

    # Desloga o usuário
    logout_user()

    # Cria a notificação e redireciona o usuário
    flash("You account has been deleted", "warning")
    return redirect(request.args.get("next") or url_for("index"))


@app.route("/products/<int:id>")
def product(id):
    product: Product = db.session.execute(db.select(Product).where(Product.id == id)).scalar()

    # Se a URL for '/products/1?json=true', printa os dados do produto em formato JSON
    json = request.args.get("json")
    if json:
        return jsonify(product.as_dict())

    return redirect(request.args.get("next") or url_for("products"))


@app.route("/products/<int:id>/favorite", methods=["POST"])
@login_required
def favorite_product(id):
    if current_user.has_liked(id):
        db.session.execute(db.delete(Favorites).where(Favorites.user_id == current_user.id))
    else:
        favorite = Favorites(user_id=current_user.id, product_id=id)
        db.session.add(favorite)

    db.session.commit()
    return Response(status=200)


@app.route("/user/<int:id>")
def profile(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    if current_user.is_authenticated and current_user.is_admin:
        return render_template("user/profile/profile.html", user=user)
    if user and not user.is_admin:
        return render_template("user/profile/profile.html", user=user)

    abort(404)


@app.route("/user/<username>")
def profile_username(username):
    user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    if not user:
        abort(404)
    return redirect(url_for("profile", id=user.id))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = EditProfileForm()
    if request.method == "GET":
        load_form(form, current_user)

    if form.validate_on_submit():
        # form.populate_obj(current_user)
        edit_user(current_user, form)
        db.session.commit()
        flash("Profile updated successfully", "success")

    return render_template("user/account/account.html", form=form)


@app.route("/account/edit/password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.new_password.data
        db.session.commit()
        flash("Account updated with success!", "success")

    return render_template("user/account/change_password.html", form=form)


@app.route("/account/edit/email", methods=["GET", "POST"])
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_user.email = form.new_email.data
        db.session.commit()
        flash("Account updated with success!", "success")

    return render_template("user/account/change_email.html", form=form)


@app.route("/account/edit/username", methods=["GET", "POST"])
def change_username():
    form = ChangeUsernameForm()
    if form.validate_on_submit():
        current_user.username = form.new_username.data
        db.session.commit()
        flash("Account updated with success!", "success")

    return render_template("user/account/change_username.html", form=form)


@app.route("/products/<int:id>/delete", methods=["POST"])
@login_required
def delete_product(id):
    p = db.session.execute(db.select(Product).where(Product.id == id)).scalar()
    if not p:
        abort(404)

    db.session.delete(p)
    db.session.commit()
    flash("Product deleted successfully.", "success")

    return redirect(request.args.get("next") or url_for("products"))


@app.route("/products/<int:id>/edit", methods=["POST"])
@login_required
def edit_product(id):
    product: Product = db.session.execute(db.select(Product).where(Product.id == id)).scalar()
    if not product:
        abort(404)

    form = EditProductForm()
    if form.validate_on_submit():
        edit_user(product, form)
        if not product.is_pending and not product.is_rejected:
            product.is_pending = True
        elif product.is_rejected:
            product.is_rejected = False
            product.is_pending = True

        db.session.commit()
        flash("Product updated succesfully.", "success")

    return redirect(request.args.get("next") or url_for("products"))


@app.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    form = AddProductForm()
    if request.method == "POST" and form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data.strip(),
            quantity=form.quantity.data,
            price=form.price.data,
            seller=current_user,
            seller_id=current_user.id,
        )

        db.session.add(product)
        db.session.commit()
        flash(f"Added product {product.name}", "success")
        return redirect(request.args.get("next") or url_for("products"))
    elif form.is_submitted():
        flash("Problems occurred when adding your product!", "danger")

    return render_template("products/add.html", form=form)


@app.route("/pending/")
@login_required
def admin_pending():
    if not current_user.is_admin:
        abort(403)

    form = SearchForm()
    username = request.args.get("keyword")
    if username:
        query = (
            db.select(Product)
            .join(Product.seller)
            .where(User.username == username)
            .where(Product.is_pending.is_(True))
        )
    else:
        query = db.select(Product).where(Product.is_pending.is_(True))

    products = db.session.execute(query).scalars()
    return render_template("admin/pending.html", products=products, form=form)


@app.route("/pending/<int:id>/accept")
@login_required
def accept_product(id):
    if not current_user.is_admin:
        abort(403)

    product = db.session.execute(db.select(Product).where(Product.id == id)).scalar()
    if not product:
        abort(404)

    product.is_pending = False
    db.session.commit()
    flash("Product accepted!", "success")
    return redirect(request.args.get("next") or url_for("pending"))


@app.route("/pending/<int:id>/reject")
@login_required
def reject_product(id):
    if not current_user.is_admin:
        abort(403)

    product = db.session.execute(db.select(Product).where(Product.id == id)).scalar()
    if not product:
        abort(404)

    product.is_pending = False
    product.is_rejected = True
    db.session.commit()

    flash("Product rejected!", "success")
    return redirect(request.args.get("next") or url_for("pending"))


@app.route("/user/<int:id>/products", methods=["GET", "POST"])
def profile_products(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    if not user:
        abort(404)

    products = [p for p in user.products if not p.is_pending and not p.is_rejected]
    edit_form = EditProductForm()
    return render_template(
        "user/profile/products.html", user=user, edit_form=edit_form, products=products
    )


@app.route("/user/<int:id>/favorites", methods=["GET"])
def user_favorites(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    if not user:
        abort(404)

    products = (
        db.session.execute(
            db.select(Product)
            .join(Favorites)
            .where(Favorites.user_id == id)
            .where(Product.is_pending.is_(False))
            .where(Product.is_rejected.is_(False))
        )
        .scalars()
        .all()
    )

    return render_template("user/profile/favorites.html", user=user, products=products)


@app.route("/user/<int:id>/pending", methods=["GET", "POST"])
def profile_pending(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    if not user:
        abort(404)

    products = [p for p in user.products if p.is_pending and not p.is_rejected]
    edit_form = EditProductForm()
    return render_template(
        "user/profile/pending.html", user=user, edit_form=edit_form, products=products
    )


@app.route("/user/<int:id>/rejected", methods=["GET", "POST"])
def profile_rejected(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    if not user:
        abort(404)

    products = [p for p in user.products if p.is_rejected and not p.is_pending]
    edit_form = EditProductForm()
    return render_template(
        "user/profile/rejected.html", user=user, edit_form=edit_form, products=products
    )
