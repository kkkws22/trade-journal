"""Forms for the trading journal application.

This module defines Flask-WTF forms for user registration, login, and
recording trades. The trade form captures details needed to log a
transaction, including prices, quantities, notes, emotions and
rule adherence.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, EqualTo, NumberRange


class RegistrationForm(FlaskForm):
    """Form for registering a new user."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")]
    )
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    """Form for logging in an existing user."""
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class TradeForm(FlaskForm):
    """Form for recording a trade."""
    symbol = StringField("Symbol", validators=[DataRequired()])
    market = StringField("Market", validators=[DataRequired()])
    direction = SelectField(
        "Direction",
        choices=[("long", "Long"), ("short", "Short")],
        validators=[DataRequired()],
    )
    entry_price = FloatField("Entry Price", validators=[DataRequired()])
    exit_price = FloatField("Exit Price")
    quantity = FloatField("Quantity", validators=[DataRequired()])
    stop_loss = FloatField("Stop Loss")
    take_profit = FloatField("Take Profit")
    fees = FloatField("Fees")
    risk = FloatField("Planned Risk", validators=[DataRequired()])
    notes = TextAreaField("Notes")
    emotions = TextAreaField("Emotions")
    rule_adherence = IntegerField(
        "Rule Adherence (1-5)", validators=[NumberRange(min=1, max=5)], default=5
    )
    submit = SubmitField("Save Trade")
