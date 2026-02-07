import streamlit as st
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO
import random
import gspread
from google.oauth2.service_account import Credentials
import string

# --- Google Sheets setup ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
SPREADSHEET_KEY = "18MA-Oy0nbasDc0Kr-2iUhYSpj-R4AmLHsog1N8fUMzI"  # replace with your sheet key
sheet = client.open_by_key(SPREADSHEET_KEY).sheet1

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
            img = Image.open(BytesIO(requests.get(item["image"]).content)).resize((250,250))
            st.image(img)
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
                st.session_state.cart.append({
                    "name": item["name"],
                    "price": item["price"],
                    "unit": item["unit"],
                    "quantity": st.session_state[f"qty_{i}"]
                })
                st.toast(f"{st.session_state[f'qty_{i}']} x {item['name']} added!", icon="🛒")
                st.session_state[f"qty_{i}"] = 1

# --- View Cart & Submit Order ---
elif page == "View Cart & Submit Order":
    st.title("🛒 Your Cart")
    if not st.session_state.cart:
        st.info("Your cart is empty. Go grab your kukis raya!")
    else:
        total = sum(item["price"]*item.get("quantity",1) for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"✅ **{item['name']}** x {item.get('quantity',1)} — RM {item['price']*item.get('quantity',1):.2f}")

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

                # Create a dictionary of quantities per dessert
                quantities = {dessert["name"]: 0 for dessert in desserts}
                for item in st.session_state.cart:
                    quantities[item["name"]] = item.get("quantity",1)

                # Append row: Order ID, Timestamp, Name, WhatsApp, Address, Dessert Qtys, Total, Remarks
                row = [
                    order_id, order_time, name, phone, address,
                    quantities["Tart Nenas"],
                    quantities["Tart Chocolate"],
                    quantities["Sea Salt Chocolate Chip"],
                    total,
                    remarks
                ]
                sheet.append_row(row)

                st.success(f"🎉 Order submitted successfully! Order ID: {order_id}")
                st.session_state.cart = []
