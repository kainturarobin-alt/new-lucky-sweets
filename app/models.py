from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), default="Staff Member")
    role = db.Column(db.String(20), default="staff") # admin, cashier, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_hindi = db.Column(db.String(100))
    wing = db.Column(db.String(30), nullable=False) # 'sweets', 'restaurant', 'hotel'
    icon = db.Column(db.String(50), default="bi-tag")
    sort_order = db.Column(db.Integer, default=0)
    items = db.relationship('MenuItem', backref='category', lazy=True, cascade='all, delete-orphan')


class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    name_hindi = db.Column(db.String(120))
    wing = db.Column(db.String(30), nullable=False) # 'sweets', 'restaurant', 'hotel'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default="plate") # kg, pc, plate, litre, glass
    image_url = db.Column(db.String(300), nullable=True)
    description = db.Column(db.Text)
    is_available = db.Column(db.Boolean, default=True)
    is_popular = db.Column(db.Boolean, default=False)
    is_veg = db.Column(db.Boolean, default=True)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(32), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), default="Walk-in Customer")
    customer_phone = db.Column(db.String(20), default="")
    wing = db.Column(db.String(30), default="sweets") # sweets, restaurant, room_service
    order_type = db.Column(db.String(30), default="takeaway") # takeaway, dine-in, room_delivery
    table_or_room = db.Column(db.String(30), default="")
    total_amount = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="completed") # pending, preparing, ready, completed, cancelled
    payment_mode = db.Column(db.String(30), default="Cash") # Cash, UPI, Card, Udhar
    payment_status = db.Column(db.String(20), default="Paid")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    item_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Float, default=1.0)
    unit = db.Column(db.String(30), default="plate")
    price = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


class HotelRoom(db.Model):
    __tablename__ = 'hotel_rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False) # Deluxe AC, Super Deluxe AC, Royal Family Suite
    floor = db.Column(db.String(20), default="1st Floor")
    price_per_night = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="available") # available, occupied, reserved, cleaning
    amenities = db.Column(db.String(250), default="King Bed, Split AC, Free High-Speed Wi-Fi, Smart TV, Hot Water Geyser")
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    bookings = db.relationship('RoomBooking', backref='room', lazy=True)


class RoomBooking(db.Model):
    __tablename__ = 'room_bookings'
    id = db.Column(db.Integer, primary_key=True)
    booking_number = db.Column(db.String(32), unique=True, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('hotel_rooms.id'), nullable=False)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_phone = db.Column(db.String(20), nullable=False)
    guest_id_proof = db.Column(db.String(100), default="")
    check_in = db.Column(db.DateTime, nullable=False)
    check_out = db.Column(db.DateTime, nullable=False)
    num_guests = db.Column(db.Integer, default=2)
    total_amount = db.Column(db.Float, default=0.0)
    advance_paid = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default="confirmed") # inquiry, confirmed, checked_in, checked_out, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class KhataCustomer(db.Model):
    __tablename__ = 'khata_customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), default="")
    daily_milk_qty = db.Column(db.Float, default=1.0) # Daily subscription litres
    milk_rate = db.Column(db.Float, default=66.0) # Rate per litre
    current_balance = db.Column(db.Float, default=0.0) # Positive means customer owes shop
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('KhataTransaction', backref='customer', lazy=True, cascade='all, delete-orphan')


class KhataTransaction(db.Model):
    __tablename__ = 'khata_transactions'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('khata_customers.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    txn_type = db.Column(db.String(30), nullable=False) # 'milk_daily', 'paneer_entry', 'sweets_entry', 'payment_received'
    description = db.Column(db.String(200), default="")
    quantity = db.Column(db.Float, default=0.0)
    amount = db.Column(db.Float, nullable=False) # positive if debit (bill), negative if credit (payment)
    balance_after = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
