import json
import os
import requests
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineListItem, OneLineAvatarListItem, ImageLeftWidget, OneLineAvatarIconListItem, IconRightWidget
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField

from frontend.test import LoginScreen

# ✅ Set Kivy to use ANGLE for OpenGL stability
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

# ✅ API Connection (Using Local FastAPI)
class ExerciseAPI:
    BASE_URL = "http://127.0.0.1:8000/exercises/"

    @classmethod
    def fetch_exercises(cls):
        """Fetch exercises from FastAPI backend."""
        try:
            response = requests.get(cls.BASE_URL, timeout=15)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ ERROR: {response.status_code}, {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"🚨 API Request Failed: {e}")
            return []

def save_token(token: str):
    with open('auth_token.json', 'w') as f:
        json.dump({"token": token}, f)

def load_token():
    try:
        with open('auth_token.json', 'r') as f:
            data = json.load(f)
            return data.get("token")
    except FileNotFoundError:
        return None

# ✅ Base Screen Class for Category-based Exercise Filtering
class ExerciseCategoryScreen(Screen):
    category_filter = StringProperty("")
    saved_exercises = set()  # ✅ Shared across all screens

    def on_pre_enter(self):
        print(f"🔄 Entering {self.category_filter} Workouts...")
        self.load_exercises()

    def load_exercises(self):
        """Load exercises for the selected category and display them with a save button."""
        exercises = ExerciseAPI.fetch_exercises()
        exercise_list = self.ids.get("exercise_list", None)

        if not exercise_list:
            print("🚨 ERROR: 'exercise_list' ID not found in with_equipment.kv!")
            return

        exercise_list.clear_widgets()
        print(f"📌 Found {len(exercises)} exercises in API response for {self.category_filter}")

        if not exercises:
            exercise_list.add_widget(OneLineListItem(text="⚠️ No exercises available"))
            return

        category_name = self.category_filter.lower()

        filtered_exercises = [
            ex for ex in exercises if "tags" in ex and category_name in [tag.lower() for tag in eval(ex["tags"])]
        ]

        if not filtered_exercises:
            print(f"⚠️ No exercises found in category '{self.category_filter}'")
            exercise_list.add_widget(OneLineListItem(text=f"⚠️ No exercises in {self.category_filter}"))
            return

        app = MDApp.get_running_app()

        for exercise in filtered_exercises:
            name = exercise.get("name", "Unknown Exercise")

            # ✅ Debugging: Ensure it's being added to the list
            print(f"🔹 Adding exercise to {self.category_filter}: {name}")

            item = OneLineAvatarIconListItem(text=name)

            # ✅ Set the correct icon state based on whether the exercise is saved
            icon_name = "bookmark" if name in app.saved_exercises else "bookmark-outline"
            save_button = IconRightWidget(icon=icon_name)
            save_button.bind(on_release=lambda btn, ex=name: self.toggle_save_exercise(ex, btn))

            item.add_widget(save_button)
            exercise_list.add_widget(item)

    def toggle_save_exercise(self, exercise_name, save_button):
        """Bookmark or remove an exercise from saved workouts and update icon."""
        app = MDApp.get_running_app()

        if exercise_name in app.saved_exercises:
            app.saved_exercises.remove(exercise_name)
            save_button.icon = "bookmark-outline"  # ✅ Update icon to unselected
            print(f"❌ Removed {exercise_name} from saved exercises")
        else:
            app.saved_exercises.add(exercise_name)
            save_button.icon = "bookmark"  # ✅ Update icon to selected
            print(f"✅ Added {exercise_name} to saved exercises")

        app.update_saved_screen()  # ✅ Refresh saved screen dynamically

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


def login_user(email: str, password: str):
    url = "http://127.0.0.1:8000/login/"
    data = {"email": email, "password": password}

    # Send POST request to login
    response = requests.post(url, json=data)

    # Check if login was successful
    if response.status_code == 200:
        token = response.json().get("access_token")
        save_token(token)  # Save the token locally
        return token
    else:
        print("Login failed:", response.json())
        return None

# ✅ Define Screens
class LandingScreen(Screen):
    pass


class LoginScreen(Screen):
    def on_login(self):
        email = self.ids.login_email.text  # Fetch the email from the text field
        password = self.ids.login_password.text  # Fetch the password from the text field

        # Validate the input fields
        if not email or not password:
            # Optionally, show an error dialog or message if fields are empty
            print("❌ Email and password cannot be empty!")
            return

        # Proceed with the login if validation passes
        token = login_user(email, password)

        if token:
            print("Login successful")
            app = MDApp.get_running_app()
            app.switch_to_home()  # Switch to home screen after successful login
        else:
            print("❌ Invalid credentials")
            # You can display an error message or dialog here if the login fails


class SignUpScreen(Screen):
    pass

class UserInfoScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class SavedScreen(Screen):
    def on_pre_enter(self):
        """Load saved exercises when switching to SavedScreen"""
        print("🔄 Loading Saved Exercises...")
        self.load_saved_exercises()

    def load_saved_exercises(self):
        """Populate saved exercises list"""
        exercise_list = self.ids.get("exercise_list", None)

        if not exercise_list:
            print("🚨 ERROR: 'exercise_list' ID not found in KV file!")
            return

        exercise_list.clear_widgets()

        app = MDApp.get_running_app()
        saved_exercises = app.saved_exercises

        if not saved_exercises:
            exercise_list.add_widget(OneLineListItem(text="⚠️ No saved exercises yet!"))
            return

        for name in saved_exercises:
            item = OneLineListItem(text=name)
            exercise_list.add_widget(item)

class UserScreen(Screen):
    pass

# ✅ Category Screens (Now Inheriting from ExerciseCategoryScreen)
class WithEquipmentScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("with equipment")


class WithoutEquipmentScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("without equipment")

class OutdoorScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("outdoor")

class WellnessScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("wellness")

# ✅ Register Screens in Factory
Factory.register("ClickableCard", cls=ClickableCard)
Factory.register("ExerciseCategoryScreen", cls=ExerciseCategoryScreen)
Factory.register("HomeScreen", cls=HomeScreen)
Factory.register("LandingScreen", cls=LandingScreen)
Factory.register("SignUpScreen", cls=SignUpScreen)
Factory.register("LoginScreen", cls=LoginScreen)
Factory.register("UserInfoScreen", cls=UserInfoScreen)
Factory.register("SavedScreen", cls=SavedScreen)
Factory.register("UserScreen", cls=UserScreen)

# ✅ Explicitly Register Category Screens
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
        self.saved_exercises = set()

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LandingScreen(name="landing"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.add_widget(UserInfoScreen(name="user_info"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(SavedScreen(name="saved"))
        self.sm.add_widget(UserScreen(name="user"))

        # ✅ Add screens for each workout category
        self.sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        self.sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        self.sm.add_widget(OutdoorScreen(name="outdoor"))
        self.sm.add_widget(WellnessScreen(name="wellness"))

        return self.sm

    # ✅ Navigation Functions
    def switch_to_screen(self, screen_name):
        """Safely switch screens and update bottom navigation highlight."""
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name
        else:
            print(f"🚨 ERROR: Screen '{screen_name}' not found!")

    def switch_to_exercises(self, category):
        """Switch to ExerciseScreen and apply the category filter"""
        screen_name = category.lower().replace(" ", "_")  # ✅ Converts "With Equipment" -> "with_equipment"

        if screen_name in self.sm.screen_names:
            screen = self.sm.get_screen(screen_name)
            screen.category_filter = category  # ✅ Apply filter
            screen.load_exercises()
            self.sm.current = screen_name
        else:
            print(f"🚨 ERROR: No screen found for category '{category}' (Converted Name: {screen_name})")
            print(f"📌 Available screens: {self.sm.screen_names}")  # ✅ Debugging

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

    def update_saved_screen(self):
        """Update the saved screen with bookmarked exercises."""
        saved_screen = self.sm.get_screen("saved")
        exercise_list = saved_screen.ids.get("exercise_list", None)

        if not exercise_list:
            print("🚨 ERROR: 'exercise_list' not found in SavedScreen KV file!")
            return

        exercise_list.clear_widgets()

        if not self.saved_exercises:
            exercise_list.add_widget(OneLineListItem(text="⚠️ No saved exercises yet"))
            return

        print(f"📌 Updating saved screen with {len(self.saved_exercises)} exercises")

        for exercise in sorted(self.saved_exercises):
            item = OneLineListItem(text=exercise)
            exercise_list.add_widget(item)

    def toggle_bookmark(self, exercise_name):
        """Toggle bookmark status for an exercise."""
        if exercise_name in self.saved_exercises:
            print(f"❌ Removing {exercise_name} from saved exercises.")
            self.saved_exercises.remove(exercise_name)
        else:
            print(f"✅ Saving {exercise_name} to saved exercises.")
            self.saved_exercises.add(exercise_name)

        # ✅ Update saved screen
        self.update_saved_screen()


if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception as e:
        print(f"🚨 ERROR: {e}")