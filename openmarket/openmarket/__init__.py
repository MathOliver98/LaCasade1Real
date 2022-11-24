from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin

# from flask_ckeditor import CKEditor

from openmarket.utils import make_class_string, format_date, format_price

# Setup app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SECRET_KEY"] = "585224dad262c1667710dd7378a96b8cbbc438c378ed87675ee3470d1c2f78af"

# Extensions
db = SQLAlchemy(app)

login_manager = LoginManager(app)
admin = Admin(app)
# ckeditor = CKEditor(app)

# Add functions to jinja templates
app.jinja_env.globals.update(make_class_string=make_class_string)
app.jinja_env.globals.update(format_date=format_date)
app.jinja_env.globals.update(format_price=format_price)

from openmarket import routes, models  # noqa

# Para iniciar o servidor 
# flask --app openmarket --debug run
