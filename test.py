from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField
import os

# 🔹 Define the Custom Password Field Before Loading KV Files
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

# 🔹 Screens (Ensure they are registered before KV Files load)
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

# 🔹 Load all KV Files Dynamically
KV_DIR = "screens"
for file in os.listdir(KV_DIR):
    if file.endswith(".kv"):
        kv_path = os.path.join(KV_DIR, file)
        print(f"✅ Loaded KV File: {kv_path}")
        Builder.load_file(kv_path)

# 🔹 Main App
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
        return self.sm

    def switch_to_login(self):
        self.root.current = "login"

    def switch_to_signup(self):
        self.root.current = "signup"

    def switch_to_user_info(self):
        """After Sign-Up, go to user details screen."""
        self.root.current = "user_info"

    def switch_to_home(self):
        """Navigate to Home Screen."""
        self.root.current = "home"
        print("Home Clicked!")

    def switch_to_saved(self):
        """Navigate to Saved Screen (Placeholder)."""
        self.root.current = "saved"
        print("Saved Workouts Clicked!")

    def switch_to_user(self):
        """Navigate to User Profile (Placeholder)."""
        self.root.current = "user"
        print("User Profile Clicked!")

    def switch_to_screen(self, screen_name):
        """Switch screen and update navigation bar highlighting."""
        self.root.current = screen_name

        # Update selected icon state
        for screen in ["home", "saved", "user"]:
            nav_item = self.root.get_screen(screen).ids.bottom_nav
            for item in nav_item.children:
                if isinstance(item, MDBottomNavigationItem):
                    item.selected = item.name == screen_name  # ✅ Set selected item


    def open_category(self, category):
        """Handles category click events."""
        print("Opening {} Workouts!".format(category))  # Fixes f-string issue

    def google_sign_in(self):
        """Show a popup to simulate Google Sign-In."""
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

        user_info_screen = self.root.get_screen("user_info")
        user_info_screen.ids.male_card.md_bg_color = self.get_gender_color("male")
        user_info_screen.ids.female_card.md_bg_color = self.get_gender_color("female")

        print(f"Gender Selected: {gender}")

    def get_gender_color(self, gender):
        """Returns the color for the selected gender card."""
        if self.user_info["gender"] == gender:
            return (0.6, 0.4, 1, 1)
        return (0.95, 0.92, 1, 1)

    def open_category(self, category):
        """Handles category click events."""
        print("Opening {} Workouts!".format(category))  # Fixes f-string issue


if __name__ == "__main__":
    MainApp().run()
