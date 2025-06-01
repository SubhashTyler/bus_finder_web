import streamlit as st
import json
import os
from datetime import date, datetime, timedelta
import pandas as pd

# ---------- Data & Backend ----------

ROUTES = [
    {"from": "Mumbai", "to": "Pune", "bus": "Shivneri Express", "departure": "07:00", "arrival": "10:00"},
    {"from": "Delhi", "to": "Agra", "bus": "Rajdhani Express", "departure": "09:00", "arrival": "12:00"},
    {"from": "Bangalore", "to": "Mysore", "bus": "Kaveri Deluxe", "departure": "06:30", "arrival": "09:30"},
    {"from": "Chennai", "to": "Tirupati", "bus": "Godavari Express", "departure": "08:00", "arrival": "11:00"},
    {"from": "Hyderabad", "to": "Vijayawada", "bus": "Deccan Queen", "departure": "13:00", "arrival": "17:00"},
    {"from": "Kolkata", "to": "Durgapur", "bus": "Eastern Star", "departure": "10:00", "arrival": "13:00"},
]

BOOKINGS_FILE = "bookings.json"

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

# ---------- Session State Initialization ----------

if 'username' not in st.session_state:
    st.session_state.username = None

if 'search_history' not in st.session_state:
    st.session_state.search_history = []

if 'user_bookings' not in st.session_state:
    st.session_state.user_bookings = []

# ---------- Helper Functions ----------

def format_booking(b):
    return f"{b['date']} | {b['from']} → {b['to']} | {b['bus']}"

def upcoming_booking_alerts(bookings):
    alerts = []
    today = date.today()
    for b in bookings:
        b_date = datetime.strptime(b['date'], "%Y-%m-%d").date()
        if today <= b_date <= today + timedelta(days=3):
            alerts.append(f"Upcoming trip on {b_date} from {b['from']} to {b['to']} by {b['bus']}")
    return alerts

def user_login():
    st.sidebar.header("User Login")
    if st.session_state.username:
        st.sidebar.markdown(f"**Logged in as:** {st.session_state.username}")
        if st.sidebar.button("Logout"):
            st.session_state.username = None
            st.session_state.user_bookings = []
            st.experimental_rerun()
    else:
        username = st.sidebar.text_input("Enter username")
        if st.sidebar.button("Login"):
            if username.strip():
                st.session_state.username = username.strip()
                # Load user bookings on login
                st.session_state.user_bookings = [
                    b for b in load_bookings() if b.get("user") == st.session_state.username
                ]
                st.success(f"Welcome, {st.session_state.username}!")
            else:
                st.error("Please enter a valid username.")

# ---------- Main App ----------

def main_app():
    st.title("🚌 Indian Bus Finder & Booking App")

    menu = st.sidebar.radio("Menu", ["Home", "Routes", "My Bookings", "Track Bus", "Search History", "User Profile"])

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
                        # Update session state for instant booking update
                        st.session_state.user_bookings = [
                            b for b in load_bookings() if b.get("user") == booking["user"]
                        ]
                        st.success("✅ Booking confirmed!")

        # Summary of recent & total bookings
        all_bookings = load_bookings()
        st.markdown("---")
        st.write(f"**Total Bookings in System:** {len(all_bookings)}")
        recent = all_bookings[-5:] if all_bookings else []
        if recent:
            st.write("**Recent Bookings:**")
            for b in recent:
                st.write(format_booking(b))

        # Upcoming trip alerts for logged-in user
        if st.session_state.username:
            alerts = upcoming_booking_alerts(st.session_state.user_bookings)
            if alerts:
                st.info("🔔 Upcoming Trips:")
                for alert in alerts:
                    st.write(f"- {alert}")

    elif menu == "Routes":
        st.subheader("🛣 Available Routes")
        for r in ROUTES:
            st.markdown(f"- **{r['from']} → {r['to']}** | {r['bus']} | {r['departure']} → {r['arrival']}")

    elif menu == "My Bookings":
        st.subheader("📒 My Bookings")
        if not st.session_state.username:
            st.warning("Please login to see your bookings.")
            return

        bookings = st.session_state.user_bookings
        if not bookings:
            st.info("You have no bookings yet.")
        else:
            # Filter & sort options
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=date(2000,1,1), key="start_date_mb")
            with col2:
                end_date = st.date_input("End Date", value=date.today() + timedelta(days=365), key="end_date_mb")

            sort_by = st.selectbox("Sort by", ["Date Ascending", "Date Descending", "Bus Name"], key="sort_bookings")

            filtered = [b for b in bookings if start_date <= datetime.strptime(b["date"], "%Y-%m-%d").date() <= end_date]

            if sort_by == "Date Ascending":
                filtered.sort(key=lambda x: x["date"])
            elif sort_by == "Date Descending":
                filtered.sort(key=lambda x: x["date"], reverse=True)
            elif sort_by == "Bus Name":
                filtered.sort(key=lambda x: x["bus"])

            for idx, b in enumerate(filtered):
                st.markdown(f"- {format_booking(b)}")
                if st.button("Cancel Booking", key=f"cancel_{idx}"):
                    # Delete from backend
                    all_bookings = load_bookings()
                    real_index = next((i for i, x in enumerate(all_bookings) if x == b), None)
                    if real_index is not None:
                        delete_booking(real_index)
                        st.session_state.user_bookings = [
                            bk for bk in load_bookings() if bk.get("user") == st.session_state.username
                        ]
                        st.success("Booking cancelled!")
                        st.experimental_rerun()

            # Export bookings as CSV
            if filtered:
                df = pd.DataFrame(filtered)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Bookings CSV",
                    data=csv,
                    file_name='my_bookings.csv',
                    mime='text/csv'
                )

    elif menu == "Track Bus":
        st.subheader("📍 Bus Tracker")
        st.info("Simulated tracking status updates:")
        bus_list = sorted({r['bus'] for r in ROUTES})
        selected_bus = st.selectbox("Select Bus to Track", bus_list)
        # Simulate status with some random logic or fixed statuses
        import random
        statuses = [
            "On Time 🟢",
            "Running Late 🟠",
            "Delayed 🔴",
            "Reached Destination ✅",
            "Scheduled to Depart 🕒"
        ]
        status = random.choice(statuses)
        st.markdown(f"**{selected_bus} status:** {status}")

    elif menu == "Search History":
        st.subheader("🔎 Search History (This Session)")
        if st.session_state.search_history:
            for h in reversed(st.session_state.search_history[-10:]):
                st.write(f"{h['timestamp']}: {h['from']} → {h['to']} on {h['date']}")
        else:
            st.info("No searches yet this session.")

    elif menu == "User Profile":
        st.subheader("👤 User Profile")
        if not st.session_state.username:
            st.warning("Please login to view your profile.")
            return
        st.markdown(f"**Username:** {st.session_state.username}")
        user_bkgs = st.session_state.user_bookings
        st.markdown(f"**Total Bookings:** {len(user_bkgs)}")
        upcoming = upcoming_booking_alerts(user_bkgs)
        if upcoming:
            st.markdown("### Upcoming Trips:")
            for trip in upcoming:
                st.write(f"- {trip}")
        else:
            st.info("No upcoming trips.")

if __name__ == "__main__":
    st.set_page_config(page_title="Bus Finder App", layout="wide")
    user_login()
    main_app()
