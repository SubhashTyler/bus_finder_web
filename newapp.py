import streamlit as st
import json
import os
from datetime import date

ROUTES = [
    {"from": "City A", "to": "City B", "bus": "Express 101", "departure": "09:00", "arrival": "12:00"},
    {"from": "City C", "to": "City D", "bus": "Rapid 202", "departure": "14:00", "arrival": "18:00"},
    {"from": "City E", "to": "City F", "bus": "Deluxe 303", "departure": "07:00", "arrival": "11:00"},
]

BOOKINGS_FILE = "bookings.json"

def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, 'r') as f:
        return json.load(f)

def save_booking(booking):
    bookings = load_bookings()
    bookings.append(booking)
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)

# --- Streamlit UI ---
st.set_page_config(page_title="Find My Bus", layout="centered")
st.title("🚌 Bus Finder App")

menu = st.sidebar.radio("Menu", ["Home", "Routes", "My Bookings", "Track Bus"])

if menu == "Home":
    st.subheader("🔍 Find Your Bus")
    from_city = st.text_input("From")
    to_city = st.text_input("To")
    journey_date = st.date_input("Journey Date", min_value=date.today())

    if st.button("Search Buses"):
        results = [r for r in ROUTES if r["from"].lower() == from_city.lower() and r["to"].lower() == to_city.lower()]
        if results:
            st.success(f"{len(results)} route(s) found")
            for r in results:
                st.markdown(f"**{r['bus']}**: {r['from']} → {r['to']} | {r['departure']} - {r['arrival']}")
                if st.button(f"Book {r['bus']}"):
                    save_booking({
                        "from": r['from'],
                        "to": r['to'],
                        "date": str(journey_date),
                        "bus": r['bus']
                    })
                    st.success("✅ Booking confirmed!")
        else:
            st.warning("No buses found for that route.")

elif menu == "Routes":
    st.subheader("🛣 Available Routes")
    for r in ROUTES:
        st.markdown(f"- **{r['from']} → {r['to']}** | {r['bus']} | {r['departure']} → {r['arrival']}")

elif menu == "My Bookings":
    st.subheader("📒 My Bookings")
    bookings = load_bookings()
    if bookings:
        for b in bookings:
            st.markdown(f"- {b['date']}: **{b['from']} → {b['to']}** on *{b['bus']}*")
    else:
        st.info("You have no bookings yet.")

elif menu == "Track Bus":
    st.subheader("📍 Bus Tracker")
    st.info("Simulated tracking: Your bus is currently en route and will arrive on time. 🚍")

