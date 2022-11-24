from datetime import datetime

from flask_login import UserMixin
from flask_admin.contrib.sqla import ModelView

from flask_sqlalchemy.model import DefaultMeta

from openmarket import app, db, login_manager, admin

# Arruma o erro do tipo 'db.Model' ser inválido.
BaseModel: DefaultMeta = db.Model


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


class Base(BaseModel):
    __abstract__ = True

    created = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    modified = db.Column(
        db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now()
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(Base, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    display_name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    bio = db.Column(db.String, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    phone = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=True, default=None)
    birthday = db.Column(db.Date, nullable=True)
    location = db.Column(db.String, nullable=True)
    products = db.relationship("Product", back_populates="seller")
    favorites = db.relationship("Favorites")

    def __repr__(self) -> str:
        return f"User(username='{self.username}')"

    def has_liked(self, product_id: int) -> bool:
        favorite = db.session.execute(
            db.select(Favorites).where(
                (Favorites.user_id == self.id) & (Favorites.product_id == product_id)
            )
        ).scalar()
        if favorite:
            return True
        return False


class Product(Base):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    is_pending = db.Column(db.Boolean, default=True, nullable=False)
    is_rejected = db.Column(db.Boolean, default=False, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    seller = db.relationship("User", back_populates="products")
    favorites = db.relationship("Favorites")

    def __repr__(self) -> str:
        return f"Product(name='{self.name}', Seller='{self.seller}')"


class Favorites(Base):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))


with app.app_context():
    # Apaga as tabelas do banco
    db.drop_all()

    # Cria as tabelas do banco
    db.create_all()

    # Usuário de administrador.
    # Talvez não tenha sentido o admin usar a mesma tabela de usuários.
    u1 = User(
        username="admin",
        display_name="OpenMarket Admin",
        email="admin@openmarket.com",
        password="admin123",
        is_admin=True,
        phone="11912341234",
    )

    u2 = User(
        username="teste",
        display_name="teste",
        email="teste@gmail.com",
        password="teste123",
        is_admin=False,
        phone="11912341234",
    )

    u3 = User(
        username="john",
        display_name="John Smith",
        email="john@gmail.com",
        password="john1234",
        is_admin=False,
        phone="11912341234",
        birthday=datetime.strptime("1992/10/04", "%Y/%m/%d"),
        gender="Male",
    )

    p1 = Product(
        name="Caixa de Bis 126g Chocolate",
        description="Uma deliciosa caixa de bis, um dos melhores doces do universo. Fonte: confia.",
        quantity=10,
        price=4,
        seller=u2,
    )

    p2 = Product(
        name="O segundo produto",
        description="Outro maravilhoso produto, porém com uma descrição um pouco maior!!",
        quantity=1,
        price=9,
        seller=u2,
    )

    p3 = Product(
        name="Produto super barato!!!",
        description="Sem descrições, pois um produto barato e de qualidade fala por si próprio!",
        quantity=12,
        price=2.5,
        seller=u3,
        is_pending=False,
    )

    p4 = Product(
        name="Um produto com um nome extremamente longo para testar a responsividade do site com base nos diferentes tamanhos de nomes.",
        description="Um lindo e maravilhoso produto com uma simples descrição!!",
        quantity=3,
        price=2.5,
        seller=u3,
    )

    p5 = Product(
        name="O quinto produto",
        description="Outro belíssimo e maravilhoso produto.",
        quantity=6,
        price=12.75,
        seller=u2,
        is_pending=False,
    )

    p6 = Product(
        name="O sexto produto",
        description="Um produto super caro!",
        quantity=4,
        price=1120,
        seller=u2,
    )

    # Adiciona os usuários
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)

    # Adiciona os produtos.
    db.session.add(p1)
    db.session.add(p2)
    db.session.add(p3)
    db.session.add(p4)
    db.session.add(p5)
    db.session.add(p6)

    # Confirma as mudanças no banco, sem isso nada acontece.
    db.session.commit()


admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Product, db.session))
