from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    EmailField,
    PasswordField,
    TextAreaField,
    IntegerField,
    DecimalField,
    BooleanField,
    TelField,
    DateField,
    SelectField,
    Label,
    widgets,
)
from markupsafe import Markup, escape
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from sqlalchemy import func
from flask_login import current_user

from openmarket import db
from openmarket.models import User


class CheckboxLabel(Label):
    def __call__(self, field=None, text=None, **kwargs):
        if "for_" in kwargs:
            kwargs["for"] = kwargs.pop("for_")
        else:
            kwargs.setdefault("for", self.field_id)

        attributes = widgets.html_params(**kwargs)
        text = escape(text or self.text)
        return Markup("<label %s>%s\n%s</label>" % (attributes, field, text))


class CheckboxField(BooleanField):
    def __init__(self, label=None, validators=None, false_values=None, **kwargs):
        super().__init__(label, validators, false_values, **kwargs)
        self.label = CheckboxLabel(self.id, label)


class SearchForm(FlaskForm):
    keyword = StringField("Keyword", validators=[DataRequired()])


class AdvancedSearchForm(FlaskForm):
    keyword = StringField("Keyword")
    username = StringField("Username")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=60)])
    remember_me = CheckboxField("Remember Me", default=False)

    def validate(self, extra_validators=None) -> bool:
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False

        user: User = db.session.execute(
            db.select(User).where(func.lower(User.email) == func.lower(self.email.data))
        ).scalar()

        if not user:
            self.email.errors.append("Email not found")
            return False

        if user.password != self.password.data:
            self.password.errors.append("Invalid password")
            return False

        return True


class RegisterForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=60)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=25)])
    display_name = StringField("Display Name", validators=[DataRequired(), Length(min=3, max=120)])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), Length(min=8, max=60), EqualTo("password")]
    )
    phone = TelField("Cellphone", validators=[DataRequired()])

    def validate(self, extra_validators=None):
        initial_validation = super().validate(extra_validators)
        if not initial_validation:
            return False

        user = db.session.execute(
            db.select(User).where(func.lower(User.username) == func.lower(self.username.data))
        ).scalar()
        if user:
            self.username.errors.append("Username already exists")
            return False

        user = db.session.execute(
            db.select(User).where(func.lower(User.email) == func.lower(self.email.data))
        ).scalar()
        if user:
            self.email.errors.append("Email already exists")
            return False

        if not self.phone.data.isnumeric():
            self.phone.errors.append("You can't type letters.")
            return False

        return True


class EditProfileForm(FlaskForm):
    # birthday = DateField("Birthday", validators=[Optional()])
    # gender = SelectField(
    #     "Gender",
    #     choices=[
    #         ("", "Select a gender"),
    #         ("male", "Male"),
    #         ("female", "Female"),
    #         ("other", "Other"),
    #         ("n/a", "Prefer not to say"),
    #     ],
    # )
    location = StringField("Location")
    bio = TextAreaField("Biography")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=8, max=60)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(min=8, max=60),
            EqualTo("new_password", "Field must be equal to New Password"),
        ],
    )

    def validate(self, extra_validators=None):
        initial = super().validate(extra_validators)
        if not initial:
            print("Failed initial validation!")
            print(self.current_password.data, self.current_password.errors)
            print(self.new_password.data, self.new_password.errors)
            print(self.confirm_password.data, self.confirm_password.errors)
            return False

        if self.new_password == current_user.password:
            self.new_password.errors.append("New password cannot be equal to current password.")
            return False

        if current_user.password != self.current_password.data:
            self.current_password.errors.append("Invalid password.")
            return False

        return True


class ChangeUsernameForm(FlaskForm):
    new_username = StringField("New Username")
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=60)])

    def validate(self, extra_validators=None):
        initial = super().validate(extra_validators)
        if not initial:
            return False

        # O usuário não pode existir.
        user = db.session.execute(
            db.select(User).where(User.username == self.new_username.data)
        ).scalar()
        if user:
            self.new_username.errors.append("Username already exists")
            return False

        # A senha precisa estar correta.
        if self.password.data != current_user.password:
            self.password.errors.append("Invalid password")
            return False

        return True


class ChangeEmailForm(FlaskForm):
    new_email = EmailField("New Email")
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=60)])

    def validate(self, extra_validators=None):
        initial = super().validate(extra_validators)
        if not initial:
            return False

        # Não pode existir um usuário com o mesmo email
        user = db.session.execute(
            db.select(User).where(func.lower(User.email) == func.lower(self.new_email.data))
        ).scalar()
        if user:
            self.new_email.errors.append("Username already exists")
            return False

        # A senha precisa estar correta
        if self.password.data != current_user.password:
            self.password.errors.append("Invalid password")
            return False

        return True


class AddProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()], default=1)
    price = DecimalField("Price Per Unit", validators=[DataRequired()])


class EditProductForm(AddProductForm):
    pass
