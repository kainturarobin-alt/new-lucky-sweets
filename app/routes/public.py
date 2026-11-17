import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Category, MenuItem, HotelRoom, RoomBooking, Order, OrderItem

public_bp = Blueprint('public_bp', __name__)

@public_bp.route('/')
def index():
    sweets_popular = MenuItem.query.filter_by(wing='sweets', is_popular=True, is_available=True).limit(6).all()
    restaurant_popular = MenuItem.query.filter_by(wing='restaurant', is_popular=True, is_available=True).limit(6).all()
    hotel_rooms = HotelRoom.query.all()
    return render_template(
        'index.html',
        sweets_popular=sweets_popular,
        restaurant_popular=restaurant_popular,
        hotel_rooms=hotel_rooms
    )

@public_bp.route('/products')
@public_bp.route('/sweets')
def products():
    categories = Category.query.filter_by(wing='sweets').order_by(Category.sort_order).all()
    items = MenuItem.query.filter_by(wing='sweets', is_available=True).all()
    return render_template('products.html', categories=categories, items=items)

@public_bp.route('/restaurant')
def restaurant():
    categories = Category.query.filter_by(wing='restaurant').order_by(Category.sort_order).all()
    items = MenuItem.query.filter_by(wing='restaurant', is_available=True).all()
    return render_template('restaurant.html', categories=categories, items=items)

@public_bp.route('/hotel')
def hotel():
    rooms = HotelRoom.query.all()
    return render_template('hotel.html', rooms=rooms)

@public_bp.route('/track', methods=['GET', 'POST'])
def track_order_search():
    if request.method == 'POST':
        order_num = request.form.get('order_number', '').strip().upper()
        if order_num:
            return redirect(url_for('public_bp.track_order_view', order_number=order_num))
        flash('Please enter a valid Order Number.', 'warning')
    return render_template('track_order.html', order=None)

@public_bp.route('/track/<order_number>')
def track_order_view(order_number):
    order = Order.query.filter_by(order_number=order_number).first()
    return render_template('track_order.html', order=order, searched_number=order_number)

@public_bp.route('/order/<order_number>')
def order_detail(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_receipt.html', order=order)

@public_bp.route('/api/order/submit', methods=['POST'])
def submit_order():
    data = request.get_json() or {}
    items_data = data.get('items', [])
    if not items_data:
        return jsonify({'success': False, 'message': 'Cart is empty. Please add items to place an order.'}), 400

    order_num = f"NL-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    cust_name = data.get('customer_name', 'Guest Customer')
    cust_phone = data.get('customer_phone', '')
    wing = data.get('wing', 'sweets')
    order_type = data.get('order_type', 'takeaway')
    table_or_room = data.get('table_or_room', '')
    payment_mode = data.get('payment_mode', 'Cash on Counter')
    notes = data.get('notes', '')

    total = 0.0
    order_items_objs = []
    whatsapp_lines = [
        f"👑 *NEW LUCKY GROUP - OFFICIAL ORDER RECEIPT*",
        f"📜 *Order Reference:* {order_num}",
        f"👤 *Customer:* {cust_name} ({cust_phone})",
        f"🏷️ *Department:* {wing.capitalize()} ({order_type.capitalize()})",
    ]
    if table_or_room:
        whatsapp_lines.append(f"📍 *Table / Room:* {table_or_room}")
    whatsapp_lines.append("───────────────────────")
    whatsapp_lines.append("*ITEMS ORDERED:*")

    for item_data in items_data:
        qty = float(item_data.get('quantity', 1))
        price = float(item_data.get('price', 0))
        unit = item_data.get('unit', 'item')
        item_name = item_data.get('name', 'Menu Item')
        line_total = round(qty * price, 2)
        total += line_total

        order_items_objs.append(
            OrderItem(
                item_name=item_name,
                quantity=qty,
                unit=unit,
                price=price,
                total=line_total
            )
        )
        whatsapp_lines.append(f"▪ {item_name} × {qty} {unit} = ₹{line_total:.0f}")

    whatsapp_lines.append("───────────────────────")
    whatsapp_lines.append(f"💰 *TOTAL BILL: ₹{total:.0f}*")
    whatsapp_lines.append(f"💳 *Payment Mode:* {payment_mode}")
    whatsapp_lines.append(f"🔍 *Live Order Track:* http://127.0.0.1:5000/track/{order_num}")
    if notes:
        whatsapp_lines.append(f"📝 *Instructions:* {notes}")
    whatsapp_lines.append("\n📍 *New Lucky Sweets, Restaurant & Hotel Residency, Miyawala Chowk, Dehradun*")

    order = Order(
        order_number=order_num,
        customer_name=cust_name,
        customer_phone=cust_phone,
        wing=wing,
        order_type=order_type,
        table_or_room=table_or_room,
        total_amount=total,
        discount=0.0,
        final_amount=total,
        status='pending',
        payment_mode=payment_mode,
        payment_status='Pending' if payment_mode != 'Cash' else 'Unpaid',
        notes=notes
    )
    db.session.add(order)
    db.session.flush()

    for oi in order_items_objs:
        oi.order_id = order.id
        db.session.add(oi)

    db.session.commit()

    import urllib.parse
    whatsapp_text = urllib.parse.quote("\n".join(whatsapp_lines))
    whatsapp_url = f"https://wa.me/919412153429?text={whatsapp_text}"

    return jsonify({
        'success': True,
        'order_number': order_num,
        'total': total,
        'whatsapp_url': whatsapp_url,
        'view_url': url_for('public_bp.track_order_view', order_number=order_num)
    })

@public_bp.route('/api/booking/submit', methods=['POST'])
def submit_booking():
    data = request.get_json() or {}
    room_id = data.get('room_id')
    guest_name = data.get('guest_name')
    guest_phone = data.get('guest_phone')
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')
    num_guests = int(data.get('num_guests', 2))

    if not all([room_id, guest_name, guest_phone, check_in_str, check_out_str]):
        return jsonify({'success': False, 'message': 'Please fill all required booking details.'}), 400

    room = HotelRoom.query.get_or_404(room_id)
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d')
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d')
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid date format.'}), 400

    days = max(1, (check_out - check_in).days)
    total = room.price_per_night * days
    booking_num = f"NLR-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

    booking = RoomBooking(
        booking_number=booking_num,
        room_id=room.id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        check_in=check_in,
        check_out=check_out,
        num_guests=num_guests,
        total_amount=total,
        advance_paid=0.0,
        status='inquiry'
    )
    db.session.add(booking)
    db.session.commit()

    msg = (
        f"🏨 *HOTEL NEW LUCKY RESIDENCY - ROOM RESERVATION*\n"
        f"📜 *Booking Ref:* {booking_num}\n"
        f"👤 *Guest Name:* {guest_name} ({guest_phone})\n"
        f"🛏️ *Room:* {room.room_type} (Room {room.room_number})\n"
        f"📅 *Dates:* {check_in_str} to {check_out_str} ({days} Nights)\n"
        f"👥 *Number of Guests:* {num_guests}\n"
        f"💰 *Estimated Total:* ₹{total:.0f}\n"
        f"📍 *Location:* Miyawala Chowk / Gularghati Rd, Dehradun"
    )
    import urllib.parse
    whatsapp_url = f"https://wa.me/919412153429?text={urllib.parse.quote(msg)}"

    return jsonify({
        'success': True,
        'booking_number': booking_num,
        'total': total,
        'days': days,
        'whatsapp_url': whatsapp_url
    })
