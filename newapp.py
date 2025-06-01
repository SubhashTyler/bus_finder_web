import streamlit as st
import json
import os
from datetime import date, datetime

# Simulated Indian bus routes data
ROUTES = [
    {"from": "Mumbai", "to": "Pune", "bus": "Shivneri Express", "departure": "07:00", "arrival": "10:00"},
    {"from": "Delhi", "to": "Agra", "bus": "Rajdhani Express", "departure": "09:00", "arrival": "12:00"},
    {"from": "Bangalore", "to": "Mysore", "bus": "Kaveri Deluxe", "departure": "06:30", "arrival": "09:30"},
    {"from": "Chennai", "to": "Tirupati", "bus": "Godavari Express", "departure": "08:00", "arrival": "11:00"},
    {"from": "Hyderabad", "to": "Vijayawada", "bus": "Deccan Queen", "departure": "13:00", "arrival": "17:00"},
    {"from": "Kolkata", "to": "Durgapur", "bus": "Eastern Star", "departure": "10:00", "arrival": "13:00"},
]

BOOKINGS_FILE = "bookings.json"

# --- Backend-like persistence ---
def load_bookings():
    if not os.path.exists(BOOKINGS_FILE):
        return []
    with open(BOOKINGS_FILE, 'r') as f:
        return json.load(f)

def save_bookings(bookings):
    with open(BOOKINGS_FILE, 'w') as f:
        json.dump(bookings, f, indent=2)

def add_booking(booking):
    bookings = load_bookings()
    bookings.append(booking)
    save_bookings(bookings)

def delete_booking(index):
    bookings = load_bookings()
    if 0 <= index < len(bookings):
        bookings.pop(index)
        save_bookings(bookings)

# --- Streamlit session state setup ---
if 'username' not in st.session_state:
    st.session_state.username = None

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# --- Helper functions ---
def format_booking(b):
    return f"{b['date']}: {b['from']} → {b['to']} on {b['bus']}"

def user_login():
    st.sidebar.subheader("User Login")
    if st.session_state.username:
        st.sidebar.write(f"Logged in as **{st.session_state.username}**")
        if st.sidebar.button("Logout"):
            st.session_state.username = None
    else:
        username = st.sidebar.text_input("Enter username")
        if st.sidebar.button("Login"):
            if username.strip():
                st.session_state.username = username.strip()
                st.success(f"Welcome, {st.session_state.username}!")
            else:
                st.error("Please enter a valid username.")

def main_app():
    st.title("🚌 Indian Bus Finder App")

    menu = st.sidebar.radio("Menu", ["Home", "Routes", "My Bookings", "Track Bus", "Search History"])

    if menu == "Home":
        st.subheader("🔍 Find Your Bus")
        from_city = st.selectbox("From", sorted({r["from"] for r in ROUTES}))
        to_city = st.selectbox("To", sorted({r["to"] for r in ROUTES}))
        journey_date = st.date_input("Journey Date", min_value=date.today())

        if st.button("Search Buses"):
            results = [r for r in ROUTES if r["from"] == from_city and r["to"] == to_city]
            st.session_state.search_history.append({
                "from": from_city,
                "to": to_city,
                "date": str(journey_date),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            if results:
                st.success(f"{len(results)} route(s) found")
                for r in results:
                    st.markdown(f"**{r['bus']}**: {r['from']} → {r['to']} | {r['departure']} - {r['arrival']}")
                    if st.button(f"Book {r['bus']}", key=f"book_{r['bus']}_{journey_date}"):
                        booking = {
                            "user": st.session_state.username or "Guest",
                            "from": r['from'],
                            "to": r['to'],
                            "date": str(journey_date),
                            "bus": r['bus']
                        }
                        add_booking(booking)
                        st.success("✅ Booking confirmed!")

        # Show summary on home
        all_bookings = load_bookings()
        st.markdown("---")
        st.write(f"**Total Bookings in System:** {len(all_bookings)}")
        recent = all_bookings[-5:] if all_bookings else []
        if recent:
            st.write("**Recent Bookings:**")
            for b in recent:
                st.write(format_booking(b))

    elif menu == "Routes":
        st.subheader("🛣 Available Routes")
        for r in ROUTES:
            st.markdown(f"- **{r['from']} → {r['to']}** | {r['bus']} | {r['departure']} → {r['arrival']}")

    elif menu == "My Bookings":
        st.subheader("📒 My Bookings")
        bookings = load_bookings()
        user_bookings = [b for b in bookings if b.get("user") == (st.session_state.username or "Guest")]

        if not user_bookings:
            st.info("You have no bookings yet.")
        else:
            # Filter by date range
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=date(2000,1,1), key="start_date")
            with col2:
                end_date = st.date_input("End Date", value=date.today(), key="end_date")

            filtered = [b for b in user_bookings if start_date <= datetime.strptime(b["date"], "%Y-%m-%d").date() <= end_date]

            for idx, b in enumerate(filtered):
                st.markdown(f"- {format_booking(b)}")
                if st.button("Cancel Booking", key=f"cancel_{idx}"):
                    # Find index in main booking list and delete
                    all_bookings = load_bookings()
                    real_index = next((i for i, x in enumerate(all_bookings) if x == b), None)
                    if real_index is not None:
                        delete_booking(real_index)
                        st.success("Booking cancelled!")
                        st.experimental_rerun()

    elif menu == "Track Bus":
        st.subheader("📍 Bus Tracker")
        st.info("Simulated tracking: Your bus is currently en route and will arrive on time. 🚍")

    elif menu == "Search History":
        st.subheader("🔎 Search History (This Session)")
        if st.session_state.search_history:
            for h in reversed(st.session_state.search_history[-10:]):
                st.write(f"{h['timestamp']}: {h['from']} → {h['to']} on {h['date']}")
        else:
            st.info("No searches yet this session.")

if __name__ == "__main__":
    user_login()
    main_app()
