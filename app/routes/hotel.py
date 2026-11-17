from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import HotelRoom, RoomBooking

hotel_bp = Blueprint('hotel_bp', __name__)

@hotel_bp.route('/')
@login_required
def index():
    rooms = HotelRoom.query.order_by(HotelRoom.room_number).all()
    bookings = RoomBooking.query.order_by(RoomBooking.created_at.desc()).limit(20).all()
    available_count = HotelRoom.query.filter_by(status='available').count()
    occupied_count = HotelRoom.query.filter_by(status='occupied').count()
    return render_template(
        'hotel_manager/index.html',
        rooms=rooms,
        bookings=bookings,
        available_count=available_count,
        occupied_count=occupied_count
    )

@hotel_bp.route('/room/<int:room_id>/status', methods=['POST'])
@login_required
def update_room_status(room_id):
    room = HotelRoom.query.get_or_404(room_id)
    new_status = request.form.get('status')
    if new_status in ['available', 'occupied', 'reserved', 'cleaning']:
        room.status = new_status
        db.session.commit()
        flash(f"Room {room.room_number} status set to {new_status.capitalize()}.", "info")
    return redirect(url_for('hotel_bp.index'))

@hotel_bp.route('/quick-checkin', methods=['POST'])
@login_required
def quick_checkin():
    room_id = request.form.get('room_id')
    guest_name = request.form.get('guest_name')
    guest_phone = request.form.get('guest_phone')
    guest_id_proof = request.form.get('guest_id_proof', '')
    days = int(request.form.get('days', 1))
    advance = float(request.form.get('advance', 0))

    room = HotelRoom.query.get_or_404(room_id)
    check_in = datetime.utcnow()
    check_out = datetime.utcnow()

    booking_num = f"CHK-{datetime.utcnow().strftime('%y%m%d%H%M')}"
    total = room.price_per_night * days

    booking = RoomBooking(
        booking_number=booking_num,
        room_id=room.id,
        guest_name=guest_name,
        guest_phone=guest_phone,
        guest_id_proof=guest_id_proof,
        check_in=check_in,
        check_out=check_out,
        num_guests=2,
        total_amount=total,
        advance_paid=advance,
        status='checked_in'
    )
    room.status = 'occupied'
    db.session.add(booking)
    db.session.commit()
    flash(f"Guest {guest_name} successfully checked into Room {room.room_number}.", "success")

    return redirect(url_for('hotel_bp.index'))
