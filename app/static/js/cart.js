// Royal Cart & Order Placement Manager for New Lucky Group
// Sweets & Dairy • Family Restaurant • Residency

let _memoryCart = [];

const RoyalCart = {
    storageKey: 'nl_royal_cart',

    getCart() {
        try {
            const raw = localStorage.getItem(this.storageKey);
            if (raw) {
                const parsed = JSON.parse(raw);
                if (Array.isArray(parsed)) {
                    _memoryCart = parsed;
                    return parsed;
                }
            }
        } catch(e) {
            console.warn('localStorage read failed, falling back to memory', e);
        }
        return _memoryCart || [];
    },

    saveCart(cart) {
        _memoryCart = cart;
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(cart));
        } catch(e) {
            console.warn('localStorage save failed', e);
        }
        this.updateBadge();
        this.renderDrawer();
    },

    addItem(item, autoOpenDrawer = true) {
        const cart = this.getCart();
        const qty = parseFloat(item.quantity) || 1;
        const price = parseFloat(item.price) || 0;
        const unit = item.unit || 'pc';

        const existing = cart.find(i => String(i.id) === String(item.id) && i.unit === unit);
        if (existing) {
            existing.quantity = Math.round((parseFloat(existing.quantity) + qty) * 100) / 100;
        } else {
            cart.push({
                id: item.id,
                name: item.name,
                price: price,
                unit: unit,
                quantity: qty,
                image_url: item.image_url || ''
            });
        }

        this.saveCart(cart);
        this.showToast(`✔ Added ${qty} ${unit} of "${item.name}" to your order!`);

        if (autoOpenDrawer) {
            this.openDrawer();
        }
    },

    addItemDirect(item) {
        this.addItem(item, false);
    },

    openDrawer() {
        const drawerEl = document.getElementById('cartOffcanvas');
        if (!drawerEl) return;

        // Try Bootstrap 5 Offcanvas first
        try {
            if (window.bootstrap && bootstrap.Offcanvas) {
                const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawerEl);
                bsOffcanvas.show();
                return;
            }
        } catch(e) {
            console.warn('Bootstrap Offcanvas failed, falling back to pure CSS', e);
        }

        // Pure CSS fallback
        drawerEl.classList.add('show');
        drawerEl.style.visibility = 'visible';
        drawerEl.style.transform = 'none';
        let backdrop = document.getElementById('cartOffcanvasBackdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.id = 'cartOffcanvasBackdrop';
            backdrop.className = 'offcanvas-backdrop fade show';
            backdrop.onclick = () => RoyalCart.closeDrawer();
            document.body.appendChild(backdrop);
        }
        document.body.style.overflow = 'hidden';
    },

    closeDrawer() {
        const drawerEl = document.getElementById('cartOffcanvas');
        if (!drawerEl) return;

        try {
            if (window.bootstrap && bootstrap.Offcanvas) {
                const bsOffcanvas = bootstrap.Offcanvas.getInstance(drawerEl);
                if (bsOffcanvas) bsOffcanvas.hide();
            }
        } catch(e) {}

        drawerEl.classList.remove('show');
        drawerEl.style.visibility = '';
        drawerEl.style.transform = '';
        const backdrop = document.getElementById('cartOffcanvasBackdrop');
        if (backdrop) backdrop.remove();
        document.body.style.overflow = '';
    },

    openCheckout() {
        this.closeDrawer();
        const modalEl = document.getElementById('checkoutModal');
        if (modalEl && window.bootstrap) {
            setTimeout(() => {
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                modal.show();
            }, 250);
        }
    },

    removeItem(index) {
        const cart = this.getCart();
        if (index >= 0 && index < cart.length) {
            const removed = cart.splice(index, 1);
            this.saveCart(cart);
            if (removed.length > 0) {
                this.showToast(`Removed "${removed[0].name}" from order.`);
            }
        }
    },

    updateQuantity(index, newQty) {
        const cart = this.getCart();
        if (index >= 0 && index < cart.length) {
            if (newQty <= 0) {
                this.removeItem(index);
            } else {
                cart[index].quantity = Math.round(newQty * 100) / 100;
                this.saveCart(cart);
            }
        }
    },

    clearCart() {
        try {
            localStorage.removeItem(this.storageKey);
        } catch(e) {}
        _memoryCart = [];
        this.updateBadge();
        this.renderDrawer();
        this.showToast('Order bag cleared.');
    },

    getTotal() {
        const cart = this.getCart();
        return cart.reduce((sum, item) => sum + ((parseFloat(item.price) || 0) * (parseFloat(item.quantity) || 0)), 0);
    },

    updateBadge() {
        const cart = this.getCart();
        const count = cart.reduce((sum, i) => sum + (i.unit === 'kg' ? 1 : (parseFloat(i.quantity) || 1)), 0);
        const roundedCount = Math.round(count);

        const badgeElements = document.querySelectorAll('.cart-count-badge');
        badgeElements.forEach(el => {
            el.innerText = roundedCount;
            el.style.display = 'inline-block';
            el.classList.remove('badge-bounce');
            void el.offsetWidth; // trigger reflow
            el.classList.add('badge-bounce');
        });

        const totalElements = document.querySelectorAll('.cart-total-badge');
        totalElements.forEach(el => {
            el.innerText = '₹' + this.getTotal().toFixed(0);
        });
    },

    renderDrawer() {
        const container = document.getElementById('cartDrawerItems');
        const emptyState = document.getElementById('cartEmptyState');
        const footerState = document.getElementById('cartFooter');
        if (!container) return;

        const cart = this.getCart();
        if (!cart || cart.length === 0) {
            container.innerHTML = '';
            if (emptyState) emptyState.style.display = 'block';
            if (footerState) footerState.style.display = 'none';
            return;
        }

        if (emptyState) emptyState.style.display = 'none';
        if (footerState) footerState.style.display = 'block';

        let html = '';
        cart.forEach((item, index) => {
            const itemTotal = (parseFloat(item.price) || 0) * (parseFloat(item.quantity) || 0);
            const stepVal = (item.unit === 'kg') ? 0.25 : 1;
            const imgSrc = item.image_url || 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=100';

            html += `
            <div class="card p-3 mb-2 border rounded-3 shadow-sm bg-white">
                <div class="d-flex align-items-center gap-3">
                    <img src="${imgSrc}" alt="${item.name}" class="rounded-3" style="width: 52px; height: 52px; object-fit: cover; border: 1px solid rgba(201,154,44,0.3);">
                    <div class="flex-grow-1 overflow-hidden">
                        <h6 class="mb-0 fw-bold text-dark text-truncate" title="${item.name}">${item.name}</h6>
                        <small class="text-muted">₹${parseFloat(item.price).toFixed(0)} / ${item.unit}</small>
                    </div>
                    <button class="btn btn-sm btn-outline-danger border-0 p-1" onclick="RoyalCart.removeItem(${index})" title="Remove item">
                        <i class="bi bi-trash fs-6"></i>
                    </button>
                </div>
                <div class="d-flex justify-content-between align-items-center mt-2 pt-2 border-top">
                    <div class="input-group input-group-sm" style="width: 130px;">
                        <button class="btn btn-outline-secondary" onclick="RoyalCart.updateQuantity(${index}, ${item.quantity - stepVal})">-</button>
                        <span class="input-group-text bg-white px-2 fw-bold text-center flex-grow-1" style="font-size: 0.85rem;">${item.quantity} ${item.unit}</span>
                        <button class="btn btn-outline-secondary" onclick="RoyalCart.updateQuantity(${index}, ${item.quantity + stepVal})">+</button>
                    </div>
                    <div class="fw-bold fs-6" style="color: #4a071f;">
                        ₹${itemTotal.toFixed(0)}
                    </div>
                </div>
            </div>`;
        });

        container.innerHTML = html;
        const totalAmountEl = document.getElementById('cartTotalAmount');
        if (totalAmountEl) {
            totalAmountEl.innerText = '₹' + this.getTotal().toFixed(0);
        }
    },

    submitOrder(wing = 'sweets') {
        const nameInput = document.getElementById('orderCustName');
        const phoneInput = document.getElementById('orderCustPhone');
        const orderTypeInput = document.getElementById('orderType');
        const tableRoomInput = document.getElementById('orderTableRoom');
        const notesInput = document.getElementById('orderNotes');

        const name = nameInput ? nameInput.value.trim() : 'Valued Customer';
        const phone = phoneInput ? phoneInput.value.trim() : '';

        if (!phone || phone.length < 10) {
            alert('Please enter a valid 10-digit mobile number to confirm your order.');
            if (phoneInput) phoneInput.focus();
            return;
        }

        const cartItems = this.getCart();
        if (!cartItems || cartItems.length === 0) {
            alert('Your order bag is empty. Please add items before placing an order.');
            return;
        }

        const payload = {
            customer_name: name || 'Valued Customer',
            customer_phone: phone,
            wing: wing,
            order_type: orderTypeInput ? orderTypeInput.value : 'takeaway',
            table_or_room: tableRoomInput ? tableRoomInput.value : '',
            notes: notesInput ? notesInput.value : '',
            items: cartItems
        };

        const submitBtn = document.getElementById('orderSubmitBtn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Placing Your Order...';
        }

        fetch('/api/order/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                this.clearCart();
                const modalEl = document.getElementById('checkoutModal');
                if (modalEl && window.bootstrap) {
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                }
                // Open WhatsApp notification
                window.open(data.whatsapp_url, '_blank');
                // Redirect to receipt view
                window.location.href = data.view_url;
            } else {
                alert('Order Error: ' + (data.message || 'Could not place order.'));
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = 'Confirm & Place Order';
                }
            }
        })
        .catch(err => {
            console.error(err);
            alert('Network connection error. Please try again.');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerText = 'Confirm & Place Order';
            }
        });
    },

    showToast(message) {
        let toast = document.getElementById('royalToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'royalToast';
            toast.style.position = 'fixed';
            toast.style.bottom = '85px';
            toast.style.right = '24px';
            toast.style.zIndex = '9999';
            toast.style.background = '#4a071f';
            toast.style.color = '#fdfaf4';
            toast.style.padding = '12px 20px';
            toast.style.borderRadius = '14px';
            toast.style.border = '1.5px solid #c99a2c';
            toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.35)';
            toast.style.fontWeight = '600';
            toast.style.fontSize = '0.9rem';
            toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            document.body.appendChild(toast);
        }
        toast.innerText = message;
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
        clearTimeout(toast._timeout);
        toast._timeout = setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px)';
        }, 3200);
    }
};

window.RoyalCart = RoyalCart;

document.addEventListener('DOMContentLoaded', () => {
    RoyalCart.updateBadge();
    RoyalCart.renderDrawer();

    const drawerEl = document.getElementById('cartOffcanvas');
    if (drawerEl) {
        drawerEl.addEventListener('show.bs.offcanvas', () => {
            RoyalCart.renderDrawer();
        });
    }
});
