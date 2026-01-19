import os
import webbrowser
import json
import requests
import random
import smtplib
import ssl
from email.message import EmailMessage
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.fitimage import FitImage
from kivymd.uix.filemanager import MDFileManager
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp

# --- CONFIGURATION ---
FIREBASE_URL = "https://missing-alert-system-default-rtdb.firebaseio.com/"

# --- ⚠️ PASTE YOUR DETAILS HERE ⚠️ ---
SENDER_EMAIL = "milansaji2705@gmail.com"  
SENDER_PASSWORD = "pqpksybccdhnrjbt" # 16 letters, no spaces

# --- LIBRARIES CHECK ---
try:
    from plyer import notification
except ImportError:
    notification = None
try:
    from geopy.geocoders import Nominatim
except ImportError:
    Nominatim = None
try:
    from kivy_garden.mapview import MapView
except ImportError:
    MapView = None

Window.size = (360, 750)

KV = '''
ScreenManager:
    LoginScreen:
    SignUpScreen:
    SignupMapScreen:
    OtpScreen:
    HomeScreen:
    LocationScreen:
    DetailsScreen:
    SightingScreen:

# 1. LOGIN SCREEN
<LoginScreen>:
    name: "login_screen"
    MDBoxLayout:
        orientation: "vertical"
        padding: "30dp"
        spacing: "20dp"
        adaptive_height: True
        pos_hint: {"center_x": .5, "center_y": .5}
        
        MDLabel:
            text: "Missing Alert App"
            halign: "center"
            font_style: "H4"

        MDTextField:
            id: email
            hint_text: "Email"
            mode: "rectangle"

        MDTextField:
            id: password
            hint_text: "Password"
            password: True
            mode: "rectangle"

        MDRaisedButton:
            text: "LOGIN"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 1, 0, 0, 1
            size_hint_x: 1
            on_release: root.do_login()

        MDFlatButton:
            text: "Don't have an account? Sign Up"
            pos_hint: {"center_x": 0.5}
            theme_text_color: "Custom"
            text_color: 0, 0, 1, 1
            on_release: app.root.current = "signup_screen"

# 2. SIGN UP SCREEN
<SignUpScreen>:
    name: "signup_screen"
    MDBoxLayout:
        orientation: "vertical"
        
        MDTopAppBar:
            title: "Create Account"
            md_bg_color: 1, 0, 0, 1
            left_action_items: [["arrow-left", lambda x: root.go_back()]]

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "15dp"
                adaptive_height: True

                MDTextField:
                    id: new_name
                    hint_text: "Full Name"
                    mode: "rectangle"

                # ID CARD UPLOAD
                MDCard:
                    size_hint_y: None
                    height: "80dp"
                    orientation: "vertical"
                    padding: "10dp"
                    md_bg_color: 0.95, 0.95, 0.95, 1
                    elevation: 1
                    
                    MDLabel:
                        id: id_photo_status
                        text: "Upload ID Proof (Aadhar/PAN)"
                        halign: "center"
                        theme_text_color: "Secondary"
                        font_style: "Caption"
                    
                    MDRaisedButton:
                        text: "SELECT ID IMAGE"
                        pos_hint: {"center_x": .5}
                        md_bg_color: 0.3, 0.3, 0.3, 1
                        on_release: root.open_file_manager()

                MDTextField:
                    id: new_mobile
                    hint_text: "Mobile Number"
                    input_filter: "int"
                    mode: "rectangle"

                MDTextField:
                    id: new_email
                    hint_text: "Email Address (For OTP)"
                    mode: "rectangle"

                MDTextField:
                    id: new_password
                    hint_text: "Create Password"
                    password: True
                    mode: "rectangle"

                # LOCATION PICKER
                MDLabel:
                    text: "Home/Base Location:"
                    theme_text_color: "Secondary"
                    font_style: "Caption"
                
                MDCard:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    padding: "5dp"
                    spacing: "10dp"
                    on_release: root.open_map_picker()
                    elevation: 1

                    MDIcon:
                        icon: "map-marker"
                        theme_text_color: "Custom"
                        text_color: 1, 0, 0, 1
                        pos_hint: {"center_y": .5}

                    MDLabel:
                        id: location_label
                        text: "Tap to Pick Location on Map"
                        theme_text_color: "Primary"
                        valign: "center"

                MDRaisedButton:
                    text: "SEND EMAIL OTP"
                    pos_hint: {"center_x": 0.5}
                    md_bg_color: 0, 0.6, 0, 1
                    size_hint_x: 1
                    on_release: root.send_otp_step()

# 3. OTP SCREEN (WITH RESEND TIMER)
<OtpScreen>:
    name: "otp_screen"
    on_enter: root.start_timer()
    MDBoxLayout:
        orientation: "vertical"
        padding: "40dp"
        spacing: "20dp"
        adaptive_height: True
        pos_hint: {"center_x": .5, "center_y": .5}

        MDIcon:
            icon: "email-check"
            font_size: "80sp"
            pos_hint: {"center_x": .5}
            theme_text_color: "Custom"
            text_color: 0, 0.6, 0, 1

        MDLabel:
            text: "Verify Email"
            halign: "center"
            font_style: "H5"

        MDLabel:
            id: otp_msg
            text: "We sent a 4-digit code to your email."
            halign: "center"
            theme_text_color: "Secondary"
            font_style: "Caption"

        MDTextField:
            id: otp_input
            hint_text: "Enter OTP"
            input_filter: "int"
            mode: "rectangle"
            halign: "center"
            font_size: "24sp"

        MDRaisedButton:
            text: "VERIFY & REGISTER"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0, 0.6, 0, 1
            size_hint_x: 1
            on_release: root.verify_otp()

        # RESEND BUTTON
        MDFlatButton:
            id: resend_btn
            text: "Resend in 20s"
            pos_hint: {"center_x": 0.5}
            disabled: True
            theme_text_color: "Custom"
            text_color: 0, 0, 0.8, 1
            on_release: root.do_resend()

        MDFlatButton:
            text: "Cancel"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "signup_screen"

# 4. SIGNUP MAP SCREEN
<SignupMapScreen>:
    name: "signup_map_screen"
    MDBoxLayout:
        orientation: "vertical"
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "50dp"
            padding: "5dp"
            spacing: "5dp"
            md_bg_color: 1, 1, 1, 1
            MDTextField:
                id: search_field
                hint_text: "Search (e.g. Kochi)"
                mode: "rectangle"
                size_hint_x: 0.8
            MDIconButton:
                icon: "magnify"
                on_release: root.search_location()
        MDRelativeLayout:
            size_hint_y: 1
            MapView:
                id: map_view
                lat: 9.9312
                lon: 76.2673
                zoom: 10
            MDIcon:
                icon: "home-map-marker"
                theme_text_color: "Custom"
                text_color: 0, 0, 1, 1
                pos_hint: {"center_x": .5, "center_y": .5}
                font_size: "40sp"
        MDRaisedButton:
            text: "CONFIRM THIS LOCATION"
            size_hint_x: 1
            md_bg_color: 0, 0.6, 0, 1
            on_release: root.confirm_location()

# 5. HOME SCREEN
<HomeScreen>:
    name: "home_screen"
    on_enter: root.on_enter_actions()
    
    MDBottomNavigation:
        selected_color_background: 0, 0, 0, 0
        text_color_active: 1, 0, 0, 1

        MDBottomNavigationItem:
            name: "screen_home"
            text: "Live"
            icon: "home"
            MDBoxLayout:
                orientation: "vertical"
                MDTopAppBar:
                    title: "Live Reports"
                    md_bg_color: 1, 0, 0, 1
                    right_action_items: [["refresh", lambda x: root.load_online_reports()]]
                MDScrollView:
                    MDBoxLayout:
                        id: report_list
                        orientation: "vertical"
                        padding: "10dp"
                        spacing: "15dp"
                        size_hint_y: None
                        height: self.minimum_height
                MDFloatingActionButton:
                    icon: "plus"
                    md_bg_color: 1, 0, 0, 1
                    pos_hint: {"right": .95}
                    on_release: app.root.current = "location_screen"
                    MDBoxLayout:
                        size_hint_y: None
                        height: "10dp"

        MDBottomNavigationItem:
            name: "screen_solved"
            text: "Solved"
            icon: "check-circle"
            MDBoxLayout:
                orientation: "vertical"
                MDTopAppBar:
                    title: "Solved Cases"
                    md_bg_color: 0, 0.6, 0, 1
                MDScrollView:
                    MDBoxLayout:
                        id: solved_list
                        orientation: "vertical"
                        padding: "10dp"
                        spacing: "15dp"
                        size_hint_y: None
                        height: self.minimum_height
                        MDLabel:
                            text: "No solved cases yet."
                            halign: "center"
                            theme_text_color: "Secondary"
                            size_hint_y: None
                            height: "50dp"

        MDBottomNavigationItem:
            name: "screen_account"
            text: "Account"
            icon: "account"
            MDBoxLayout:
                orientation: "vertical"
                padding: "20dp"
                spacing: "20dp"
                MDTopAppBar:
                    title: "My Profile"
                    md_bg_color: 0.2, 0.2, 0.2, 1
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    pos_hint: {"center_y": .5}
                    spacing: "10dp"
                    MDIcon:
                        icon: "account-circle"
                        font_size: "100sp"
                        pos_hint: {"center_x": .5}
                        theme_text_color: "Custom"
                        text_color: 0.5, 0.5, 0.5, 1
                    MDLabel:
                        id: user_email_label
                        text: "user@email.com"
                        halign: "center"
                        font_style: "H5"
                    MDLabel:
                        text: "Verified Volunteer"
                        halign: "center"
                        theme_text_color: "Secondary"
                    MDRaisedButton:
                        text: "LOGOUT"
                        md_bg_color: 1, 0, 0, 1
                        pos_hint: {"center_x": .5}
                        on_release: app.root.current = "login_screen"
                MDWidget:

# 6. REPORT LOCATION SCREEN
<LocationScreen>:
    name: "location_screen"
    MDBoxLayout:
        orientation: "vertical"
        padding: "10dp"
        spacing: "10dp"
        MDLabel:
            text: "Step 1: Location"
            halign: "center"
            font_style: "H6"
            size_hint_y: None
            height: "30dp"
        MDTextField:
            id: reporter_contact
            hint_text: "Phone Number"
            mode: "rectangle"
            size_hint_y: None
            height: "40dp"
        MDBoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "50dp"
            spacing: "5dp"
            MDTextField:
                id: search_field
                hint_text: "Search City"
                mode: "rectangle"
                size_hint_x: 0.8
            MDIconButton:
                icon: "magnify"
                on_release: root.search_location()
        MDRelativeLayout:
            size_hint_y: 1
            MapView:
                id: map_view
                lat: 9.9312
                lon: 76.2673
                zoom: 7
            MDIcon:
                icon: "map-marker"
                theme_text_color: "Custom"
                text_color: 1, 0, 0, 1
                pos_hint: {"center_x": .5, "center_y": .5}
                font_size: "40sp"
        MDRaisedButton:
            text: "NEXT"
            pos_hint: {"center_x": 0.5}
            md_bg_color: 1, 0, 0, 1
            on_release: root.check_location_step()

# 7. DETAILS SCREEN
<DetailsScreen>:
    name: "details_screen"
    MDBoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15
        MDLabel:
            text: "Step 2: Details"
            halign: "center"
            font_style: "H5"
            size_hint_y: None
            height: "30dp"
        MDCard:
            size_hint_y: None
            height: "80dp"
            orientation: "vertical"
            padding: "10dp"
            MDLabel:
                id: photo_status
                text: "No Photo Selected"
                halign: "center"
                theme_text_color: "Secondary"
            MDRaisedButton:
                text: "SELECT PHOTO (PC)"
                pos_hint: {"center_x": .5}
                on_release: root.open_file_manager()
        MDTextField:
            id: name_field
            hint_text: "Missing Name"
            mode: "rectangle"
        MDTextField:
            id: description_field
            hint_text: "Description"
            mode: "rectangle"
        MDTextField:
            id: last_seen_field
            hint_text: "Last Seen (Date & Time)"
            mode: "rectangle"
        MDRaisedButton:
            text: "BROADCAST REPORT"
            md_bg_color: 1, 0, 0, 1
            pos_hint: {"center_x": 0.5}
            on_release: root.validate_and_broadcast()

# 8. SIGHTING SCREEN
<SightingScreen>:
    name: "sighting_screen"
    MDBoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15
        MDLabel:
            text: "Report a Sighting"
            halign: "center"
            font_style: "H5"
            theme_text_color: "Custom"
            text_color: 0, 0.5, 0, 1
        MDLabel:
            id: report_for_label
            text: "Reporting sighting for: Unknown"
            halign: "center"
            theme_text_color: "Secondary"
        MDCard:
            size_hint_y: None
            height: "80dp"
            orientation: "vertical"
            padding: "10dp"
            MDLabel:
                id: sighting_photo_status
                text: "Evidence Photo (Optional)"
                halign: "center"
                theme_text_color: "Secondary"
            MDRaisedButton:
                text: "SELECT PHOTO"
                pos_hint: {"center_x": .5}
                on_release: root.open_file_manager()
        MDTextField:
            id: seen_time
            hint_text: "When? (Date & Time)"
            mode: "rectangle"
        MDTextField:
            id: seen_location
            hint_text: "Where? (Location)"
            mode: "rectangle"
        MDRaisedButton:
            text: "SUBMIT SIGHTING"
            md_bg_color: 0, 0.5, 0, 1
            pos_hint: {"center_x": 0.5}
            on_release: root.submit_sighting()
        MDFlatButton:
            text: "Cancel"
            pos_hint: {"center_x": 0.5}
            on_release: app.root.current = "home_screen"
'''

# ---------------------------------------------------------
# PYTHON LOGIC
# ---------------------------------------------------------

class LoginScreen(MDScreen):
    def do_login(self):
        email = self.ids.email.text.strip()
        if email:
            MDApp.get_running_app().user_email = email
            self.manager.current = "home_screen"
        else:
            print("Please enter email")

class SignUpScreen(MDScreen):
    selected_lat = None
    selected_lon = None
    generated_otp = None
    pending_user_data = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.selected_id_path = ""

    def open_file_manager(self):
        path = os.path.expanduser("~")
        self.file_manager.show(path)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.selected_id_path = path
        filename = os.path.basename(path)
        self.ids.id_photo_status.text = f"ID Selected: {filename}"
        self.ids.id_photo_status.theme_text_color = "Primary"

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def go_back(self):
        self.manager.current = "login_screen"

    def open_map_picker(self):
        self.manager.current = "signup_map_screen"

    def update_location_label(self, lat, lon):
        self.selected_lat = lat
        self.selected_lon = lon
        self.ids.location_label.text = f"Loc: {lat:.4f}, {lon:.4f}"
        self.ids.location_label.theme_text_color = "Custom"
        self.ids.location_label.text_color = (0, 0.6, 0, 1)

    def send_otp_step(self):
        name = self.ids.new_name.text.strip()
        mobile = self.ids.new_mobile.text.strip()
        email = self.ids.new_email.text.strip()
        pwd = self.ids.new_password.text.strip()

        if not name or not mobile or not email or not pwd:
            print("Fill all fields")
            return
        if not self.selected_id_path or not self.selected_lat:
            print("Upload ID & Pick Location")
            return

        # 1. GENERATE OTP
        self.generated_otp = str(random.randint(1000, 9999))
        print(f"--- OTP Generated (Console Backup): {self.generated_otp} ---")

        # 2. SAVE DATA TEMPORARILY
        clean_id_path = self.selected_id_path.replace("\\", "/")
        self.pending_user_data = {
            "name": name,
            "id_proof_image": clean_id_path,
            "mobile": mobile,
            "email": email,
            "password": pwd,
            "home_coords": f"{self.selected_lat},{self.selected_lon}"
        }

        # 3. SEND REAL EMAIL VIA GMAIL SMTP
        if "YOUR_REAL_GMAIL" in SENDER_EMAIL:
             print("⚠️ UPDATE EMAIL CONFIG IN LINE 26 TO SEND REAL EMAILS ⚠️")
             self.manager.current = "otp_screen"
             return

        try:
            msg = EmailMessage()
            msg.set_content(f"Hello {name},\n\nYour OTP for the Missing Alert App is: {self.generated_otp}\n\nPlease do not share this code.")
            msg['Subject'] = 'Missing App Verification Code'
            msg['From'] = SENDER_EMAIL
            msg['To'] = email

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            print(">>> EMAIL SENT SUCCESSFULLY! <<<")
            self.manager.current = "otp_screen"
            
        except Exception as e:
            print(f"EMAIL ERROR: {e}")
            self.manager.current = "otp_screen"

class OtpScreen(MDScreen):
    time_left = 20
    timer_event = None

    def on_enter(self):
        self.start_timer()

    def start_timer(self):
        # RESET TIMER
        self.time_left = 20
        self.ids.resend_btn.disabled = True
        self.ids.resend_btn.text = f"Resend in {self.time_left}s"
        
        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.time_left -= 1
        if self.time_left > 0:
            self.ids.resend_btn.text = f"Resend in {self.time_left}s"
        else:
            self.ids.resend_btn.disabled = False
            self.ids.resend_btn.text = "RESEND OTP"
            if self.timer_event:
                self.timer_event.cancel()

    def do_resend(self):
        signup_screen = self.manager.get_screen('signup_screen')
        email = signup_screen.pending_user_data.get('email')
        name = signup_screen.pending_user_data.get('name')
        
        if not email:
            print("No email found to resend")
            return

        # GENERATE NEW OTP
        new_otp = str(random.randint(1000, 9999))
        signup_screen.generated_otp = new_otp
        print(f"--- RESENT OTP (Console Backup): {new_otp} ---")
        
        # SEND EMAIL AGAIN
        try:
            msg = EmailMessage()
            msg.set_content(f"Hello {name},\n\nYour NEW OTP is: {new_otp}")
            msg['Subject'] = 'Resent Verification Code'
            msg['From'] = SENDER_EMAIL
            msg['To'] = email

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            print(">>> RESENT EMAIL SUCCESSFULLY! <<<")
            self.ids.otp_msg.text = "New OTP sent successfully!"
            
        except Exception as e:
            print(f"RESEND ERROR: {e}")
            self.ids.otp_msg.text = "Failed to resend. Check console."

        # RESTART TIMER
        self.start_timer()

    def verify_otp(self):
        entered_otp = self.ids.otp_input.text.strip()
        signup_screen = self.manager.get_screen('signup_screen')
        correct_otp = signup_screen.generated_otp
        
        if entered_otp == correct_otp:
            print("OTP VERIFIED!")
            self.save_to_firebase(signup_screen.pending_user_data)
        else:
            print("WRONG OTP!")
            self.ids.otp_msg.text = "Incorrect OTP. Try again."
            self.ids.otp_msg.theme_text_color = "Error"

    def save_to_firebase(self, user_data):
        try:
            requests.post(FIREBASE_URL + "users.json", json=user_data)
            print("User Registered to Firebase!")
            self.manager.current = "login_screen"
        except Exception as e:
            print(f"Database Error: {e}")

class SignupMapScreen(MDScreen):
    def search_location(self):
        query = self.ids.search_field.text
        if not query: return
        try:
            geolocator = Nominatim(user_agent="missing_person_app")
            location = geolocator.geocode(query)
            if location:
                self.ids.map_view.lat = location.latitude
                self.ids.map_view.lon = location.longitude
                self.ids.map_view.zoom = 14
        except:
            print("Search Error")

    def confirm_location(self):
        lat = self.ids.map_view.lat
        lon = self.ids.map_view.lon
        signup_screen = self.manager.get_screen('signup_screen')
        signup_screen.update_location_label(lat, lon)
        self.manager.current = "signup_screen"

class HomeScreen(MDScreen):
    def on_enter_actions(self):
        app = MDApp.get_running_app()
        self.ids.user_email_label.text = app.user_email
        app.start_listening()
        self.load_online_reports()

    def load_online_reports(self):
        self.ids.report_list.clear_widgets()
        try:
            response = requests.get(FIREBASE_URL + "reports.json")
            data = response.json()
            if data:
                for key, report in data.items():
                    self.add_report_card(report)
        except Exception as e:
            print(f"Connection Error: {e}")

    def add_report_card(self, report):
        card = MDCard(
            size_hint=(None, None), size=("320dp", "480dp"),
            pos_hint={"center_x": .5}, orientation="vertical",
            elevation=3, radius=[15], padding="0dp", spacing="5dp"
        )
        photo_path = report.get('photo', '')
        image_loaded = False
        if photo_path and os.path.exists(photo_path):
            card.add_widget(FitImage(source=photo_path, size_hint_y=None, height="200dp", radius=[15, 15, 0, 0]))
            image_loaded = True
        else:
            fixed_path = photo_path.replace("/", "\\")
            if os.path.exists(fixed_path):
                card.add_widget(FitImage(source=fixed_path, size_hint_y=None, height="200dp", radius=[15, 15, 0, 0]))
                image_loaded = True
        
        if not image_loaded:
            no_img = MDLabel(text="[No Image Available]", halign="center", size_hint_y=None, height="50dp", theme_text_color="Secondary")
            card.add_widget(no_img)

        info_box = MDCard(orientation="vertical", padding="10dp", spacing="5dp", elevation=0)
        name = report.get('name', 'Unknown')
        desc = report.get('desc', 'No description')
        phone = report.get('phone', 'No phone')
        last_seen = report.get('last_seen', 'Unknown time')
        coords = report.get('coords', '')

        info_box.add_widget(MDLabel(text=f"MISSING: {name}", font_style="H6", theme_text_color="Error", bold=True))
        info_box.add_widget(MDLabel(text=f"Desc: {desc}", theme_text_color="Secondary"))
        info_box.add_widget(MDLabel(text=f"Last Seen: {last_seen}", theme_text_color="Primary", bold=True))
        info_box.add_widget(MDLabel(text=f"📞 {phone}", theme_text_color="Primary"))

        if coords:
            map_btn = MDRaisedButton(text="VIEW MAP", md_bg_color=(0.2, 0.2, 0.2, 1), size_hint_x=1)
            map_btn.bind(on_release=lambda x: webbrowser.open(f"http://maps.google.com/?q={coords}"))
            info_box.add_widget(map_btn)

        saw_btn = MDRaisedButton(text="I SAW THEM", md_bg_color=(1, 0, 0, 1), size_hint_x=1)
        saw_btn.bind(on_release=lambda x: self.go_to_sighting(name))
        info_box.add_widget(saw_btn)

        card.add_widget(info_box)
        self.ids.report_list.add_widget(card)

    def go_to_sighting(self, missing_name):
        app = MDApp.get_running_app()
        sighting_screen = app.root.get_screen('sighting_screen')
        sighting_screen.ids.report_for_label.text = f"Reporting sighting for: {missing_name}"
        sighting_screen.missing_name = missing_name 
        app.root.current = "sighting_screen"

class LocationScreen(MDScreen):
    def search_location(self):
        query = self.ids.search_field.text
        if not query: return
        try:
            geolocator = Nominatim(user_agent="missing_person_app")
            location = geolocator.geocode(query)
            if location:
                self.ids.map_view.lat = location.latitude
                self.ids.map_view.lon = location.longitude
                self.ids.map_view.zoom = 15
        except:
            print("Search Error")

    def check_location_step(self):
        self.manager.current = "details_screen"

class DetailsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.selected_photo_path = ""

    def open_file_manager(self):
        path = os.path.expanduser("~")
        self.file_manager.show(path)
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        self.selected_photo_path = path
        filename = os.path.basename(path)
        self.ids.photo_status.text = f"Selected: {filename}"
        self.ids.photo_status.theme_text_color = "Primary"

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def validate_and_broadcast(self):
        name = self.ids.name_field.text
        desc = self.ids.description_field.text
        last_seen = self.ids.last_seen_field.text
        loc_screen = self.manager.get_screen('location_screen')
        phone = loc_screen.ids.reporter_contact.text
        lat = loc_screen.ids.map_view.lat
        lon = loc_screen.ids.map_view.lon
        clean_path = self.selected_photo_path.replace("\\", "/")
        
        # ADD EMAIL SO WE KNOW WHO POSTED IT
        current_user_email = MDApp.get_running_app().user_email
        
        report_data = {
            "name": name,
            "desc": desc,
            "last_seen": last_seen,
            "phone": phone,
            "photo": clean_path, 
            "coords": f"{lat},{lon}",
            "reporter_email": current_user_email # <--- KEY ADDITION
        }
        try:
            requests.post(FIREBASE_URL + "reports.json", json=report_data)
            self.manager.current = "home_screen"
            MDApp.get_running_app().manual_refresh()
        except Exception as e:
            print(f"Upload Failed: {e}")

class SightingScreen(MDScreen):
    missing_name = "Unknown"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        self.selected_photo_path = ""
    def open_file_manager(self):
        path = os.path.expanduser("~")
        self.file_manager.show(path)
        self.manager_open = True
    def select_path(self, path):
        self.exit_manager()
        self.selected_photo_path = path
        filename = os.path.basename(path)
        self.ids.sighting_photo_status.text = f"Selected: {filename}"
        self.ids.sighting_photo_status.theme_text_color = "Primary"
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
    def submit_sighting(self):
        time = self.ids.seen_time.text
        location = self.ids.seen_location.text
        clean_path = self.selected_photo_path.replace("\\", "/")
        sighting_data = {
            "missing_person": self.missing_name,
            "seen_at_time": time,
            "seen_at_loc": location,
            "evidence_photo": clean_path,
            "status": "UNVERIFIED"
        }
        try:
            requests.post(FIREBASE_URL + "sightings.json", json=sighting_data)
            if notification:
                notification.notify(title="SIGHTING SUBMITTED", message="Thank you for your help!", app_name="MissingApp")
            MDApp.get_running_app().root.current = "home_screen"
        except:
            print("Failed to send sighting")

class MissingPersonApp(MDApp):
    last_report_count = 0
    last_sighting_count = 0
    user_email = "Guest"
    
    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.material_style = "M3"
        return Builder.load_string(KV)
    
    def start_listening(self):
        Clock.schedule_interval(self.check_for_updates, 10)
        
    def manual_refresh(self):
        self.check_for_updates(0)
        
    def check_for_updates(self, dt):
        try:
            # 1. FETCH REPORTS
            response_reports = requests.get(FIREBASE_URL + "reports.json")
            reports_data = response_reports.json() if response_reports.json() else {}
            
            # 2. FETCH SIGHTINGS
            response_sightings = requests.get(FIREBASE_URL + "sightings.json")
            sightings_data = response_sightings.json() if response_sightings.json() else {}

            # 3. UPDATE HOME SCREEN (Standard refresh)
            home_screen = self.root.get_screen('home_screen')
            home_screen.ids.report_list.clear_widgets()
            
            current_report_count = len(reports_data)
            
            # NOTIFY IF NEW REPORT ADDED
            if current_report_count > self.last_report_count and self.last_report_count != 0:
                if notification:
                    notification.notify(
                        title="⚠️ NEW MISSING ALERT",
                        message="New report near you!",
                        app_name="MissingApp",
                        timeout=5
                    )
            self.last_report_count = current_report_count

            # DRAW CARDS
            for key, report in reports_data.items():
                home_screen.add_report_card(report)

            # 4. CHECK FOR SIGHTINGS FOR *THIS* USER
            # Find names of people *I* reported
            my_reported_names = []
            for k, r in reports_data.items():
                if r.get('reporter_email') == self.user_email:
                    my_reported_names.append(r.get('name'))
            
            # Count how many sightings match my cases
            my_relevant_sightings = []
            for k, s in sightings_data.items():
                if s.get('missing_person') in my_reported_names:
                    my_relevant_sightings.append(s)
            
            current_sighting_count = len(my_relevant_sightings)
            
            # If I have a new sighting for my case -> ALERT ME!
            if current_sighting_count > self.last_sighting_count and self.last_sighting_count != 0:
                latest_sighting = my_relevant_sightings[-1] # Get last one
                p_name = latest_sighting.get('missing_person')
                if notification:
                    notification.notify(
                        title="🔔 SIGHTING ALERT",
                        message=f"Someone saw {p_name}!",
                        app_name="MissingApp",
                        timeout=10
                    )
            
            self.last_sighting_count = current_sighting_count

        except Exception as e:
            print(f"Update Error: {e}")

if __name__ == "__main__":
    MissingPersonApp().run()