import json
import os
import requests
from datetime import datetime
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import OneLineListItem, OneLineAvatarListItem, ImageLeftWidget, OneLineAvatarIconListItem, \
    IconRightWidget, IconLeftWidget, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # ✅ Ensures proper inheritance
        self.category_filter = ""
    category_filter = StringProperty("")
    saved_exercises = set()  # ✅ Shared across all screens

    def on_pre_enter(self):
        Clock.schedule_once(self.load_exercises, 0.1)  # ✅ Delay execution slightly
        print(f"🔄 Entering {self.category_filter} Workouts...")

    def load_exercises(self, dt=None, search_query=""):
        """Load exercises for the selected category and display them with a save button."""
        exercises = ExerciseAPI.fetch_exercises()
        exercise_list = self.ids.get("exercise_list", None)

        if not exercise_list:
            # print("🚨 ERROR: 'exercise_list' ID not found in with_equipment.kv!")
            return

        exercise_list.clear_widgets()
        print(f"📌 Found {len(exercises)} exercises in API response for {self.category_filter}")

        if not exercises:
            exercise_list.add_widget(OneLineListItem(text="⚠️ No exercises available"))
            return

        category_name = self.category_filter.lower()

        # ✅ Handle cases where search_query is None
        if search_query:
            search_query = search_query.lower()
        else:
            search_query = ""

        filtered_exercises = []
        for ex in exercises:
            tags = ex.get("tags", "[]")

            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)  # ✅ Convert JSON string to list
                except json.JSONDecodeError:
                    tags = []

            if category_name in [tag.lower() for tag in tags]:
                # ✅ Apply search filter if search_query exists
                if search_query and search_query.lower() not in ex["name"].lower():
                    continue  # Skip exercises that don't match the search query

                filtered_exercises.append(ex)

        if not filtered_exercises:
            print(f"⚠️ No exercises found in category '{self.category_filter}'")
            exercise_list.add_widget(OneLineListItem(text=f"⚠️ No exercises in {self.category_filter}"))
            return

        app = MDApp.get_running_app()

        for exercise in filtered_exercises:
            name = exercise.get("name", "Unknown Exercise")
            exercise_id = exercise.get("id", "Unknown Exercise")

            # ✅ Debugging: Ensure it's being added to the list
            print(f"🔹 Adding exercise to {self.category_filter}: {name} (ID: {exercise_id})")

            item = OneLineAvatarIconListItem(text=name)
            item.exercise_id = exercise_id

            item.bind(on_release=lambda btn, ex_id=exercise_id: self.on_exercise_click(ex_id))

            edit_button = IconRightWidget(icon = "pencil")
            edit_button.bind(on_release = lambda btn, ex_id = exercise_id: app.edit_workout(ex_id))

            delete_button = IconRightWidget(icon = "trash-can")
            delete_button.bind(on_release = lambda btn, ex_id=exercise_id: app.delete_exercise(ex_id))

            # ✅ Set the correct icon state based on whether the exercise is saved
            icon_name = "bookmark" if name in app.saved_exercises else "bookmark-outline"
            save_button = IconLeftWidget(icon=icon_name)
            save_button.bind(on_release=lambda btn, ex=name: self.toggle_save_exercise(ex, btn))

            item.add_widget(edit_button)
            item.add_widget(delete_button)
            item.add_widget(save_button)
            exercise_list.add_widget(item)

    def on_search(self, instance, search_text = ""):
        self.load_exercises(search_query = search_text)

    def on_exercise_click(self, exercise_id):
        """Handles clicking on an exercise to navigate to the detail screen."""
        app = MDApp.get_running_app()
        app.show_exercise(exercise_id)

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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

class GuestHomeScreen(Screen):
    def on_pre_enter(self):
        """Load all workouts initially."""
        Clock.schedule_once(lambda dt: self.load_workouts(""), 0.1)

    def load_workouts(self, search_query=""):
        """Fetch workouts dynamically based on search input."""
        search_query = search_query.strip().lower()
        workouts = ExerciseAPI.fetch_exercises()  # ✅ Fetch all exercises from API

        if not workouts:
            print("⚠️ No workouts found from API")
            self.display_workouts([])
            return

        # ✅ Only filter on API response (no in-memory storage)
        filtered_workouts = [
            workout for workout in workouts if search_query in workout["name"].lower()
        ]

        self.display_workouts(filtered_workouts)

    def display_workouts(self, workouts):
        """Update the UI with workout list."""
        all_workouts_list = self.ids.get("all_workouts_list", None)

        if not all_workouts_list:
            print("🚨 ERROR: 'all_workouts_list' ID not found in all_workouts_screen.kv!")
            return

        all_workouts_list.clear_widgets()  # ✅ Clear previous results

        if not workouts:
            all_workouts_list.add_widget(OneLineListItem(text="⚠️ No workouts found"))
            return

        app = MDApp.get_running_app()

        for workout in workouts:
            name = workout.get("name", "Unknown Workout")
            workout_id = workout.get("id", "Unknown ID")

            item = OneLineAvatarIconListItem(text=name)
            item.workout_id = workout_id

            all_workouts_list.add_widget(item)

    def on_search(self, instance, *args):
        """Fetch workouts dynamically based on user input."""
        search_text = instance.text.strip()  # ✅ Extract text properly
        Clock.schedule_once(lambda dt: self.load_workouts(search_text), 0.1)  # ✅ Debounce search


class UserInfoScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class SavedScreen(Screen):
    def on_pre_enter(self):
        """Load saved exercises when switching to SavedScreen"""
        print("🔄 Loading Saved Exercises...")
        self.load_saved_exercises()

    def load_saved_exercises(self, search_query=""):
        """Populate saved exercises list with optional search functionality"""
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

        # ✅ Apply search filter
        filtered_exercises = [
            name for name in saved_exercises if search_query.lower() in name.lower()
        ] if search_query else saved_exercises

        if not filtered_exercises:
            exercise_list.add_widget(OneLineListItem(text="⚠️ No matches found!"))
            return

        for name in filtered_exercises:
            item = OneLineListItem(text=name)
            exercise_list.add_widget(item)

    def on_search(self, instance, search_text=""):
        """Triggered when search text changes"""
        print(f"🔍 Searching for: {search_text}")
        self.load_saved_exercises(search_query=search_text)


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

class AddWorkoutScreen(ExerciseCategoryScreen):
    selected_toughness = StringProperty("Easy")

    def set_toughness(self, toughness):
        self.selected_toughness = toughness
        print(f"Toughness set to {self.selected_toughness}")

class ExerciseDetailScreen(Screen):
    exercise_id = StringProperty("")
    exercise_name = StringProperty("")
    exercise_description = StringProperty("")
    exercise_tags = StringProperty("")
    exercise_reps = StringProperty("")
    exercise_toughness = StringProperty("")
    exercise_image_url = StringProperty("")

    def display_exercise(self, exercise_id):
        """Fetch and display exercise details from the backend."""
        self.exercise_id = str(exercise_id)
        BASE_URL = "http://127.0.0.1:8000"
        response = requests.get(f"{BASE_URL}/exercise/{exercise_id}")

        if response.status_code == 200:
            exercise_data = response.json()
            print(f"📄 API Response: {exercise_data}")

            # ✅ Since FastAPI now returns a list, join it properly
            self.exercise_tags = ", ".join(exercise_data.get("tags", [])) if exercise_data.get(
                "tags") else "No tags available"

            self.exercise_name = exercise_data.get("name", "Unknown Exercise")
            self.exercise_description = exercise_data.get("description", "No description available.")
            self.exercise_reps = str(exercise_data.get("suggested_reps", "N/A"))
            self.exercise_toughness = exercise_data.get("toughness", "Unknown")
            self.exercise_image_url = exercise_data.get("image_url", "")

            Clock.schedule_once(lambda dt: self.property_refresh(), 0)

        else:
            print(f"❌ ERROR: Failed to fetch exercise. Status {response.status_code}")
            print(f"⚠️ API Error Message: {response.text}")

    def property_refresh(self):
        """Manually refresh properties to update UI."""
        self.property("exercise_name").dispatch(self)
        self.property("exercise_description").dispatch(self)
        self.property("exercise_tags").dispatch(self)
        self.property("exercise_reps").dispatch(self)
        self.property("exercise_toughness").dispatch(self)
        self.property("exercise_image_url").dispatch(self)

class FilterDialogContent(MDBoxLayout):
    pass

class AllWorkoutsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_filters = set()
        self.menu = None  # ✅ Initialize menu

    # def get_filter_items(self):
    #     return [{"text": f"{tag}", "on_release": lambda x=tag: self.apply_filter(x)} for tag in ["With Equipment", "Without Equipment", "Outdoor", "Wellness"]]
    #
    # def open_dropdown(self):
    #     self.menu = MDDropdownMenu(items=self.get_filter_items(), width_mult=4)
    #     self.menu.open()

    def on_pre_enter(self):
        """Load all workouts initially."""
        Clock.schedule_once(lambda dt: self.load_workouts(""), 0.1)

    def load_workouts(self, search_query=""):
        """Fetch workouts dynamically based on search input."""
        search_query = search_query.strip().lower()
        workouts = ExerciseAPI.fetch_exercises()  # ✅ Fetch all exercises from API

        if not workouts:
            print("⚠️ No workouts found from API")
            self.display_workouts([])
            return

        # ✅ Only filter on API response (no in-memory storage)
        filtered_workouts = [
            workout for workout in workouts if search_query in workout["name"].lower()
        ]

        self.display_workouts(filtered_workouts)

    def display_workouts(self, workouts):
        """Update the UI with workout list."""
        all_workouts_list = self.ids.get("all_workouts_list", None)

        if not all_workouts_list:
            print("🚨 ERROR: 'all_workouts_list' ID not found in all_workouts_screen.kv!")
            return

        all_workouts_list.clear_widgets()  # ✅ Clear previous results

        if not workouts:
            all_workouts_list.add_widget(OneLineListItem(text="⚠️ No workouts found"))
            return

        app = MDApp.get_running_app()

        for workout in workouts:
            name = workout.get("name", "Unknown Workout")
            workout_id = workout.get("id", "Unknown ID")

            item = OneLineAvatarIconListItem(text=name)
            item.workout_id = workout_id

            view_button = IconRightWidget(icon="arrow-right")
            view_button.bind(on_release=lambda btn, ex_id=workout_id: app.show_exercise(ex_id))

            # delete_button = IconRightWidget(icon="trash-can")
            # delete_button.bind(on_release=lambda btn, ex_id=workout_id: app.delete_exercise(ex_id))

            item.add_widget(view_button)
            # item.add_widget(delete_button)
            all_workouts_list.add_widget(item)

    def on_search(self, instance, *args):
        """Fetch workouts dynamically based on user input."""
        search_text = instance.text.strip()  # ✅ Extract text properly
        Clock.schedule_once(lambda dt: self.load_workouts(search_text), 0.1)  # ✅ Debounce search

    from kivymd.uix.menu import MDDropdownMenu

    def open_filter_dropdown(self):
        """Open the filter dropdown menu safely without unpacking errors."""

        filters = ["with equipment", "without equipment", "outdoor", "wellness"]

        menu_items = [
            {
                "text": filter_name,
                "viewclass": "OneLineListItem",
                "on_release": lambda f=filter_name: self.toggle_filter(f), # ✅ Assign filter properly
                "md_bg_color": (0.2, 0.6, 1, 1) if filter_name in self.selected_filters else (0.8, 0.8, 0.8, 1)
            }
            for filter_name in filters
        ]

        # ✅ Debugging: Check if menu_items is correctly populated
        if not menu_items:
            print("🚨 ERROR: menu_items is empty!")

        self.menu = MDDropdownMenu(
            caller=self.ids.filter_button,  # ✅ Ensure this button ID exists in the KV file
            items=menu_items,
            width_mult=4
        )

        self.menu.open()

    def toggle_filter(self, filter_name):
        """Toggle filter buttons and update UI color based on selection."""

        # ✅ Ensure selected_filters is initialized
        if self.selected_filters is None:
            self.selected_filters = set()

        # ✅ Toggle filter state
        if filter_name in self.selected_filters:
            self.selected_filters.remove(filter_name)
            print(f"❌ Removed Filter: {filter_name}")
        else:
            self.selected_filters.add(filter_name)
            print(f"✅ Added Filter: {filter_name}")

        # ✅ Debugging Output
        print(f"📌 Current Filters: {self.selected_filters}")

        # ✅ Apply filter changes immediately
        self.apply_filter()

    def apply_filter(self):
        """Apply the selected filters and update the workout list."""
        print(f"🎯 Applying Filters: {self.selected_filters}")

        # ✅ Fetch all workouts
        all_workouts = ExerciseAPI.fetch_exercises()

        if not all_workouts:
            print("⚠️ No workouts fetched from API")
            self.display_workouts([])
            return

        # ✅ Normalize selected filters (convert to lowercase)
        normalized_filters = {filter.lower() for filter in self.selected_filters}
        print(f"🛠️ Normalized Filters: {normalized_filters}")

        # ✅ Debug: Print how tags are stored in the API response
        for workout in all_workouts[:5]:  # Print first 5 workouts only
            print(f"📌 API Workout: {workout['name']}, Tags: {workout.get('tags', 'N/A')}")

        # ✅ If no filters are selected, show all workouts
        if not self.selected_filters:
            self.display_workouts(all_workouts)
            return

        # ✅ Fix Filtering Logic (Convert API Tags to lowercase)
        filtered_workouts = []
        for workout in all_workouts:
            workout_tags = workout.get("tags", [])

            # ✅ Ensure tags are a **list** and convert to lowercase
            if isinstance(workout_tags, str):
                try:
                    workout_tags = json.loads(workout_tags)  # Convert string to list
                except json.JSONDecodeError:
                    workout_tags = []

            workout_tags = {tag.lower() for tag in workout_tags}  # ✅ Convert tags to lowercase

            print(f"🔹 Checking: {workout['name']} -> Tags: {workout_tags}")

            # ✅ Check if at least one normalized filter is in workout tags
            if normalized_filters.intersection(workout_tags):
                filtered_workouts.append(workout)

        # ✅ Debugging Output
        print(f"📌 Displaying {len(filtered_workouts)} workouts after filtering")

        # ✅ Update UI with filtered workouts
        self.display_workouts(filtered_workouts)


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
Factory.register("GuestHomeScreen", cls=GuestHomeScreen)

# ✅ Explicitly Register Category Screens
Factory.register("WithEquipmentScreen", cls=WithEquipmentScreen)
Factory.register("WithoutEquipmentScreen", cls=WithoutEquipmentScreen)
Factory.register("OutdoorScreen", cls=OutdoorScreen)
Factory.register("WellnessScreen", cls=WellnessScreen)
Factory.register("ExerciseDetailScreen", cls=ExerciseDetailScreen)

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

    def __getattr__(self, name):
        print(f"🚨 Attempted to access: {name}")  # Debugging
        return super().__getattr__(name)

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LandingScreen(name="landing"))
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignUpScreen(name="signup"))
        self.sm.add_widget(UserInfoScreen(name="user_info"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(SavedScreen(name="saved"))
        self.sm.add_widget(UserScreen(name="user"))
        self.sm.add_widget(AddWorkoutScreen(name="add_workout"))
        self.sm.add_widget(GuestHomeScreen(name="guest"))


        # ✅ Add screens for each workout category
        self.sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        self.sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        self.sm.add_widget(OutdoorScreen(name="outdoor"))
        self.sm.add_widget(WellnessScreen(name="wellness"))

        self.sm.add_widget(ExerciseDetailScreen(name="exercise_detail"))
        self.sm.add_widget(AllWorkoutsScreen(name="all_workouts"))

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

    def show_exercise(self, exercise_id):
        screen = self.root.get_screen("exercise_detail")
        screen.display_exercise(exercise_id)
        self.root.current = "exercise_detail"

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
            birthdate = screen.ids.birthdate
            birthdate.text = value.strftime("%m/%d/%Y")  # Update UI immediately
            birthdate.focus = True  # Forces Kivy to recognize the update
            birthdate.focus = False  # Ensures it refreshes properly
        except Exception as e:
            print(f"Error updating birthdate UI: {e}")  # Debugging if needed

    def close_date_picker(self, instance, value):
        """Handles when the user cancels the date picker to prevent crashes."""
        print("Date picker closed without selection.")

    def convert_date_format(self, date_str):
        """Converts MM/DD/YYYY to YYYY-MM-DD format."""
        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%Y")  # ✅ Convert input format
            return date_obj.strftime("%Y-%m-%d")  # ✅ Return formatted date
        except ValueError:
            print("🚨 ERROR: Invalid date format!")  # ✅ Debugging
            return ""

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

    def complete_user_info(self):
        """Collects all sign-up details and completes user registration."""
        user_info_screen = self.root.get_screen("user_info")
        signup_screen = self.root.get_screen("signup")

        # ✅ Get user details from user_info_screen
        birthdate_text = user_info_screen.ids.birthdate.text.strip()
        formatted_dob = self.convert_date_format(birthdate_text)  # Convert MM/DD/YYYY → YYYY-MM-DD
        gender = self.user_info.get("gender", "")  # Get gender selection
        height = user_info_screen.ids.height.text.strip()
        weight = user_info_screen.ids.weight.text.strip()

        # ✅ Get user details from signup_screen
        username = signup_screen.ids.signup_username.text.strip()
        full_name = signup_screen.ids.signup_name.text.strip()
        email = signup_screen.ids.signup_email.text.strip()
        password = signup_screen.ids.signup_password.text.strip()

        # ✅ Merge all details into one dictionary
        user_data = {
            "username": username,
            "full_name": full_name,
            "email": email,
            "password": password,
            "dob": formatted_dob,
            "gender": gender,
            "height": height,
            "weight": weight,
            "role": "user"
        }


        print(f"📌 Final Signup Data: {user_data}")  # ✅ Debugging

        # ✅ Send request to backend
        response = requests.post("http://127.0.0.1:8000/signup/", json=user_data)

        if response.status_code == 200:
            print("✅ User registered successfully!")
            self.root.current = "login"  # ✅ Redirect to login screen
        else:
            print(f"❌ Signup Error: {response.json()}")  # ✅ Show exact error message


    def logout_user(self):
        """Logs out the user by deleting the stored token and redirecting to login screen."""
        try:
            if os.path.exists("auth_token.json"):
                os.remove("auth_token.json")  # ✅ Delete stored auth token
                print("✅ Logged out successfully.")
            else:
                print("⚠️ No authentication token found.")

            self.switch_to_login()  # ✅ Redirect user to login screen
        except Exception as e:
            print(f"🚨 ERROR during logout: {e}")

    def edit_workout(self, exercise_id):
        self.dialog = MDDialog(
            title="Edit Workout",
            type="custom",
            content_cls = MDTextField(hint_text="Enter New Workout Name"),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda _: self.confirm_edit_workout(exercise_id)
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=lambda _: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def confirm_edit_workout(self, exercise_id):
        new_name = self.dialog.content_cls.text.strip()
        if not new_name:
            print("❌ Workout name cannot be empty!")
            return

        url = f"http://127.0.0.1:8000/edit_exercise/{exercise_id}"
        response = requests.put(url, json={"name": new_name})

        if response.status_code == 200:
            print(f"✅ Workout {exercise_id} updated successfully!")
            self.refresh_exercises()
        else:
            print(f"❌ Error updating Workout {response.json()}!")

        self.dialog.dismiss()

    def delete_exercise(self, exercise_id):
        """Confirms and deletes the exercise."""
        print(f"🚨 Function Reference Check: delete_exercise = {self.delete_exercise}")

        # ✅ Define confirm_delete AFTER dialog
        def confirm_delete(instance):
            print(f"📌 Attempting to delete exercise with ID: {exercise_id}")
            url = f"http://127.0.0.1:8000/api/exercises/{exercise_id}"
            response = requests.delete(url)

            if response.status_code == 200:
                print(f"✅ Exercise {exercise_id} deleted successfully!")
                self.refresh_exercises()
            else:
                print(f"❌ Error deleting exercise: {response.json()}")

            dialog.dismiss()  # ✅ Ensure dialog is correctly defined before calling dismiss()

        # ✅ Define dialog BEFORE calling confirm_delete
        dialog = MDDialog(
            title="Delete Exercise",
            text="Are you sure you want to delete this exercise?",
            buttons=[
                MDRaisedButton(text="Yes", on_release=lambda _: confirm_delete(None)),  # ✅ Proper lambda
                MDRaisedButton(text="No", on_release=lambda _: dialog.dismiss())  # ✅ Ensures dialog exists
            ]
        )

        dialog.open()

    def refresh_exercises(self):
        """Reloads the exercises list after changes."""
        current_screen = self.root.current_screen
        if hasattr(current_screen, "load_exercises"):
            current_screen.load_exercises()
        else:
            print("❌ ERROR: Current screen doesn't support exercise loading.")

    def update_saved_screen(self):
        """Update the saved screen with bookmarked exercises."""
        saved_screen = self.sm.get_screen("saved")
        exercise_list = saved_screen.ids.get("exercise_list", None)

        if not exercise_list:
            print("🚨 ERROR: 'exercise_list' not found in SavedScreen KV file!")
            return

        exercise_list.clear_widgets()

        if not self.saved_exercises:
            exercise_list.add_widget(OneLineListItem(text="No saved exercises yet :("))
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

    def switch_to_add_workout(self):
        """Switch to AddWorkoutScreen."""
        self.switch_to_screen("add_workout")

    def submit_workout(self):
        screen = self.sm.get_screen("add_workout")

        tag_input_widget = screen.ids.workout_tags
        tag_text = tag_input_widget.text.strip()

        tags_list = [tag.strip() for tag in tag_text.split(",") if tag.strip()] if tag_text else []

        workout_data = {
            "name": screen.ids.workout_name.text,
            "description": screen.ids.workout_description.text,
            "toughness": screen.selected_toughness,
            "tags": tags_list,
            "suggested_reps": int(screen.ids.workout_reps.text) if screen.ids.workout_reps.text.isdigit() else 10
        }

        print(f"📤 Submitting workout: {workout_data}")  # ✅ Print the request payload

        response = requests.post("http://127.0.0.1:8000/add_exercise/", json=workout_data)

        print(f"📥 API Response: {response.status_code}, {response.text}")  # ✅ Print the API response

        if response.status_code == 200:
            print("✅ Workout added successfully!")
            self.root.current = "user"
        else:
            print(f"❌ Error adding workout: {response.json()}")  # ✅ Print the error message


if __name__ == "__main__":
    try:
        MainApp().run()
    except AttributeError as e:
        print(f"🚨 AttributeError: {e}")
    except Exception as e:
        print(f"🚨 ERROR: {e}")