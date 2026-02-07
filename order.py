import streamlit as st
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO
import random
import string

# --- Sheet.Best API URL from Secrets ---
SHEET_API_URL = st.secrets["sheet_best"]["api_url"]

# --- Page config ---
st.set_page_config(page_title="Bake Bites Haven", page_icon="🍪", layout="wide")

# --- Session state ---
if 'cart' not in st.session_state:
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

# --- Home & Menu page ---
if page == "Home & Menu":
    st.title("🍪 BakeBites.Haven")
    headlines = ["Time to Fill Your Kukis Raya Basket! ✨🌙"]
    st.markdown(f"### {random.choice(headlines)}")
    st.divider()

    cols = st.columns(3)
    for i, item in enumerate(desserts):
        col = cols[i % 3]
        with col:
            st.image(item["image"], width=250)
            st.subheader(item["name"])
            st.write(f"**Price:** RM {item['price']:.2f}")
            st.caption(f"Quantity: {item['unit']}")

            if f"qty_{i}" not in st.session_state:
                st.session_state[f"qty_{i}"] = 1

            q_col1, q_col2, q_col3 = st.columns([1,1,2])
            with q_col1:
                if st.button("➖", key=f"minus_{i}"):
                    if st.session_state[f"qty_{i}"] > 1:
                        st.session_state[f"qty_{i}"] -= 1
            with q_col2:
                st.markdown(f"**{st.session_state[f'qty_{i}']}**")
            with q_col3:
                if st.button("➕", key=f"plus_{i}"):
                    st.session_state[f"qty_{i}"] += 1

            if st.button(f"+ Add to Cart", key=f"add_{i}"):
                # Check if item already in cart
                for cart_item in st.session_state.cart:
                    if cart_item["name"] == item["name"]:
                        cart_item["quantity"] += st.session_state[f"qty_{i}"]
                        break
                else:
                    st.session_state.cart.append({
                        "name": item["name"],
                        "price": item["price"],
                        "unit": item["unit"],
                        "quantity": st.session_state[f"qty_{i}"]
                    })
                st.toast(f"{st.session_state[f'qty_{i}']} x {item['name']} added!", icon="🛒")
                st.session_state[f"qty_{i}"] = 1

# --- View Cart & Submit Order page ---
elif page == "View Cart & Submit Order":
    st.title("🛒 Your Cart")
    
    if not st.session_state.cart:
        st.info("Your cart is empty. Go grab your kukis raya!")
    else:
        # Display cart items with quantity control and remove option
        total = 0
        for idx, item in enumerate(st.session_state.cart.copy()):  # loop over a copy
            col1, col2, col3, col4 = st.columns([4,1,1,1])
            with col1:
                st.write(f"✅ **{item['name']}** x {item.get('quantity',1)} — RM {item['price']*item.get('quantity',1):.2f}")
            with col2:
                if st.button("➖", key=f"dec_{idx}"):
                    if item["quantity"] > 1:
                        st.session_state.cart[idx]["quantity"] -= 1
                    else:
                        st.session_state.cart.pop(idx)
            with col3:
                if st.button("➕", key=f"inc_{idx}"):
                    st.session_state.cart[idx]["quantity"] += 1
            with col4:
                if st.button("❌ Remove", key=f"remove_{idx}"):
                    st.session_state.cart.pop(idx)

            total += item["price"]*item.get("quantity",1)

        st.divider()
        st.subheader(f"Total Amount: RM {total:.2f}")

        st.markdown("### Fill in your details to submit your order")
        name = st.text_input("Full Name")
        phone = st.text_input("WhatsApp Number")
        address = st.text_area("Delivery Address")
        remarks = st.text_input("Special Request")

        if st.button("Submit Order"):
            if not name or not phone or not address:
                st.error("Please fill in all required fields.")
            else:
                order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Prepare order dictionary
                order_data = {
                    "Order ID": order_id,
                    "Timestamp": order_time,
                    "Name": name,
                    "WhatsApp": phone,
                    "Address": address,
                    "Tart Nenas Qty": 0,
                    "Tart Chocolate Qty": 0,
                    "Sea Salt Cookie Qty": 0,
                    "Total Amount": total,
                    "Remarks": remarks
                }

                # Fill quantities from cart
                for item in st.session_state.cart:
                    if item["name"] == "Tart Nenas":
                        order_data["Tart Nenas Qty"] = item.get("quantity",1)
                    elif item["name"] == "Tart Chocolate":
                        order_data["Tart Chocolate Qty"] = item.get("quantity",1)
                    elif item["name"] == "Sea Salt Chocolate Chip":
                        order_data["Sea Salt Cookie Qty"] = item.get("quantity",1)

                # Send to Sheet.Best
                try:
                    res = requests.post(SHEET_API_URL, json=order_data, timeout=10)
                    if res.status_code in [200, 201]:
                        st.success(f"🎉 Order submitted successfully! Order ID: {order_id}")
                        st.session_state.cart = []
                    else:
                        st.error("❌ Failed to submit order. Please check Sheet.Best connection.")
                        st.write(res.status_code, res.text)
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Failed to submit order: {e}")



