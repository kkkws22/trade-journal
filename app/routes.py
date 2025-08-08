"""Routes for the trading journal application."""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import User, Trade
from .forms import RegistrationForm, LoginForm, TradeForm

# Blueprint for route definitions
main = Blueprint("main", __name__)


@main.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username already exists
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists", "danger")
            return redirect(url_for("main.register"))
        # Create the user and hash the password
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            # Redirect to next page if available
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@main.route("/logout")
@login_required
def logout():
    """Log the user out and redirect to the login page."""
    logout_user()
    return redirect(url_for("main.login"))


@main.route("/")
@login_required
def index():
    """Display the dashboard with a summary of trades."""
    trades = (
        Trade.query.filter_by(user_id=current_user.id)
        .order_by(Trade.timestamp.desc())
        .all()
    )
    # Calculate metrics
    net_pl = sum((t.pl() or 0) for t in trades)
    win_count = len([t for t in trades if (t.pl() or 0) > 0])
    loss_count = len([t for t in trades if (t.pl() or 0) < 0])
    return render_template(
        "dashboard.html",
        trades=trades,
        net_pl=net_pl,
        win_count=win_count,
        loss_count=loss_count,
    )


@main.route("/trade/new", methods=["GET", "POST"])
@login_required
def new_trade():
    """Create a new trade entry."""
    form = TradeForm()
    if form.validate_on_submit():
        trade = Trade(
            user_id=current_user.id,
            symbol=form.symbol.data,
            market=form.market.data,
            direction=form.direction.data,
            entry_price=form.entry_price.data,
            exit_price=form.exit_price.data,
            quantity=form.quantity.data,
            stop_loss=form.stop_loss.data,
            take_profit=form.take_profit.data,
            fees=form.fees.data,
            risk=form.risk.data,
            notes=form.notes.data,
            emotions=form.emotions.data,
            rule_adherence=form.rule_adherence.data,
        )
        db.session.add(trade)
        db.session.commit()
        flash("Trade saved", "success")
        return redirect(url_for("main.index"))
    return render_template("trade_form.html", form=form)


@main.route("/trade/<int:trade_id>/edit", methods=["GET", "POST"])
@login_required
def edit_trade(trade_id: int):
    """Edit an existing trade."""
    trade = Trade.query.get_or_404(trade_id)
    if trade.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("main.index"))
    form = TradeForm(obj=trade)
    if form.validate_on_submit():
        form.populate_obj(trade)
        db.session.commit()
        flash("Trade updated", "success")
        return redirect(url_for("main.index"))
    return render_template("trade_form.html", form=form, trade=trade)


@main.route("/trade/<int:trade_id>/delete", methods=["POST"])
@login_required
def delete_trade(trade_id: int):
    """Delete a trade."""
    trade = Trade.query.get_or_404(trade_id)
    if trade.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for("main.index"))
    db.session.delete(trade)
    db.session.commit()
    flash("Trade deleted", "success")
    return redirect(url_for("main.index"))
