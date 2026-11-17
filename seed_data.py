from app import create_app, db
from app.models import User, Category, MenuItem, HotelRoom, KhataCustomer, KhataTransaction
from datetime import datetime, date

app = create_app()

def seed_database(target_app=None):
    use_app = target_app if target_app else app
    with use_app.app_context():
        db.create_all()

        # 1. Admin & Staff User
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                full_name='Owner / Manager',
                role='admin'
            )
            admin.set_password('lucky123')
            db.session.add(admin)

        if not User.query.filter_by(username='cashier').first():
            cashier = User(
                username='cashier',
                full_name='Front Counter Staff',
                role='cashier'
            )
            cashier.set_password('lucky123')
            db.session.add(cashier)

        # 2. Categories
        cat_data = [
            # Sweets & Dairy Wing
            ("Traditional Sweets", "पारंपरिक मिठाइयाँ", "sweets", "bi-basket2-fill", 1),
            ("Pure Dairy Products", "शुद्ध डेयरी उत्पाद", "sweets", "bi-droplet-half", 2),
            ("Hot Snacks & Chaat", "गरमा-गरम स्नैक्स व समोसा", "sweets", "bi-fire", 3),
            ("Celebration Gift Boxes", "त्यौहार व शादी गिफ्ट बॉक्स", "sweets", "bi-gift", 4),
            
            # Restaurant Wing
            ("Main Course Special", "शाही मुख्य भोजन (ग्रेवी)", "restaurant", "bi-egg-fried", 5),
            ("Tandoor & Breads", "तंदूरी रोटी व नान", "restaurant", "bi-disc", 6),
            ("Chinese & Fast Food", "चाइनीज व फास्ट फूड", "restaurant", "bi-cup-hot", 7),
            ("Royal Thali & Combos", "शाही थाली व कॉम्बो", "restaurant", "bi-grid-1x2", 8),
            
            # Hotel Wing
            ("Deluxe Accommodation", "डीलक्स रूम्स", "hotel", "bi-door-open", 9),
            ("Executive Family Suites", "रॉयल फैमिली सुइट्स", "hotel", "bi-building", 10),
        ]

        categories_map = {}
        for name, name_hi, wing, icon, sort_order in cat_data:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name, name_hindi=name_hi, wing=wing, icon=icon, sort_order=sort_order)
                db.session.add(cat)
                db.session.flush()
            categories_map[name] = cat.id

        # 3. Exact Authentic Product Photos
        items_data = [
            # Sweets
            ("Kaju Katli (Pure Cashew)", "Traditional Sweets", "sweets", 920.0, "kg", 
             "https://commons.wikimedia.org/wiki/Special:FilePath/Kaju_katli.JPG?width=600", 
             "Rich diamond-shaped silver-foiled cashew delicacy made with finest Goan cashews.", True, True),
            ("Special Rasmalai (2 Pcs)", "Traditional Sweets", "sweets", 70.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Ras-Malai.jpg?width=600",
             "Soft spongy cottage cheese discs soaked in thickened saffron & cardamom milk.", True, True),
            ("Pure Milk Cake", "Traditional Sweets", "sweets", 560.0, "kg",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Milk_Cake.jpg?width=600",
             "Caramelized grain-textured traditional milk fudge slow cooked to perfection.", True, True),
            ("Gulab Jamun (Desi Ghee)", "Traditional Sweets", "sweets", 440.0, "kg",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Gulab_Jamun.jpg?width=600",
             "Soft melt-in-mouth golden dumplings dipped in aromatic rose sugar syrup.", True, False),
            ("Besan Laddu (Desi Ghee)", "Traditional Sweets", "sweets", 520.0, "kg",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Besan_laddu_photo.JPG?width=600",
             "Roasted gram flour balls with pure desi ghee, roasted dry fruits and fragrant cardamom.", True, False),
            
            # Dairy
            ("Fresh Malai Paneer", "Pure Dairy Products", "sweets", 380.0, "kg",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Panir_Paneer_Indian_cheese_fresh.jpg?width=600",
             "Made fresh every morning from 100% pure buffalo milk. Super soft, creamy and rich in protein.", True, True),
            ("Pure Fresh Milk", "Pure Dairy Products", "sweets", 66.0, "litre",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Glass_of_Milk_(temperature_shocked).jpg?width=600",
             "Unadulterated farm-fresh full cream milk delivered daily.", True, False),
            ("Fresh Thick Dahi (Curd)", "Pure Dairy Products", "sweets", 90.0, "kg",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Dahi_(curd).jpg?width=600",
             "Naturally set thick and creamy sweet curd, perfect for dining and raita.", True, False),
            ("Special Kulhad Malai Lassi", "Pure Dairy Products", "sweets", 60.0, "glass",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Lassi_(Sweet).JPG?width=600",
             "Chilled thick whipped yogurt served in traditional earthen clay cup with rich rabdi & malai topping.", True, True),
            
            # Snacks
            ("Miyawala Famous Crispy Samosa", "Hot Snacks & Chaat", "sweets", 15.0, "pc",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Samosa_-_Snack.JPG?width=600",
             "Live counter golden crispy samosa stuffed with spiced potato, paneer chunks and green peas. Served with sweet tamarind & spicy mint chutney.", True, True),
            ("Crispy Paneer Patties", "Hot Snacks & Chaat", "sweets", 25.0, "pc",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Curry_puffs_(1862151488).jpg?width=600",
             "Flaky golden bakery puff loaded with seasoned spiced paneer filling.", True, False),
            ("Royal Shahi Gift Hamper", "Celebration Gift Boxes", "sweets", 680.0, "box",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Sweets_Diwali_Mithai_India.jpg?width=600",
             "Assorted luxury gift pack of Kaju Katli, Milk Cake, Dryfruit Ladoo and Roasted Cashews.", True, True),

            # Restaurant Main Course
            ("Paneer Butter Masala", "Main Course Special", "restaurant", 240.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Paneer_butter_masala.jpg?width=600",
             "Cubes of our in-house fresh cottage cheese simmered in a silky tomato butter gravy with aromatic kasuri methi.", True, True),
            ("Dal Makhani (Slow Simmered)", "Main Course Special", "restaurant", 210.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Dal_Makhani.jpg?width=600",
             "Black lentils and kidney beans slow cooked overnight with butter, cream, and freshly ground spices.", True, True),
            ("Kadhai Paneer Special", "Main Course Special", "restaurant", 240.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Paneer_butter_masala.jpg?width=600",
             "Fresh paneer tossed with crisp bell peppers, onions, and freshly pounded coriander & red chilies.", True, False),
            ("Butter Tandoori Naan", "Tandoor & Breads", "restaurant", 45.0, "pc",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Naan.JPG?width=600",
             "Freshly baked in traditional clay tandoor and brushed with rich golden butter.", True, False),
            ("Lachha Paratha", "Tandoor & Breads", "restaurant", 40.0, "pc",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Naan.JPG?width=600",
             "Crispy multi-layered whole wheat bread baked in clay tandoor.", True, False),
            ("Veg Hakka Noodles", "Chinese & Fast Food", "restaurant", 130.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Veg_Hakka_Noodles.jpg?width=600",
             "Wok-tossed noodles with shredded cabbage, carrots, bell peppers, and scallions.", True, False),
            ("Veg Manchurian Gravy", "Chinese & Fast Food", "restaurant", 160.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hakka_Noodles,_Veg_Manchurian_PK009.jpg?width=600",
             "Crispy mixed vegetable roundels cooked in tangy soy garlic ginger sauce.", True, False),
            ("Lucky Royal Special Thali", "Royal Thali & Combos", "restaurant", 230.0, "thali",
             "https://commons.wikimedia.org/wiki/Special:FilePath/A_Tipical_Veg_North_Indian_Thali.jpg?width=600",
             "Complete hearty meal: Shahi Paneer, Dal Makhani, Seasonal Sabzi, Jeera Rice, 3 Butter Roti, Dahi Raita, Salad, Achar & Gulab Jamun.", True, True),
            ("Chhole Bhature Special (2 Pcs)", "Royal Thali & Combos", "restaurant", 110.0, "plate",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Chole_bhature.jpg?width=600",
             "Crispy puffed bhature served with Amritsari pindi chhole, pickled onions and green chili.", True, True),
        ]

        for name, cat_name, wing, price, unit, img, desc, is_avail, is_pop in items_data:
            item = MenuItem.query.filter_by(name=name).first()
            if not item:
                item = MenuItem(
                    name=name,
                    category_id=categories_map.get(cat_name),
                    wing=wing,
                    price=price,
                    unit=unit,
                    image_url=img,
                    description=desc,
                    is_available=is_avail,
                    is_popular=is_pop,
                    is_veg=True
                )
                db.session.add(item)
            else:
                # Update existing image URL to authentic verified photo
                item.image_url = img
                item.description = desc

        # 4. Hotel Rooms (New Lucky Residency)
        rooms_data = [
            ("101", "Deluxe AC Room", "1st Floor", 1599.0, "available",
             "King Bed, Split AC, Free High-Speed Wi-Fi, 32-inch LED TV, 24-hr Hot Water Geyser, Work Desk",
             "Comfortable air-conditioned deluxe room perfect for couples, travelers and business visitors.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel_room.jpg?width=600"),
            ("102", "Deluxe AC Room", "1st Floor", 1599.0, "available",
             "King Bed, Split AC, Free High-Speed Wi-Fi, 32-inch LED TV, 24-hr Hot Water Geyser, Work Desk",
             "Well-lit contemporary deluxe room with daily housekeeping and in-room dining service.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel_room.jpg?width=600"),
            ("201", "Super Deluxe AC Room (Balcony)", "2nd Floor", 1999.0, "available",
             "Premium King Bed, Mountain View Balcony, Split AC, Free Wi-Fi, 40-inch Smart TV, Tea/Coffee Maker, Modern Bath",
             "Spacious superior room featuring private outdoor balcony and scenic mountain breeze.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel_Room_with_queen_size_bed.jpg?width=600"),
            ("202", "Super Deluxe AC Room (Balcony)", "2nd Floor", 1999.0, "occupied",
             "Premium King Bed, Mountain View Balcony, Split AC, Free Wi-Fi, 40-inch Smart TV, Tea/Coffee Maker, Modern Bath",
             "Luxurious room with premium bedding, soft pillows and 24/7 dedicated room service.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel_Room_with_queen_size_bed.jpg?width=600"),
            ("301", "Royal Executive Family Suite", "3rd Floor", 2799.0, "available",
             "2 Queen Beds, Living Lounge Sofa, Dual ACs, 50-inch 4K Smart TV, Mini Fridge, Large Luxury Bathroom, Wardrobe",
             "Grand family suite designed for families of 4 to 6 people traveling together with supreme comfort.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel-suite-bedroom.jpg?width=600"),
            ("302", "Royal Executive Family Suite", "3rd Floor", 2799.0, "available",
             "2 Queen Beds, Living Lounge Sofa, Dual ACs, 50-inch 4K Smart TV, Mini Fridge, Large Luxury Bathroom, Wardrobe",
             "Elegantly decorated suite with separate sitting space and personalized hospitality.",
             "https://commons.wikimedia.org/wiki/Special:FilePath/Hotel-suite-bedroom.jpg?width=600"),
        ]

        for r_num, r_type, flr, price, status, amen, desc, img in rooms_data:
            room = HotelRoom.query.filter_by(room_number=r_num).first()
            if not room:
                room = HotelRoom(
                    room_number=r_num,
                    room_type=r_type,
                    floor=flr,
                    price_per_night=price,
                    status=status,
                    amenities=amen,
                    description=desc,
                    image_url=img
                )
                db.session.add(room)
            else:
                room.image_url = img

        db.session.commit()
        print("Database photos successfully updated with authentic food & hotel images!")

if __name__ == '__main__':
    seed_database()
