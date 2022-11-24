from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from openmarket.models import User
    from openmarket.forms import FlaskForm


def edit_user(user: User, form: FlaskForm):
    for attr in user.__dict__:
        if not hasattr(form, attr) or attr.startswith("_"):
            continue
        value = getattr(form, attr).data
        print(f"Editing user attribute {attr} to {value}")
        setattr(user, attr, value)


def load_form(form: FlaskForm, user: User):
    """Change fields' value from an user."""
    for attr in form.__dict__:
        if not hasattr(user, attr) or attr.startswith("_"):
            continue
        value = getattr(user, attr)

        print(f"Setting form attribute {attr} to {value}")
        getattr(form, attr).data = value


def make_class_string(*args: str) -> str:
    return " ".join([c.strip() for c in args])


def format_date(date: datetime) -> str:
    local = date.astimezone().now()
    return local.strftime("%d-%m-%y")


def format_price(price: float) -> str:
    temp = "{:.2f}".format(price)
    return temp.replace(".", ",")
