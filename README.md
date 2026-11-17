# New Lucky - Hospitality & Commerce Architecture 👑
### 1. New Lucky Sweets & Dairy
### 2. New Lucky Family Restaurant
### 3. New Lucky Residency
**Location:** Miyawala Chowk, Raipur Road, Dehradun, Uttarakhand 248005 • **Contact:** +91 94121 53429

---

## 🏛️ Public Visitor Experience (Customer-Facing Website)
The public website is tailored strictly for visitors and local customers:
* **Home:** Royal heritage branding, highlights of all 3 businesses, 769+ Google reviews badge, and interactive location map.
* **Products (New Lucky Sweets & Dairy):** Pure Desi Ghee sweets, daily morning fresh malai paneer, milk, curd, samosas & gift boxes with dynamic weight selector (250g, 500g, 1kg) and direct **"Place Order"** / **"Add to Bag"** buttons.
* **Family Restaurant (New Lucky Family Restaurant):** Full vegetarian dining menu, North Indian curries, tandoor naans, Chinese dishes, Deluxe Thalis, with Takeaway/Dine-in checkout and table reservations.
* **Hotel Residency (New Lucky Residency):** Deluxe AC rooms, balcony suites, amenities list, photo gallery, and direct room reservation inquiries.
* **Live Order Tracking (`/track`):** Visitors can enter their Order Number (e.g. `NL-261117-XXXX`) to track live progress (*Received ➔ Preparing ➔ Ready for Pickup / Out for Delivery ➔ Completed*).
* **Shopping Bag & Checkout:** Clean offcanvas drawer with zero friction ordering and official printable tax invoice receipt.

---

## 🔒 Security & Access Control
* **No Open Business Suite:** Visitors cannot view or access POS billing, hotel room racks, or customer debt ledgers from the public navigation.
* **Role-Based Authentication:** All management routes (`/admin/*`, `/pos/*`, `/hotel-desk/*`, `/khata/*`) are strictly protected via `@login_required`. Any unauthenticated attempt is instantly redirected to the secure staff login page.

---

## 💼 Business Operations & Management Suite (Staff & Owner)
1. **Multi-Business POS & Billing Terminal (`/pos`):**
   * **New Lucky Sweets & Dairy Mode:** Quick weight calculator buttons (100g, 250g, 500g, 1kg) and piece counters for sweets, samosas, and dairy.
   * **New Lucky Family Restaurant Mode:** Table number selector (Table 1 to 15), KOT (Kitchen Order Ticket), and dining bill print.
   * **New Lucky Residency Mode:** Room selector (Rooms 101 to 302), Nightly tariff calculator, and in-room food/sweets room service billing added to Room Folio.
   * Keyboard shortcut `F8` for instant checkout.
2. **Executive Command Dashboard (`/admin/dashboard`):**
   * **Live Order Dispatch Stream:** Real-time incoming orders with 1-click status update buttons (*Start Preparing ➔ Mark Ready ➔ Complete*).
   * **Product & Inventory Controller:** Add new menu products, change prices, and 1-click **"Mark In Stock / Out of Stock"** toggle.
   * **Financial Analytics:** Separate revenue tracking for *New Lucky Sweets & Dairy*, *New Lucky Family Restaurant*, and *New Lucky Residency*.
3. **Hotel Front Desk (`/hotel-desk`):** Live Room Rack status (*Vacant, Occupied, Cleaning*) and instant guest check-in.
4. **Customer Dairy Ledger (`/khata`):** Passbook ledger for regular milk & paneer subscribers with balance tracking.

---

## 🚀 How to Run the Program
1. Double-click **`start_program.bat`** OR execute in your terminal:
   ```bash
   python run.py
   ```
2. Open in browser:
   * **Visitor Portal:** `http://127.0.0.1:5000/`
   * **Order Products:** `http://127.0.0.1:5000/products`
   * **Track Order:** `http://127.0.0.1:5000/track`
   * **Staff Portal Login:** `http://127.0.0.1:5000/admin/login`
   * **POS Terminal (Protected):** `http://127.0.0.1:5000/pos`
   * **Admin Dashboard (Protected):** `http://127.0.0.1:5000/admin/dashboard`

---

## 🔑 Default Staff Credentials
* **Username:** `admin`
* **Password:** `lucky123`
*(Cashier: `cashier` / `lucky123`)*
