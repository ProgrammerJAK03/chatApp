# import streamlit as st
# import mysql.connector
# import time
# import os
# from dotenv import load_dotenv
# from streamlit_autorefresh import st_autorefresh

# # ✅ Connect to MySQL
# def connect_db():
#     load_dotenv()

#     # Fetch environment variables
#     host = os.getenv("DB_HOST")  # Make sure this points to the correct IP address or localhost
#     user = os.getenv("DB_USER")
#     password = os.getenv("DB_PASSWORD")
#     database = os.getenv("DB_NAME")

#     # Display for debugging purpose
#     st.write(f"Connecting to DB with: Host={host}, User={user}, Database={database}")

#     return mysql.connector.connect(
#         host=host,
#         user=user,
#         password=password,
#         database=database
#     )

# # ✅ Establish DB Connection
# conn = connect_db()
# cursor = conn.cursor()

# # ✅ Create Tables (Users, Messages, Contacts)
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255) NOT NULL,
#         phone VARCHAR(11) NOT NULL UNIQUE,
#         is_online BOOLEAN DEFAULT FALSE,
#         last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
#     )
# ''')
# conn.commit()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS messages (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         sender_phone VARCHAR(11),
#         receiver_phone VARCHAR(11),
#         message TEXT,
#         timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         FOREIGN KEY (sender_phone) REFERENCES users(phone),
#         FOREIGN KEY (receiver_phone) REFERENCES users(phone)
#     )
# ''')
# conn.commit()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS contacts (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         user_phone VARCHAR(11) NOT NULL,
#         contact_phone VARCHAR(11) NOT NULL,
#         contact_name VARCHAR(255) DEFAULT NULL,
#         UNIQUE KEY unique_contact (user_phone, contact_phone),
#         FOREIGN KEY (user_phone) REFERENCES users(phone),
#         FOREIGN KEY (contact_phone) REFERENCES users(phone)
#     )
# ''')
# conn.commit()

# # ✅ Update Last Seen & Online Status
# def update_last_seen(phone, is_online=True):
#     cursor.execute("UPDATE users SET last_seen = NOW(), is_online = %s WHERE phone = %s", (is_online, phone))
#     conn.commit()

# # ✅ Save Contact Function
# def save_contact(user_phone, contact_phone):
#     try:
#         cursor.execute("INSERT INTO contacts (user_phone, contact_phone) VALUES (%s, %s)", (user_phone, contact_phone))
#         conn.commit()
#     except mysql.connector.IntegrityError:
#         pass

# # ✅ Fetch Contacts from Database
# def get_saved_contacts(user_phone):
#     cursor.execute("SELECT contact_phone, contact_name FROM contacts WHERE user_phone = %s", (user_phone,))
#     return dict(cursor.fetchall())

# # ✅ Streamlit UI Configuration
# st.set_page_config(page_title="Chat App", layout="wide")
# st.title("💬 Secure MySQL Chat App")

# # ✅ Auto-Refresh
# st_autorefresh(interval=3000, key="refresh")  # Refresh every 3 seconds

# # ✅ Sidebar Settings (User Name & Logout)
# if "user_phone" in st.session_state:
#     with st.sidebar.expander("⚙️ Settings"):
#         st.write(f"👤 Name: **{st.session_state.get('user_name', 'Unknown')}**")  
#         st.write(f"📞 Phone Number: **{st.session_state.get('user_phone', 'N/A')}**")

#         new_name = st.text_input("Update your name:")

#         # Save Name Button
#         if st.button("Save Name", key="save_name_btn"):
#             cursor.execute("UPDATE users SET name = %s WHERE phone = %s", (new_name, st.session_state.user_phone))
#             conn.commit()
#             st.session_state.user_name = new_name
#             st.success("Name updated!")

#         # Logout Button
#         if st.button("Logout", key="logout_btn"):
#             update_last_seen(st.session_state.user_phone, is_online=False)
#             st.session_state.clear()
#             st.rerun()

# # ✅ Login & Sign-Up Handling
# if "user_phone" not in st.session_state:
#     with st.form("user_form"):
#         name = st.text_input("Enter your name:")
#         phone = st.text_input("Enter your 11-digit phone number:", max_chars=11)
#         submit_user = st.form_submit_button("Continue")

#     if submit_user:
#         if len(phone) == 11 and phone.isdigit():
#             try:
#                 cursor.execute("INSERT INTO users (name, phone, is_online) VALUES (%s, %s, TRUE)", (name, phone))
#                 conn.commit()
#                 st.session_state.user_name = name
#                 st.success("User registered successfully!")
                
#             except mysql.connector.IntegrityError:
#                 cursor.execute("SELECT name FROM users WHERE phone = %s", (phone,))
#                 result = cursor.fetchone()
#                 if result:
#                     st.session_state.user_name = result[0]
#                 st.info("Phone number already registered. Logging you in!")

#             st.session_state.user_phone = phone
#             update_last_seen(phone, is_online=True)
#             st.rerun()
#         else:
#             st.error("Please enter a valid 11-digit phone number.")

# if "user_phone" not in st.session_state:
#     st.warning("🚫 Please Sign Up or Login to use chat features!")
#     st.stop()

# phone = st.session_state.user_phone

# # ✅ Fetch Saved Contacts
# st.session_state.saved_contacts = get_saved_contacts(phone)

# # ✅ Sidebar: Username
# st.sidebar.subheader(f"👤 **{st.session_state.get('user_name', 'Unknown')}**")

# # ✅ Sidebar: Saved Contacts
# st.sidebar.subheader("📞 Saved Contacts")

# receiver_phone_input = st.sidebar.text_input("Enter receiver's phone number:", max_chars=11)

# if receiver_phone_input and len(receiver_phone_input) == 11 and receiver_phone_input.isdigit():
#     if receiver_phone_input not in st.session_state.saved_contacts:
#         save_contact(phone, receiver_phone_input)
#         st.session_state.saved_contacts = get_saved_contacts(phone)  # Refresh contacts list
#     receiver_phone = receiver_phone_input
# else:
#     receiver_phone = None

# # ✅ Fetch Unread Messages
# def get_unread_messages():
#     cursor.execute(
#         "SELECT sender_phone, COUNT(*) FROM messages WHERE receiver_phone = %s AND timestamp > NOW() - INTERVAL 1 MINUTE GROUP BY sender_phone",
#         (phone,)
#     )
#     return dict(cursor.fetchall())

# unread_messages = get_unread_messages()

# # ✅ Get User Online Status
# def get_user_status(phone):
#     cursor.execute("SELECT is_online, last_seen FROM users WHERE phone = %s", (phone,))
#     result = cursor.fetchone()
#     if result:
#         is_online, last_seen = result
#         if is_online:
#             return "🟢 Online"
#         time_diff = (time.time() - last_seen.timestamp()) / 60
#         return f"🔴 Last seen {int(time_diff)} min ago"
#     return "🔴 Offline"

# # ✅ Display Contacts
# for number, contact_name in st.session_state.saved_contacts.items():
#     col1, col2, col3 = st.sidebar.columns([1, 5, 1])
#     with col1:
#         st.write("📱")
#     with col2:
#         status = get_user_status(number)
#         notification_badge = f" **({unread_messages.get(number, 0)})**" if unread_messages.get(number) else ""
#         contact_display = f"**{contact_name if contact_name else 'Unknown'}**  \n{number}{notification_badge}\n{status}"
#         if st.button(contact_display, key=f"select_{number}"):
#             st.session_state["selected_receiver"] = number
#             st.rerun()
#     with col3:
#         if st.button("✏️", key=f"edit_{number}"):
#             st.session_state["edit_contact"] = number

# # ✅ Edit Contact Info
# if "edit_contact" in st.session_state:
#     contact = st.session_state["edit_contact"]
#     new_name = st.text_input(f"Enter new name for {contact}:")
#     if st.button("Save", key="save_contact_name"):
#         cursor.execute("UPDATE contacts SET contact_name = %s WHERE contact_phone = %s", (new_name, contact))
#         conn.commit()
#         st.session_state.saved_contacts = get_saved_contacts(phone)  # Refresh contacts
#         st.success(f"Name updated for {contact}!")
#         st.session_state.pop("edit_contact")

# # ✅ Chat & Messages
# if receiver_phone:
#     st.write(f"💬 Chat with {receiver_phone}")
#     # Fetch messages
#     cursor.execute("SELECT sender_phone, message, timestamp FROM messages WHERE (sender_phone = %s AND receiver_phone = %s) OR (sender_phone = %s AND receiver_phone = %s) ORDER BY timestamp ASC", (phone, receiver_phone, receiver_phone, phone))
#     messages = cursor.fetchall()
    
#     for msg in messages:
#         sender, message, timestamp = msg
#         direction = "You" if sender == phone else receiver_phone
#         st.write(f"**{direction}:** {message} ({timestamp})")

#     # Send Message Input
#     message = st.text_input("Enter your message:")
#     if st.button("Send", key="send_message"):
#         cursor.execute("INSERT INTO messages (sender_phone, receiver_phone, message) VALUES (%s, %s, %s)", (phone, receiver_phone, message))
#         conn.commit()
#         st.text_input("Enter your message:", value="")
#         st.experimental_rerun()
import streamlit as st
import mysql.connector
import time
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

# ✅ THIS MUST BE RIGHT HERE – NOTHING STREAMLIT BEFORE IT
st.set_page_config(page_title="Chat App", layout="wide")  # ✅ CORRECT

# ✅ Load environment variables
load_dotenv()

# (your DB connection and app logic follows)


# import streamlit as st
# import mysql.connector
# import time
# import os
# from dotenv import load_dotenv
# from streamlit_autorefresh import st_autorefresh

# # ✅ Load .env (if used)
# load_dotenv()

# ✅ Database Connection
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="NewPasswordHere",
#         database="chatapp01"
#     )
def connect_db():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        st.stop()
st.write("Connecting to DB:", os.getenv("DB_HOST"))

conn = connect_db()
cursor = conn.cursor()

# ✅ Create Tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        phone VARCHAR(11) UNIQUE,
        is_online BOOLEAN DEFAULT FALSE,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sender_phone VARCHAR(11),
        receiver_phone VARCHAR(11),
        message TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_phone) REFERENCES users(phone),
        FOREIGN KEY (receiver_phone) REFERENCES users(phone)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_phone VARCHAR(11),
        contact_phone VARCHAR(11),
        contact_name VARCHAR(255),
        UNIQUE(user_phone, contact_phone),
        FOREIGN KEY (user_phone) REFERENCES users(phone),
        FOREIGN KEY (contact_phone) REFERENCES users(phone)
    )
''')
conn.commit()

# ✅ Utility Functions
def update_last_seen(phone, is_online=True):
    cursor.execute("UPDATE users SET last_seen = NOW(), is_online = %s WHERE phone = %s", (is_online, phone))
    conn.commit()

def signup_user(name, phone):
    try:
        cursor.execute("INSERT INTO users (name, phone, is_online) VALUES (%s, %s, TRUE)", (name, phone))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False

def login_user(phone):
    cursor.execute("SELECT name FROM users WHERE phone = %s", (phone,))
    result = cursor.fetchone()
    return result[0] if result else None

def save_contact(user_phone, contact_phone):
    try:
        cursor.execute("INSERT INTO contacts (user_phone, contact_phone) VALUES (%s, %s)", (user_phone, contact_phone))
        conn.commit()
    except mysql.connector.IntegrityError:
        pass

def get_saved_contacts(user_phone):
    cursor.execute("SELECT contact_phone, contact_name FROM contacts WHERE user_phone = %s", (user_phone,))
    return dict(cursor.fetchall())

def get_user_status(phone):
    cursor.execute("SELECT is_online, last_seen FROM users WHERE phone = %s", (phone,))
    result = cursor.fetchone()
    if result:
        is_online, last_seen = result
        if is_online:
            return "🟢 Online"
        mins = int((time.time() - last_seen.timestamp()) / 60)
        return f"🔴 Last seen {mins} min ago"
    return "🔴 Offline"

def get_unread_messages(user_phone):
    cursor.execute(
        "SELECT sender_phone, COUNT(*) FROM messages WHERE receiver_phone = %s AND timestamp > NOW() - INTERVAL 1 MINUTE GROUP BY sender_phone",
        (user_phone,)
    )
    return dict(cursor.fetchall())

def get_messages(user, receiver):
    cursor.execute(
        "SELECT sender_phone, message, timestamp FROM messages WHERE (sender_phone = %s AND receiver_phone = %s) OR (sender_phone = %s AND receiver_phone = %s) ORDER BY timestamp ASC",
        (user, receiver, receiver, user)
    )
    return cursor.fetchall()

# ✅ Page Config
# st.set_page_config("Chat App", layout="wide")
st.title("💬 Secure MySQL Chat App")
st_autorefresh(interval=3000, key="autorefresh")

# ✅ Signup/Login Section
if "user_phone" not in st.session_state:
    st.subheader("🔐 Login / Signup")

    with st.form("auth_form"):
        name = st.text_input("Your Name (for signup)")
        phone = st.text_input("11-digit Phone Number", max_chars=11)
        option = st.radio("Choose Action", ["Login", "Signup"])
        submit = st.form_submit_button("Continue")

    if submit:
        if phone.isdigit() and len(phone) == 11:
            if option == "Signup":
                if signup_user(name, phone):
                    st.session_state.user_name = name
                    st.session_state.user_phone = phone
                    update_last_seen(phone)
                    st.success("✅ Signup successful!")
                    st.rerun()
                else:
                    st.warning("⚠️ Already registered.")
            else:
                name_fetched = login_user(phone)
                if name_fetched:
                    st.session_state.user_name = name_fetched
                    st.session_state.user_phone = phone
                    update_last_seen(phone)
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Phone not found.")
        else:
            st.error("📵 Invalid phone number.")
    st.stop()

# ✅ App Main (If Logged In)
phone = st.session_state.user_phone
name = st.session_state.user_name
update_last_seen(phone)

# ✅ Sidebar - Profile
with st.sidebar:
    st.markdown(f"### 👤 {name}")
    st.markdown(f"**📱 {phone}**")
    
    new_name = st.text_input("Update your name:")
    if st.button("Save Name"):
        cursor.execute("UPDATE users SET name = %s WHERE phone = %s", (new_name, phone))
        conn.commit()
        st.session_state.user_name = new_name
        st.success("Name updated!")

    if st.button("Logout"):
        update_last_seen(phone, is_online=False)
        st.session_state.clear()
        st.rerun()

# ✅ Sidebar - Contacts
st.sidebar.subheader("📞 Contacts")
receiver_input = st.sidebar.text_input("Add contact phone:", max_chars=11)
if receiver_input and receiver_input != phone and receiver_input.isdigit():
    save_contact(phone, receiver_input)

contacts = get_saved_contacts(phone)
unread = get_unread_messages(phone)

for c_phone, c_name in contacts.items():
    col1, col2, col3 = st.sidebar.columns([1, 6, 1])
    with col1:
        st.write("📱")
    with col2:
        status = get_user_status(c_phone)
        badge = f" **({unread.get(c_phone, 0)})**" if unread.get(c_phone) else ""
        display = f"**{c_name or 'Unknown'}**\n{c_phone}{badge}\n{status}"
        if st.button(display, key=f"btn_{c_phone}"):
            st.session_state.selected_receiver = c_phone
            st.rerun()
    with col3:
        if st.button("✏️", key=f"edit_{c_phone}"):
            st.session_state.edit_contact = c_phone

# ✅ Edit Contact Name
if "edit_contact" in st.session_state:
    with st.sidebar.expander("Edit Contact"):
        editing = st.session_state.edit_contact
        new_contact_name = st.text_input("New name:", value=contacts.get(editing, ""))
        if st.button("Save Contact Name"):
            cursor.execute("UPDATE contacts SET contact_name = %s WHERE user_phone = %s AND contact_phone = %s", (new_contact_name, phone, editing))
            conn.commit()
            del st.session_state.edit_contact
            st.rerun()

# ✅ Chat Section
receiver = st.session_state.get("selected_receiver")
if receiver:
    receiver_name = contacts.get(receiver, "Unknown")
    st.subheader(f"Chat with {receiver_name} ({receiver}) - {get_user_status(receiver)}")

    chat = get_messages(phone, receiver)
    # for msg in chat:
    #     sender = "You" if msg[0] == phone else receiver_name or msg[0]
    #     st.markdown(f"**{sender}**: {msg[1]}  \n*🕒 {msg[2]}*")
    for msg in chat:
        sender = "You" if msg[0] == phone else receiver_name or msg[0]
        if msg[0] == phone:
            st.markdown(f'''
            <div style="text-align: right; background-color: #e0ffe0; padding: 8px; border-radius: 10px; margin: 5px;">
                <strong style="color: green;">{sender}</strong>: {msg[1]}<br>
                <small><em>🕒 {msg[2]}</em></small>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div style="text-align: left; background-color: #e6f0ff; padding: 8px; border-radius: 10px; margin: 5px;">
                <strong style="color: blue;">{sender}</strong>: {msg[1]}<br>
                <small><em>🕒 {msg[2]}</em></small>
            </div>
            ''', unsafe_allow_html=True)

    # msg_text = st.text_input("Type your message:")
    # if st.button("Send"):
    #     if msg_text.strip():
    #         cursor.execute("INSERT INTO messages (sender_phone, receiver_phone, message) VALUES (%s, %s, %s)", (phone, receiver, msg_text))
    #         conn.commit()
    #         st.rerun()
    col1, col2 = st.columns([5, 1])
    with col1:
        msg_text = st.text_input("Type your message:", label_visibility="collapsed")
    with col2:
        if st.button("Send"):
            if msg_text.strip():
                cursor.execute(
                    "INSERT INTO messages (sender_phone, receiver_phone, message) VALUES (%s, %s, %s)",
                    (phone, receiver, msg_text)
                )
                conn.commit()
                st.rerun()