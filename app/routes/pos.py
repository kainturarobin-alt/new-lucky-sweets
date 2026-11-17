import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app import db
from app.models import MenuItem, Category, Order, OrderItem, HotelRoom

pos_bp = Blueprint('pos_bp', __name__)

@pos_bp.route('/')
@login_required
def index():
    sweets_items = MenuItem.query.filter_by(wing='sweets', is_available=True).all()
    rest_items = MenuItem.query.filter_by(wing='restaurant', is_available=True).all()
    hotel_rooms = HotelRoom.query.all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(15).all()
    return render_template(
        'pos/index.html',
        sweets_items=sweets_items,
        rest_items=rest_items,
        hotel_rooms=hotel_rooms,
        recent_orders=recent_orders
    )

@pos_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json() or {}
    cart_items = data.get('cart', [])
    if not cart_items:
        return jsonify({'success': False, 'message': 'No items in POS cart.'}), 400

    order_num = f"POS-{datetime.utcnow().strftime('%y%m%d%H%M')}-{uuid.uuid4().hex[:3].upper()}"
    cust_name = data.get('customer_name') or 'Counter Walk-in'
    cust_phone = data.get('customer_phone') or ''
    payment_mode = data.get('payment_mode') or 'Cash'
    wing = data.get('wing') or 'sweets'
    order_type = data.get('order_type') or 'takeaway'
    table_or_room = data.get('table_or_room') or ''
    discount = float(data.get('discount') or 0.0)

    subtotal = 0.0
    order_items_objs = []
    for item in cart_items:
        qty = float(item.get('qty', 1))
        price = float(item.get('price', 0))
        unit = item.get('unit', 'pc')
        name = item.get('name', 'Item')
        item_id = item.get('id')
        total = round(qty * price, 2)
        subtotal += total

        order_items_objs.append(
            OrderItem(
                item_id=item_id,
                item_name=name,
                quantity=qty,
                unit=unit,
                price=price,
                total=total
            )
        )

    final_total = max(0.0, subtotal - discount)
    order = Order(
        order_number=order_num,
        customer_name=cust_name,
        customer_phone=cust_phone,
        wing=wing,
        order_type=order_type,
        table_or_room=table_or_room,
        total_amount=subtotal,
        discount=discount,
        final_amount=final_total,
        status='completed',
        payment_mode=payment_mode,
        payment_status='Paid',
        notes=f"Billed from {wing.replace('_', ' ').capitalize()} POS Terminal"
    )
    db.session.add(order)
    db.session.flush()

    for oi in order_items_objs:
        oi.order_id = order.id
        db.session.add(oi)

    db.session.commit()

    return jsonify({
        'success': True,
        'order_number': order_num,
        'order_id': order.id,
        'total': final_total,
        'print_url': f"/order/{order_num}"
    })
