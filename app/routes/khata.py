from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import KhataCustomer, KhataTransaction

khata_bp = Blueprint('khata_bp', __name__)

@khata_bp.route('/')
@login_required
def index():
    customers = KhataCustomer.query.order_by(KhataCustomer.current_balance.desc()).all()
    total_receivable = sum(c.current_balance for c in customers if c.current_balance > 0)
    total_daily_milk = sum(c.daily_milk_qty for c in customers if c.status == 'active')
    return render_template(
        'khata/index.html',
        customers=customers,
        total_receivable=total_receivable,
        total_daily_milk=total_daily_milk
    )

@khata_bp.route('/customer/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = KhataCustomer.query.get_or_404(customer_id)
    txns = KhataTransaction.query.filter_by(customer_id=customer.id).order_by(KhataTransaction.created_at.desc()).all()
    return render_template('khata/detail.html', customer=customer, txns=txns)

@khata_bp.route('/add-customer', methods=['POST'])
@login_required
def add_customer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    address = request.form.get('address', '')
    daily_qty = float(request.form.get('daily_milk_qty', 1.0))
    rate = float(request.form.get('milk_rate', 66.0))
    initial_balance = float(request.form.get('initial_balance', 0.0))

    if name and phone:
        cust = KhataCustomer(
            name=name,
            phone=phone,
            address=address,
            daily_milk_qty=daily_qty,
            milk_rate=rate,
            current_balance=initial_balance
        )
        db.session.add(cust)
        db.session.commit()
        flash(f"Customer {name} added to Dairy Ledger.", "success")
    return redirect(url_for('khata_bp.index'))

@khata_bp.route('/add-entry', methods=['POST'])
@login_required
def add_entry():
    customer_id = int(request.form.get('customer_id'))
    txn_type = request.form.get('txn_type', 'milk_daily')
    qty = float(request.form.get('quantity', 1.0))
    amount = float(request.form.get('amount', 0.0))
    description = request.form.get('description', '')

    cust = KhataCustomer.query.get_or_404(customer_id)
    if txn_type == 'payment_received':
        cust.current_balance -= amount
    else:
        cust.current_balance += amount

    txn = KhataTransaction(
        customer_id=cust.id,
        date=date.today(),
        txn_type=txn_type,
        description=description or ('Payment Received' if txn_type == 'payment_received' else f"{qty}L Milk Entry"),
        quantity=qty,
        amount=-amount if txn_type == 'payment_received' else amount,
        balance_after=cust.current_balance
    )
    db.session.add(txn)
    db.session.commit()
    flash("Ledger entry recorded successfully.", "success")
    return redirect(url_for('khata_bp.customer_detail', customer_id=customer_id))
