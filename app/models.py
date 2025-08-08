"""
Database models for the trading journal.

This module defines the `User` and `Trade` models. Users can register and log
in, and each user can record multiple trades. Trades store details about
individual trades and offer convenience methods for calculating profit/loss
and risk multiples.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    """Model representing a registered user of the journal."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    trades = db.relationship('Trade', backref='user', lazy=True)

    def set_password(self, password: str) -> None:
        """Hashes and stores a plaintext password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check a plaintext password against the stored hash."""
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))


class Trade(db.Model):
    """Model representing a single trade recorded by a user."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    symbol = db.Column(db.String(32), nullable=False)
    market = db.Column(db.String(64), nullable=True)
    direction = db.Column(db.String(8), nullable=False)  # Long or Short
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=True)
    take_profit = db.Column(db.Float, nullable=True)
    fees = db.Column(db.Float, nullable=True)
    risk = db.Column(db.Float, nullable=True)  # Planned risk amount in currency
    notes = db.Column(db.Text, nullable=True)
    emotions = db.Column(db.Text, nullable=True)
    rule_adherence = db.Column(db.Integer, nullable=True)  # 1–5 scale

    def pl(self) -> float | None:
        """Calculate the profit or loss for the trade (fees deducted)."""
        if self.exit_price is None:
            return None
        # Determine profit based on trade direction.
        price_diff = (
            (self.exit_price - self.entry_price)
            if self.direction.lower() == 'long'
            else (self.entry_price - self.exit_price)
        )
        pnl = price_diff * self.quantity
        if self.fees:
            pnl -= self.fees
        return pnl

    def r_multiple(self) -> float | None:
        """Calculate the trade's R-multiple based on the planned risk."""
        if not self.risk:
            return None
        pl_value = self.pl()
        if pl_value is None or self.risk == 0:
            return None
        return pl_value / self.risk
