import streamlit as st
from datetime import datetime
import requests
import random
import string

# --- Sheet.Best API URL from Secrets ---
SHEET_API_URL = st.secrets["sheet_best"]["api_url"]

# --- Page config ---
st.set_page_config(page_title="Bake Bites Haven", page_icon="🍪", layout="wide")

# --- Session state ---
if "cart" not in st.session_state:
    st.session_state.cart = []

# --- Sidebar navigation ---
st.sidebar.title("🍪 BakeBites.Haven")
page = st.sidebar.radio("Go to", ["Home & Menu", "View Cart & Submit Order"])

# --- Dessert data ---
desserts = [
    {"name": "Tart Nenas", "price": 35.00, "unit": "40 pieces +-", "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/tart_nenas.jpg"},
    {"name": "Tart Chocolate", "price": 35.00, "unit": "40 pieces +-", "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/tart_chocolate.jpg"},
    {"name": "Sea Salt Chocolate Chip", "price": 35.00, "unit": "40 pieces +-", "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/sea_salt_cookie.jpg"},
]

# =========================================================
# 🏠 HOME & MENU
# =========================================================
if page == "Home & Menu":
    st.title("🍪 BakeBites.Haven")
    st.markdown("### Time to Fill Your Kukis Raya Basket! ✨🌙")
    st.divider()

    cols = st.columns(3)
    for i, item in enumerate(desserts):
        with cols[i]:
            st.image(item["image"], width=250)
            st.subheader(item["name"])
            st.write(f"**Price:** RM {item['price']:.2f}")
            st.caption(f"Quantity: {item['unit']}")

            qty_key = f"qty_{i}"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1

            q1, q2, q3 = st.columns([1,1,2])
            with q1:
                if st.button("➖", key=f"minus_{i}") and st.session_state[qty_key] > 1:
                    st.session_state[qty_key] -= 1
            with q2:
                st.markdown(f"**{st.session_state[qty_key]}**")
            with q3:
                if st.button("➕", key=f"plus_{i}"):
                    st.session_state[qty_key] += 1

            if st.button("+ Add to Cart", key=f"add_{i}"):
                for cart_item in st.session_state.cart:
                    if cart_item["name"] == item["name"]:
                        cart_item["quantity"] += st.session_state[qty_key]
                        break
                else:
                    st.session_state.cart.append({
                        "name": item["name"],
                        "price": item["price"],
                        "quantity": st.session_state[qty_key]
                    })

                st.toast(f"{st.session_state[qty_key]} x {item['name']} added!", icon="🛒")
                st.session_state[qty_key] = 1

# =========================================================
# 🛒 CART & SUBMIT ORDER
# =========================================================
elif page == "View Cart & Submit Order":
    st.title("🛒 Your Cart")

    if not st.session_state.cart:
        st.info("Your cart is empty. Go grab your kukis raya!")
    else:
        remove_indices = []

        # 1️⃣ Update quantities / mark removals
        for idx, item in enumerate(st.session_state.cart):
            c1, c2, c3, c4 = st.columns([4,1,1,1])

            with c1:
                st.write(
                    f"✅ **{item['name']}** x {item['quantity']} — "
                    f"RM {item['price'] * item['quantity']:.2f}"
                )

            with c2:
                if st.button("➖", key=f"dec_{idx}"):
                    if item["quantity"] > 1:
                        st.session_state.cart[idx]["quantity"] -= 1
                    else:
                        remove_indices.append(idx)

            with c3:
                if st.button("➕", key=f"inc_{idx}"):
                    st.session_state.cart[idx]["quantity"] += 1

            with c4:
                if st.button("❌", key=f"remove_{idx}"):
                    remove_indices.append(idx)

        # 2️⃣ Remove items safely
        for idx in sorted(remove_indices, reverse=True):
            st.session_state.cart.pop(idx)

        # 3️⃣ Calculate total AFTER all updates
        total = sum(
            item["price"] * item["quantity"]
            for item in st.session_state.cart
        )

        st.divider()
        st.subheader(f"💰 Total Amount: RM {total:.2f}")

        # -----------------------------
        # Order Form
        # -----------------------------
        st.markdown("### Fill in your details")
        name = st.text_input("Full Name")
        phone = st.text_input("WhatsApp Number")
        address = st.text_area("Delivery Address")
        remarks = st.text_input("Special Request")

        if st.button("Submit Order"):
            if not name or not phone or not address:
                st.error("Please fill in all required fields.")
            else:
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

                order_data = {
                    "Order ID": order_id,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Name": name,
                    "WhatsApp": phone,
                    "Address": address,
                    "Tart Nenas Qty": 0,
                    "Tart Chocolate Qty": 0,
                    "Sea Salt Cookie Qty": 0,
                    "Total Amount": total,
                    "Remarks": remarks
                }

                for item in st.session_state.cart:
                    if item["name"] == "Tart Nenas":
                        order_data["Tart Nenas Qty"] = item["quantity"]
                    elif item["name"] == "Tart Chocolate":
                        order_data["Tart Chocolate Qty"] = item["quantity"]
                    elif item["name"] == "Sea Salt Chocolate Chip":
                        order_data["Sea Salt Cookie Qty"] = item["quantity"]

                try:
                    res = requests.post(SHEET_API_URL, json=order_data, timeout=10)
                    if res.status_code in [200, 201]:
                        st.success(f"🎉 Order submitted! Order ID: {order_id}")
                        st.session_state.cart = []
                    else:
                        st.error("Failed to submit order.")
                except Exception as e:
                    st.error(f"Error: {e}")
