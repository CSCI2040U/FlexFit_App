import os
import requests
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.factory import Factory

# ✅ Set Kivy to use ANGLE for OpenGL stability
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

# ✅ Exercise API Class
class ExerciseAPI:
    BASE_URL = "https://exercisedb.p.rapidapi.com/exercises"
    HEADERS = {
        "X-RapidAPI-Key": "22a8c20e56msh9797b7aeae03bdfp1b629cjsna83e21797dde",
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }

    @classmethod
    def fetch_exercises(cls):
        """Fetch exercise data from RapidAPI."""
        try:
            response = requests.get(cls.BASE_URL, headers=cls.HEADERS)
            if response.status_code == 200:
                return response.json()  # ✅ Returns a list of exercises
            else:
                print(f"❌ API ERROR: {response.status_code}, {response.text}")
                return []
        except Exception as e:
            print(f"🚨 API Request Failed: {e}")
            return []

# ✅ Clickable MDCard Class
class ClickableCard(MDCard, ButtonBehavior):
    target_screen = StringProperty("")

    def on_release(self):
        """Navigate to the target screen when clicked."""
        if self.target_screen:
            print(f'🔄 Navigating to {self.target_screen}')
            app = MDApp.get_running_app()
            app.root.current = self.target_screen

class PasswordTextField(MDTextField):
    def on_touch_down(self, touch):
        """Detects click on the eye icon and toggles password visibility"""
        if self.icon_right and self.collide_point(*touch.pos):
            if self.icon_right == "eye-off":
                self.icon_right = "eye"
                self.password = False  # Show password
            else:
                self.icon_right = "eye-off"
                self.password = True  # Hide password
        return super().on_touch_down(touch)

# ✅ Generic Exercise Screen Template
class ExerciseScreen(Screen):
    exercise_name = StringProperty("")
    exercise_image = StringProperty("")
    exercise_description = StringProperty("")

    def on_enter(self):
        """Runs when the screen is opened and fetches data dynamically."""
        print(f"📥 Loading exercise: {self.exercise_name}")

# ✅ Define Screens
class LandingScreen(Screen):
    pass

class LoginScreen(Screen):
    pass

class SignUpScreen(Screen):
    pass

class UserInfoScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class SavedScreen(Screen):
    pass

class UserScreen(Screen):
    pass

class WithEquipmentScreen(Screen):
    pass

class WithoutEquipmentScreen(Screen):
    pass

class OutdoorScreen(Screen):
    pass

class WellnessScreen(Screen):
    pass

# ✅ Register Screens in Factory
Factory.register("ClickableCard", cls=ClickableCard)
Factory.register("ExerciseScreen", cls=ExerciseScreen)
Factory.register("HomeScreen", cls=HomeScreen)
Factory.register("LandingScreen", cls=LandingScreen)
Factory.register("SignUpScreen", cls=SignUpScreen)
Factory.register("LoginScreen", cls=LoginScreen)
Factory.register("UserInfoScreen", cls=UserInfoScreen)
Factory.register("SavedScreen", cls=SavedScreen)
Factory.register("UserScreen", cls=UserScreen)
Factory.register("WithEquipmentScreen", cls=WithEquipmentScreen)
Factory.register("WithoutEquipmentScreen", cls=WithoutEquipmentScreen)
Factory.register("OutdoorScreen", cls=OutdoorScreen)
Factory.register("WellnessScreen", cls=WellnessScreen)

# ✅ Load all KV Files Dynamically
KV_DIR = "screens"
for file in os.listdir(KV_DIR):
    if file.endswith(".kv"):
        kv_path = os.path.join(KV_DIR, file)
        print(f"✅ Loaded KV File: {kv_path}")
        Builder.load_file(kv_path)

# ✅ Main App Class
class MainApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_info = {"birthdate": None, "gender": None, "height": None, "weight": None}

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LandingScreen(name="landing"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.add_widget(UserInfoScreen(name="user_info"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(SavedScreen(name="saved"))
        self.sm.add_widget(UserScreen(name="user"))
        self.sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        self.sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        self.sm.add_widget(OutdoorScreen(name="outdoor"))
        self.sm.add_widget(WellnessScreen(name="wellness"))

        # ✅ Fetch API Data and Dynamically Create Exercise Screens
        exercise_data = ExerciseAPI.fetch_exercises()
        for exercise in exercise_data[:10]:  # Limit to 10 exercises for now
            screen = ExerciseScreen(name=str(exercise["id"]))
            screen.exercise_name = exercise["name"]
            screen.exercise_image = exercise["gifUrl"]  # Ensure this is a valid URL
            screen.exercise_description = f"Target: {exercise['target']} | Equipment: {exercise['equipment']}"
            self.sm.add_widget(screen)

        return self.sm

    # ✅ Navigation Functions
    def switch_to_screen(self, screen_name):
        """Safely switch screens and update bottom navigation highlight."""
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name
        else:
            print(f"🚨 ERROR: Screen '{screen_name}' not found!")

    def switch_to_login(self):
        self.switch_to_screen("login")

    def switch_to_signup(self):
        self.switch_to_screen("signup")

    def switch_to_user_info(self):
        self.switch_to_screen("user_info")

    def switch_to_home(self):
        self.switch_to_screen("home")

    def switch_to_saved(self):
        self.switch_to_screen("saved")

    def switch_to_user(self):
        self.switch_to_screen("user")

    def open_category(self, category):
        print(f"Opening {category} Workouts!")
        self.switch_to_screen(category)

    def google_sign_in(self):
    # """Show a popup to simulate Google Sign-In."""
        from kivymd.uix.dialog import MDDialog
        try:
            dialog = MDDialog(
                title="Google Sign-In",
                text="Google authentication is not set up yet.\nThis is a placeholder pop-up.",
                size_hint=(0.8, 0.4),
            )
            dialog.open()
        except Exception as e:
            print(f"Error opening Google Sign-In popup: {e}")

    def complete_user_info(self):
        """Store user info and go to the dashboard."""
        screen = self.root.get_screen("user_info")
        self.user_info["birthdate"] = screen.ids.birthdate.text
        self.user_info["height"] = screen.ids.height.text
        self.user_info["weight"] = screen.ids.weight.text
        print(f"User Info Saved: {self.user_info}")
        self.switch_to_home()  # Proceed to Dashboard

    def open_date_picker(self):
        """Safely opens the date picker without crashing."""
        try:
            date_dialog = MDDatePicker()  # No 'callback' argument
            date_dialog.bind(on_save=self.set_birthdate, on_cancel=self.close_date_picker)
            date_dialog.open()
        except Exception as e:
            print(f"Error opening date picker: {e}")  # Debugging in case of crashes

    def set_birthdate(self, instance, value, date_range):
        """Set the selected date in the birthdate field and update UI."""
        try:
            screen = self.root.get_screen("user_info")
            birthdate_field = screen.ids.birthdate
            birthdate_field.text = value.strftime("%m/%d/%Y")  # Update UI immediately
            birthdate_field.focus = True  # Forces Kivy to recognize the update
            birthdate_field.focus = False  # Ensures it refreshes properly
        except Exception as e:
            print(f"Error updating birthdate UI: {e}")  # Debugging if needed

    def close_date_picker(self, instance, value):
        """Handles when the user cancels the date picker to prevent crashes."""
        print("Date picker closed without selection.")

    def select_gender(self, gender):
        """Store selected gender and update UI colors."""
        self.user_info["gender"] = gender

        # Debugging: Check if gender is set correctly
        print(f"Gender Selected: {self.user_info['gender']}")

        user_info_screen = self.root.get_screen("user_info")
        user_info_screen.ids.male_card.md_bg_color = self.get_gender_color("male")
        user_info_screen.ids.female_card.md_bg_color = self.get_gender_color("female")

    def get_gender_color(self, gender):
        """Returns the color for the selected gender card."""
        if self.user_info.get("gender") == gender:
            return 0.6, 0.4, 1, 1  # Selected color (Purple)
        return 0.95, 0.92, 1, 1  # Default color (Light Purple)

if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception as e:
        print(f"🚨 ERROR: {e}")
