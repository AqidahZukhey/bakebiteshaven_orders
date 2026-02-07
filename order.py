import streamlit as st
from datetime import datetime, timezone, timedelta
import requests
import random
import string
from PIL import Image
from io import BytesIO

# --- Malaysia Time (UTC+8) ---
MYT = timezone(timedelta(hours=8))

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
    {"id": "nenas", "name": "Tart Nenas", "price": 35.00, "unit": "40 pieces +-",
     "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/tart_nenas.jpg"},
    {"id": "choc_tart", "name": "Tart Chocolate", "price": 35.00, "unit": "40 pieces +-",
     "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/tart_chocolate.jpg"},
    {"id": "sea_salt", "name": "Sea Salt Chocolate Chip", "price": 35.00, "unit": "40 pieces +-",
     "image": "https://raw.githubusercontent.com/AqidahZukhey/bakebiteshaven-images/main/sea_salt_cookie.jpg"},
]

# =========================================================
# 🔧 IMAGE LOADER (cached & resized)
# =========================================================
@st.cache_data
def load_and_resize_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img.resize((250, 250))

# =========================================================
# 🏠 HOME & MENU
# =========================================================

if page == "Home & Menu":

    st.title("🍪 BakeBites.Haven")
    st.markdown("### Time to Fill Your Kukis Raya Basket! ✨🌙")
    st.divider()

    cols = st.columns(3)

    for i, item in enumerate(desserts):
        with cols[i % 3]:

            # ✅ FIXED: same-size images
            img = load_and_resize_image(item["image"])
            st.image(img, width=250)

            st.subheader(item["name"])
            st.write(f"**Price:** RM {item['price']:.2f}")
            st.caption(f"Quantity: {item['unit']}")

            qty_key = f"qty_{item['id']}"
            if qty_key not in st.session_state:
                st.session_state[qty_key] = 1

            q1, q2, q3 = st.columns([1,1,2])
            with q1:
                if st.button("➖", key=f"minus_menu_{item['id']}") and st.session_state[qty_key] > 1:
                    st.session_state[qty_key] -= 1
            with q2:
                st.markdown(f"**{st.session_state[qty_key]}**")
            with q3:
                if st.button("➕", key=f"plus_menu_{item['id']}"):
                    st.session_state[qty_key] += 1

            if st.button("+ Add to Cart", key=f"add_{item['id']}"):
                for cart_item in st.session_state.cart:
                    if cart_item["id"] == item["id"]:
                        cart_item["quantity"] += st.session_state[qty_key]
                        break
                else:
                    st.session_state.cart.append({
                        "id": item["id"],
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
        remove_ids = []

        # 1️⃣ Update quantities
        for item in st.session_state.cart:
            c1, c2, c3, c4 = st.columns([4,1,1,1])

            with c1:
                st.write(
                    f"✅ **{item['name']}** x {item['quantity']} — "
                    f"RM {item['price'] * item['quantity']:.2f}"
                )

            with c2:
                if st.button("➖", key=f"dec_cart_{item['id']}"):
                    if item["quantity"] > 1:
                        item["quantity"] -= 1
                    else:
                        remove_ids.append(item["id"])
                    st.rerun()

            with c3:
                if st.button("➕", key=f"inc_cart_{item['id']}"):
                    item["quantity"] += 1
                    st.rerun()

            with c4:
                if st.button("❌", key=f"remove_cart_{item['id']}"):
                    remove_ids.append(item["id"])

        # 2️⃣ Remove safely (by ID, not index)
        st.session_state.cart = [
            item for item in st.session_state.cart
            if item["id"] not in remove_ids
        ]

        # 3️⃣ TOTAL — SINGLE SOURCE OF TRUTH
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
        remarks = st.text_input("Remarks")

        if st.button("Submit Order"):
            if not name or not phone or not address:
                st.error("Please fill in all required fields.")
            else:
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

                order_data = {
                    "Order ID": order_id,
                    "Timestamp": datetime.now(MYT).strftime("%A, %Y-%m-%d %H:%M:%S"),
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
                    if item["id"] == "nenas":
                        order_data["Tart Nenas Qty"] = item["quantity"]
                    elif item["id"] == "choc_tart":
                        order_data["Tart Chocolate Qty"] = item["quantity"]
                    elif item["id"] == "sea_salt":
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






