from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, MenuItem, Category, Order, OrderItem, HotelRoom, RoomBooking, KhataCustomer, KhataTransaction

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.full_name}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.dashboard'))
        flash('Invalid username or password. Access denied.', 'danger')

    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('public_bp.index'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Overall multi-business metrics
    sweets_orders = Order.query.filter_by(wing='sweets').all()
    rest_orders = Order.query.filter_by(wing='restaurant').all()
    hotel_orders = Order.query.filter_by(wing='hotel').all()

    sweets_revenue = sum(o.final_amount for o in sweets_orders)
    rest_revenue = sum(o.final_amount for o in rest_orders)
    hotel_service_revenue = sum(o.final_amount for o in hotel_orders)
    total_sales = sweets_revenue + rest_revenue + hotel_service_revenue

    # Hotel Rooms & Inquiries
    total_rooms = HotelRoom.query.count()
    occupied_rooms = HotelRoom.query.filter_by(status='occupied').count()
    available_rooms = HotelRoom.query.filter_by(status='available').count()
    hotel_bookings = RoomBooking.query.order_by(RoomBooking.created_at.desc()).limit(10).all()

    # Dairy Khata Outstanding
    khata_customers = KhataCustomer.query.all()
    total_khata_due = sum(c.current_balance for c in khata_customers if c.current_balance > 0)
    total_daily_milk = sum(c.daily_milk_qty for c in khata_customers if c.status == 'active')

    # Menu items & categories
    categories = Category.query.order_by(Category.wing, Category.sort_order).all()
    items = MenuItem.query.order_by(MenuItem.wing, MenuItem.name).all()

    # Recent Live Orders with Status Filter
    status_filter = request.args.get('status')
    wing_filter = request.args.get('wing')
    query = Order.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if wing_filter:
        query = query.filter_by(wing=wing_filter)
    recent_orders = query.order_by(Order.created_at.desc()).limit(25).all()

    return render_template(
        'admin/dashboard.html',
        sweets_revenue=sweets_revenue,
        rest_revenue=rest_revenue,
        hotel_service_revenue=hotel_service_revenue,
        total_sales=total_sales,
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        available_rooms=available_rooms,
        hotel_bookings=hotel_bookings,
        total_khata_due=total_khata_due,
        total_daily_milk=total_daily_milk,
        categories=categories,
        items=items,
        recent_orders=recent_orders,
        current_status_filter=status_filter or 'all',
        current_wing_filter=wing_filter or 'all'
    )

# --- Admin Live Order Controls ---
@admin_bp.route('/order/<int:order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['pending', 'preparing', 'ready', 'completed', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash(f"Order #{order.order_number} status updated to {new_status.capitalize()}.", "success")
    return redirect(request.referrer or url_for('admin_bp.dashboard'))

# --- Inventory & Product Controls ---
@admin_bp.route('/toggle-item/<int:item_id>', methods=['POST'])
@login_required
def toggle_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    item.is_available = not item.is_available
    db.session.commit()
    status_text = "In Stock" if item.is_available else "Out of Stock"
    flash(f"'{item.name}' marked as {status_text}.", "info")
    return redirect(request.referrer or url_for('admin_bp.dashboard'))

@admin_bp.route('/item/add', methods=['POST'])
@login_required
def add_item():
    name = request.form.get('name')
    wing = request.form.get('wing', 'sweets')
    category_id = request.form.get('category_id')
    price = float(request.form.get('price', 0))
    unit = request.form.get('unit', 'pc')
    description = request.form.get('description', '')
    image_url = request.form.get('image_url', '')

    if name and price > 0:
        new_item = MenuItem(
            name=name,
            wing=wing,
            category_id=int(category_id) if category_id else None,
            price=price,
            unit=unit,
            description=description,
            image_url=image_url or "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=500&auto=format&fit=crop",
            is_available=True,
            is_popular=False,
            is_veg=True
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f"Product '{name}' successfully added.", "success")
    return redirect(url_for('admin_bp.dashboard'))

@admin_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    name = item.name
    db.session.delete(item)
    db.session.commit()
    flash(f"Product '{name}' has been deleted.", "warning")
    return redirect(url_for('admin_bp.dashboard'))
