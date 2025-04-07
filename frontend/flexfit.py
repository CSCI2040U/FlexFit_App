import json
import os
from collections import Counter
from datetime import datetime

import requests
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.chip import MDChip
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, ImageLeftWidget, OneLineAvatarIconListItem, \
    IconRightWidget, IconLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField

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
            save_button.bind(
                on_release=lambda btn, ex_id=exercise_id, ex_name=name: app.toggle_bookmark(ex_id, ex_name, btn))

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

    try:
        # Send POST request to login
        response = requests.post(url, json={"email": email, "password": password})
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            save_token(token)  # Save token locally

            # ✅ Save user info globally
            app = MDApp.get_running_app()
            app.user_info = {
                "id": data["user"]["id"],
                "username": data["user"]["username"],
                "email": data["user"]["email"],
                "height": data["user"]["height"],
                "weight": data["user"]["weight"],
                "gender": data["user"]["gender"],
                "birthdate": data["user"]["dob"],
                "role": data["user"]["role"]
            }

            user_id = app.user_info["id"]
            saved_url = f"http://127.0.0.1:8000/saved_exercises/{user_id}/"
            saved_response = requests.get(saved_url)

            if saved_response.status_code == 200:
                saved_ids = saved_response.json()
                all_exercises = ExerciseAPI.fetch_exercises()
                app.saved_exercises = {
                    ex["name"] for ex in all_exercises if ex["id"] in saved_ids
                }
                print(f"📌 Loaded {len(app.saved_exercises)} saved exercises")
            else:
                print(f"⚠️ Could not load saved exercises: {saved_response.status_code} | {saved_response.text}")
                app.saved_exercises = set()

            print(f"✅ Logged in as: {app.user_info}")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}, {response.json()}")
            return None
    except Exception as e:
        print(f"🚨 ERROR during login: {e}")
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_filters = set()
        self.menu = None  # ✅ Initialize menu

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
        guest_all_workouts_list = self.ids.get("guest_all_workouts_list", None)

        if not guest_all_workouts_list:
            print("🚨 ERROR: 'all_workouts_list' ID not found in all_workouts_screen.kv!")
            return

        guest_all_workouts_list.clear_widgets()  # ✅ Clear previous results

        if not workouts:
            guest_all_workouts_list.add_widget(OneLineListItem(text="⚠️ No workouts found"))
            return

        app = MDApp.get_running_app()

        for workout in workouts:
            name = workout.get("name", "Unknown Workout")
            workout_id = workout.get("id", "Unknown ID")
            image_url = workout.get("media_url",
                                    "https://res.cloudinary.com/dudftatqj/image/upload/v1741316241/logo_iehkuj.png")

            item = OneLineAvatarIconListItem(text=name)
            item.add_widget(ImageLeftWidget(source=image_url))
            item.workout_id = workout_id

            view_button = IconRightWidget(icon="arrow-right")
            view_button.bind(on_release=lambda btn, ex_id=workout_id: app.show_guest_exercise(ex_id))

            item.add_widget(view_button)
            guest_all_workouts_list.add_widget(item)

    def on_search(self, instance, *args):
        """Fetch workouts dynamically based on user input."""
        search_text = instance.text.strip()  # ✅ Extract text properly
        Clock.schedule_once(lambda dt: self.load_workouts(search_text), 0.1)  # ✅ Debounce search

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

class AddWorkoutScreen(ExerciseCategoryScreen):
    selected_toughness = StringProperty("Easy")
    selected_tags = ListProperty([])
    selected_image_path = StringProperty("")

    def upload_image_to_cloudinary(self):
        print(f"[DEBUG UPLOAD] self = {self}, selected_image_path = {self.selected_image_path}")

        if not self.selected_image_path:
            print("⚠️ No image selected.")
            return None

        print(f"📸 Path to upload: {self.selected_image_path}")
        url = "https://api.cloudinary.com/v1_1/dudftatqj/image/upload"
        payload = {
            "upload_preset": "flexfit_unsigned"
        }
        with open(self.selected_image_path, "rb") as img:
            files = {"file": img}
            res = requests.post(url, data=payload, files=files)

        if res.status_code == 200:
            uploaded_url = res.json()["secure_url"]
            print(f"✅ Uploaded image URL: {uploaded_url}")
            return uploaded_url
        else:
            print("❌ Image upload failed.")
            return None
    def set_toughness(self, toughness):
        self.selected_toughness = toughness
        print(f"Toughness set to {self.selected_toughness}")

    def toggle_category(self, category):
        if category in self.selected_tags:
            self.selected_tags.remove(category)
            print(f"❌ Removed tag: {category}")
        else:
            self.selected_tags.append(category)
            print(f"✅ Added tag: {category}")

        print(f"Current selected tags: {self.selected_tags}")

    def select_image(self):
        chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"])
        selected_path_label = Label(text="No file selected", size_hint_y=None, height=dp(30))
        select_button = Button(text="Confirm", size_hint_y=None, height=dp(40))

        box = BoxLayout(orientation='vertical', spacing=10)
        box.add_widget(chooser)
        box.add_widget(selected_path_label)
        box.add_widget(select_button)

        popup = Popup(title="Select Image", content=box, size_hint=(0.9, 0.9))

        def on_confirm_press(_):
            selection = chooser.selection
            if selection:
                self.selected_image_path = selection[0]
                print(f"✅ Selected image: {self.selected_image_path}")
                print(f"[DEBUG SELECT] self = {self}, selected_image_path = {self.selected_image_path}")
                selected_path_label.text = f"Selected: {os.path.basename(self.selected_image_path)}"
                popup.dismiss()
            else:
                selected_path_label.text = "⚠️ Please select an image file first"

        select_button.bind(on_press=on_confirm_press)
        popup.open()

    def submit_workout(self):
        media_url = self.upload_image_to_cloudinary()

        workout_data = {
            "name": self.ids.workout_name.text,
            "description": self.ids.workout_description.text,
            "toughness": self.selected_toughness,
            "tags": self.selected_tags,
            "media_url": media_url,
            "suggested_reps": int(self.ids.workout_reps.text or "12")
        }

        print(f"📤 Submitting workout: {workout_data}")

        try:
            res = requests.post("http://127.0.0.1:8000/add_exercise/", json=workout_data)
            if res.status_code == 200:
                print(f"✅ Workout added successfully!")
                print(f"📥 API Response: {res.status_code}, {res.json()}")
            else:
                print(f"❌ Failed to add workout. Code: {res.status_code}, Response: {res.text}")
        except Exception as e:
            print(f"🔥 Error during workout submission: {e}")


class AllWorkoutsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_filters = set()
        self.menu = None  # ✅ Initialize menu

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
        user_all_workouts_list = self.ids.get("user_all_workouts_list", None)

        if not user_all_workouts_list:
            print("🚨 ERROR: 'all_workouts_list' ID not found in all_workouts_screen.kv!")
            return

        user_all_workouts_list.clear_widgets()  # ✅ Clear previous results

        if not workouts:
            user_all_workouts_list.add_widget(OneLineListItem(text="⚠️ No workouts found"))
            return

        app = MDApp.get_running_app()

        for workout in workouts:
            name = workout.get("name", "Unknown Workout")
            workout_id = workout.get("id", "Unknown ID")
            image_url = workout.get("media_url",
                                     "https://res.cloudinary.com/dudftatqj/image/upload/v1741316241/logo_iehkuj.png")

            item = OneLineAvatarIconListItem(text=name)
            item.add_widget(ImageLeftWidget(source=image_url))
            item.workout_id = workout_id

            view_button = IconRightWidget(icon="arrow-right")
            view_button.bind(on_release=lambda btn, ex_id=workout_id: app.show_exercise(ex_id))

            edit_button = IconRightWidget(icon = "pencil")
            edit_button.bind(on_release = lambda btn, ex_id = workout_id: app.edit_workout(ex_id))

            icon_name = "bookmark" if name in app.saved_exercises else "bookmark-outline"

            item.add_widget(view_button)
            item.add_widget(edit_button)
            user_all_workouts_list.add_widget(item)

    def on_search(self, instance, *args):
        """Fetch workouts dynamically based on user input."""
        search_text = instance.text.strip()  # ✅ Extract text properly
        Clock.schedule_once(lambda dt: self.load_workouts(search_text), 0.1)  # ✅ Debounce search

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


class UserInfoScreen(Screen):
    pass

class HomeScreen(Screen):
    pass

class SavedScreen(Screen):
    def on_pre_enter(self):
        """Load saved exercises from the database"""
        print("🔄 Loading Saved Exercises from DB...")
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")

        if not user_id:
            print("🚨 No user logged in")
            return

        try:
            response = requests.get(f"http://127.0.0.1:8000/saved_exercises/{user_id}")
            if response.status_code == 200:
                exercise_ids = response.json()

                # Fetch all exercises and map IDs to names
                all_exercises = ExerciseAPI.fetch_exercises()
                id_to_name = {ex["id"]: ex["name"] for ex in all_exercises}
                app.saved_exercises = {id_to_name[ex_id] for ex_id in exercise_ids if ex_id in id_to_name}

                print(f"✅ Loaded {len(app.saved_exercises)} saved exercises")
            else:
                print(f"❌ Failed to load saved exercises: {response.text}")

        except Exception as e:
            print(f"🚨 Error fetching saved exercises: {e}")

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
    def on_enter(self):
        app = MDApp.get_running_app()
        user_info = app.user_info

        self.ids.greeting_user_text.text = f"Hello {user_info.get('username', 'N/A')}"
        self.ids.height_label.text = f"{user_info.get('height', 'N/A')} cm"
        self.ids.weight_label.text = f"{user_info.get('weight', 'N/A')} kg"


# ✅ Category Screens (Now Inheriting from ExerciseCategoryScreen)
class WithEquipmentScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("with equipment")


class WithoutEquipmentScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("without equipment")

class OutdoorScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("outdoor")

class WellnessScreen(ExerciseCategoryScreen):
    category_filter = StringProperty("wellness")

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


    def log_workout_completion(self):
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")
        exercise_id = self.exercise_id  # Make sure you're storing this in your class when showing workout detail

        if not user_id or not exercise_id:
            print("🚨 Missing user or exercise ID")
            return

        try:
            response = requests.post(
                f"http://127.0.0.1:8000/log_workout/{user_id}/{exercise_id}"
            )
            if response.status_code == 200:
                print("✅ Workout logged successfully")
            else:
                print(f"❌ Failed to log workout: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"🚨 ERROR logging workout: {e}")

class GuestExerciseDetailScreen(Screen):
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

class EditWorkoutScreen(ExerciseCategoryScreen):
    exercise_id = StringProperty("")
    selected_image_path = StringProperty("")  # ✅ Add this line
    selected_tags = ListProperty([])          # ✅ Optional: add this if using category/tag selection
    selected_toughness = StringProperty("Easy")

    def load_exercise_data(self, exercise_id):
        self.exercise_id = exercise_id
        response = requests.get(f"http://127.0.0.1:8000/exercise/{exercise_id}")
        if response.status_code == 200:
            data = response.json()
            self.ids.workout_name.text = data.get("name", "")
            self.ids.workout_description.text = data.get("description", "")
            self.ids.workout_reps.text = str(data.get("suggested_reps", ""))
            self.selected_toughness = data.get("toughness", "Easy")
            self.selected_tags = data.get("tags", [])
            self.selected_image_path = data.get("media_url", "")
        else:
            print("❌ Failed to load exercise details")

    def upload_image_to_cloudinary(self):
        if not self.selected_image_path:
            print("⚠️ No image selected.")
            return None

        print(f"📸 Path to upload: {self.selected_image_path}")
        url = "https://api.cloudinary.com/v1_1/dudftatqj/image/upload"
        payload = {
            "upload_preset": "flexfit_unsigned"
        }
        with open(self.selected_image_path, "rb") as img:
            files = {"file": img}
            res = requests.post(url, data=payload, files=files)

        if res.status_code == 200:
            uploaded_url = res.json()["secure_url"]
            print(f"✅ Uploaded image URL: {uploaded_url}")
            return uploaded_url
        else:
            print("❌ Image upload failed.")
            return None

    def select_image(self):
        chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"])
        selected_path_label = Label(text="No file selected", size_hint_y=None, height=dp(30))
        select_button = Button(text="Confirm", size_hint_y=None, height=dp(40))

        box = BoxLayout(orientation='vertical', spacing=10)
        box.add_widget(chooser)
        box.add_widget(selected_path_label)
        box.add_widget(select_button)

        popup = Popup(title="Select Image", content=box, size_hint=(0.9, 0.9))

        def on_confirm_press(_):
            selection = chooser.selection
            if selection:
                self.selected_image_path = selection[0]
                print(f"✅ Selected image: {self.selected_image_path}")
                selected_path_label.text = f"Selected: {os.path.basename(self.selected_image_path)}"
                popup.dismiss()
            else:
                selected_path_label.text = "⚠️ Please select an image file first"

        select_button.bind(on_press=on_confirm_press)
        popup.open()

    def toggle_category(self, category):
        if category in self.selected_tags:
            self.selected_tags.remove(category)
            print(f"❌ Removed tag: {category}")
        else:
            self.selected_tags.append(category)
            print(f"✅ Added tag: {category}")

        print(f"Current selected tags: {self.selected_tags}")

    def set_toughness(self, toughness):
        self.selected_toughness = toughness
        print(f"Toughness set to {self.selected_toughness}")

    def submit_edit(self):
        image_url = self.upload_image_to_cloudinary() or self.selected_image_path

        updated_data = {
            "name": self.ids.workout_name.text,
            "description": self.ids.workout_description.text,
            "toughness": self.selected_toughness,
            "tags": self.selected_tags,
            "media_url": image_url,
            "suggested_reps": int(self.ids.workout_reps.text or "12")
        }

        print("🧾 Payload sent to backend:", updated_data)

        response = requests.put(f"http://127.0.0.1:8000/edit_exercise/{self.exercise_id}", json=updated_data)

        if response.status_code == 200:
            print("✅ Workout updated successfully")
            MDApp.get_running_app().switch_to_home()
        else:
            print(f"❌ Failed to update workout: {response.text}")


import matplotlib.pyplot as plt
from io import BytesIO
from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.core.image import Image as CoreImage


class ProgressScreen(Screen):
    def on_enter(self):
        self.load_progress_logs()
        self.load_achievements()

    def log_progress(self):
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")
        height = self.ids.height_input.text
        weight = self.ids.weight_input.text

        if not height or not weight:
            print("⚠️ Fill both height and weight")
            return

        # Fetch and print current streak
        try:
            streak_response = requests.get(f"http://127.0.0.1:8000/streak/{user_id}")
            if streak_response.status_code == 200:
                streak = streak_response.json().get("streak", 0)
                print(f"🔥 Current streak: {streak} days")
                self.ids.streak_label.text = f"🔥 Current Streak: {streak} Days"
        except Exception as e:
            print(f"🚨 Failed to fetch streak: {e}")


        try:
            response = requests.post(
                f"http://127.0.0.1:8000/progress/{user_id}",
                params={"height": float(height), "weight": float(weight)}
            )
            if response.status_code == 200:
                print("✅ Progress logged")


                # 🔥 Trigger streak update
                streak_response = requests.post(f"http://127.0.0.1:8000/streak/{user_id}")
                if streak_response.status_code == 200:
                    streak_data = streak_response.json()
                    print(f"🔥 Streak updated: {streak_data.get('streak')} days")

                self.ids.height_input.text = ""
                self.ids.weight_input.text = ""
                self.load_progress_logs()
            else:
                print(f"❌ Failed to log progress: {response.text}")
        except Exception as e:
            print(f"🚨 ERROR: {e}")
            print(f"🚨 ERROR logging progress: {e}")


    def load_progress_logs(self):
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")
        progress_list = self.ids.progress_list
        progress_list.clear_widgets()

        try:
            response = requests.get(f"http://127.0.0.1:8000/progress/{user_id}")
            if response.status_code == 200:
                logs = response.json()
                if not logs:
                    progress_list.add_widget(OneLineListItem(text="No progress entries yet."))
                    return

                for log in logs[::-1]:  # Show latest on top
                    date = log.get("date", "")[:10] if log.get("date") else "Unknown Date"
                    height = log.get("height", "N/A")
                    weight = log.get("weight", "N/A")
                    item = OneLineListItem(
                        text=f"{date}: Height {height} cm, Weight {weight} kg"
                    )
                    progress_list.add_widget(item)
            else:
                print("❌ Failed to load logs")

        except Exception as e:
            print(f"🚨 ERROR fetching logs: {e}")

    def show_graphs(self):
        try:
            app = MDApp.get_running_app()
            user_id = app.user_info.get("id")

            response = requests.get(f"http://127.0.0.1:8000/progress/{user_id}")
            if response.status_code != 200:
                print("❌ Failed to fetch progress data")
                return

            logs = response.json()
            if not logs:
                print("⚠️ No logs to display")
                return

            dates = [log["date"][:10] for log in logs]
            heights = [log["height"] for log in logs]
            weights = [log["weight"] for log in logs]
            bmis = []

            for h, w in zip(heights, weights):
                try:
                    height_m = h / 100
                    height_m = h / 100  # convert to meters
                    bmi = w / (height_m ** 2)
                    bmis.append(round(bmi, 2))
                except:
                    bmis.append(None)

            # Plotting
            plt.figure(figsize=(12, 6))
            plt.plot(dates, heights, marker='o', label="Height (cm)")
            plt.plot(dates, weights, marker='o', label="Weight (kg)")
            plt.plot(dates, bmis, marker='o', linestyle='--', label="BMI")

            plt.title("📈 Progress Over Time", fontsize=16, fontweight='bold')
            plt.xlabel("Date", fontsize=12)
            plt.ylabel("Values", fontsize=12)
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.6)
            # Plotting graphs
            plt.figure(figsize=(10, 6))
            plt.plot(dates, heights, marker='o', label="Height (cm)")
            plt.plot(dates, weights, marker='o', label="Weight (kg)")
            plt.plot(dates, bmis, marker='o', label="BMI", linestyle='--')
            plt.title("Progress Over Time")
            plt.xlabel("Date")
            plt.ylabel("Values")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()


            core_image = CoreImage(buf, ext='png')
            image = Image(texture=core_image.texture)

            self.graph_popup = Popup(title="Progress Graphs", content=image, size_hint=(0.9, 0.9))
            self.graph_popup.open()

        except Exception as e:
            print(f"🚨 ERROR showing graphs: {e}")

    def show_completed_workouts_graph(self):
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")

        try:
            # Fetch workout logs
            response = requests.get(f"http://127.0.0.1:8000/workout_logs/{user_id}")
            if response.status_code != 200:
                print(f"❌ Failed to fetch workout logs: {response.text}")
                return

            logs = response.json()
            if not logs:
                print("⚠️ No workout logs found.")
                return

            # Count each exercise_id
            counter = Counter([entry["exercise_id"] for entry in logs])

            # Map exercise_id to name
            exercise_map = {
                ex["id"]: ex["name"]
                for ex in ExerciseAPI.fetch_exercises()
            }

            names = [exercise_map.get(ex_id, f"Exercise {ex_id}") for ex_id in counter.keys()]
            counts = list(counter.values())

            # Create bar chart
            plt.figure(figsize=(12, 6))
            plt.bar(names, counts)
            plt.xlabel("Exercise")
            plt.ylabel("Times Completed")
            plt.title("Workout Completion Count")
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()

            # Save to buffer
            buf = BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plt.close()

            # Show image in popup
            image = CoreImage(buf, ext="png")
            img_widget = Image(texture=image.texture, size_hint_y=None, height="400dp")
            box = MDBoxLayout(orientation='vertical', padding=10)
            box.add_widget(img_widget)

            self.graph_popup = MDDialog(
                title="Completed Workouts",
                type="custom",
                content_cls=box,
                buttons=[]
            )
            self.graph_popup.open()

        except Exception as e:
            print(f"🚨 Error showing graph: {e}")

    def load_achievements(self):
        app = MDApp.get_running_app()
        user_id = app.user_info.get("id")
        try:
            response = requests.get(f"http://127.0.0.1:8000/achievements/{user_id}")
            if response.status_code == 200:
                data = response.json()
                achievements = data.get("achievements", [])

                container = self.ids.achievement_box
                container.clear_widgets()

                if achievements:
                    for badge in achievements:
                        chip = MDChip(
                            label=badge,
                            icon="star-circle-outline",
                            check=False
                        )
                        container.add_widget(chip)
                else:
                    container.add_widget(MDLabel(text="No achievements yet!", halign="center"))

            else:
                print(f"❌ Failed to fetch achievements: {response.status_code}")
        except Exception as e:
            print(f"🚨 Error fetching achievements: {e}")

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
Factory.register("GuestExerciseDetailScreen", cls=GuestExerciseDetailScreen)
Factory.register("ProgressScreen", cls=ProgressScreen)
Factory.register("EditWorkoutScreen", cls=EditWorkoutScreen)

# ✅ Load all KV Files Dynamically
BASE_DIR = os.path.dirname(__file__)
KV_DIR = os.path.join(BASE_DIR, "screens")
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
        self.sm.add_widget(ProgressScreen(name="progress"))
        self.sm.add_widget(EditWorkoutScreen(name="edit_workout"))


        # ✅ Add screens for each workout category
        self.sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        self.sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        self.sm.add_widget(OutdoorScreen(name="outdoor"))
        self.sm.add_widget(WellnessScreen(name="wellness"))

        self.sm.add_widget(ExerciseDetailScreen(name="exercise_detail"))
        self.sm.add_widget(GuestExerciseDetailScreen(name="exercise_detail_guest"))
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

    def show_guest_exercise(self, exercise_id):
        screen = self.root.get_screen("exercise_detail_guest")
        screen.display_exercise(exercise_id)
        self.root.current = "exercise_detail_guest"

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
        screen = self.root.get_screen("edit_workout")
        screen.load_exercise_data(str(exercise_id))  # ✅ Force it to be a string
        self.root.current = "edit_workout"

    def edit_height(self):
        self.dialog = MDDialog(
            title="Edit Height",
            type="custom",
            content_cls=MDTextField(hint_text="Enter New Height in cm", input_filter='int'),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda _: self.confirm_edit_user("height")
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=lambda _: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def edit_weight(self):
        self.dialog = MDDialog(
            title="Edit Weight",
            type="custom",
            content_cls=MDTextField(hint_text="Enter New Weight in kg", input_filter='int'),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=lambda _: self.confirm_edit_user("weight")
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=lambda _: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    def confirm_edit_user(self, field):
        new_value = self.dialog.content_cls.text.strip()
        self.dialog.dismiss()

        if not new_value.isdigit():
            print("❌ Invalid input. Please enter a number.")
            return

        user_id = self.user_info.get("id")
        if not user_id:
            print("❌ User not logged in")
            return

        payload = {field: int(new_value)}
        url = f"http://127.0.0.1:8000/user/{user_id}/update"

        try:
            response = requests.put(url, json=payload)
            if response.status_code == 200:
                print(f"✅ Successfully updated {field} to {new_value}")
                self.user_info[field] = int(new_value)

                # ✅ Update UI immediately
                user_screen = self.root.get_screen("user")
                if field == "height":
                    user_screen.ids.height_label.text = f"{new_value} cm"
                elif field == "weight":
                    user_screen.ids.weight_label.text = f"{new_value} kg"

            else:
                print(f"❌ Failed to update {field}: {response.json()}")
        except Exception as e:
            print(f"🚨 Error updating {field}: {e}")

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

        def confirm_delete(instance):
            print(f"📌 Attempting to delete exercise with ID: {exercise_id}")
            url = f"http://127.0.0.1:8000/api/exercises/{exercise_id}"
            response = requests.delete(url)

            if response.status_code == 200:
                print(f"✅ Exercise {exercise_id} deleted successfully!")
                self.switch_to_home()
            else:
                print(f"❌ Error deleting exercise: {response.json()}")

            dialog.dismiss()

        dialog = MDDialog(
            title="Delete Exercise",
            text="Are you sure you want to delete this exercise?",
            buttons=[
                MDRaisedButton(text="Yes", on_release=lambda _: confirm_delete(None)),
                MDRaisedButton(text="No", on_release=lambda _: dialog.dismiss())
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

    def toggle_bookmark(self, exercise_id, exercise_name, save_button):
        user_id = self.user_info.get("id")
        if not user_id:
            print("🚨 No user logged in")
            return

        try:
            response = requests.post(f"http://127.0.0.1:8000/toggle_saved/{user_id}/{exercise_id}")
            if response.status_code == 200:
                if exercise_name in self.saved_exercises:
                    self.saved_exercises.remove(exercise_name)
                    save_button.icon = "bookmark-outline"
                    print(f"❌ Unsaved {exercise_name}")
                else:
                    self.saved_exercises.add(exercise_name)
                    save_button.icon = "bookmark"
                    print(f"✅ Saved {exercise_name}")
                self.update_saved_screen()
            else:
                print(f"❌ Failed to toggle bookmark: {response.text}")
        except Exception as e:
            print(f"🚨 Error while toggling saved exercise: {e}")

    def switch_to_add_workout(self):
        """Switch to AddWorkoutScreen."""
        self.switch_to_screen("add_workout")

    def submit_workout(self):
        screen = self.root.get_screen("add_workout")

        print(f"📸 Path to upload: {screen.selected_image_path}")

        # ✅ Upload the image
        image_url = screen.upload_image_to_cloudinary()
        if not image_url:
            image_url = "https://res.cloudinary.com/dudftatqj/image/upload/v1741316241/logo_iehkuj.png"

        # ✅ Build the workout data
        try:
            workout_data = {
                "name": screen.ids.workout_name.text.strip(),
                "description": screen.ids.workout_description.text.strip(),
                "toughness": screen.selected_toughness,
                "tags": screen.selected_tags,
                "media_url": image_url,
                "suggested_reps": int(screen.ids.workout_reps.text) if screen.ids.workout_reps.text.isdigit() else 10
            }
        except Exception as e:
            print(f"❌ Failed to build workout data: {e}")
            return

        print(f"📤 Submitting workout: {workout_data}")
        print(f"🧾 Final Payload Sent:\n{json.dumps(workout_data, indent=2)}")

        # ✅ Send to backend
        try:
            response = requests.post("http://127.0.0.1:8000/add_exercise/", json=workout_data)
            print(f"📥 API Response: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"❌ Could not reach backend: {e}")
            return

        if response.status_code == 200:
            print("✅ Workout added successfully!")
            self.root.current = "user"
        else:
            print(f"❌ Error adding workout: {response.json()}")


if __name__ == "__main__":
    try:
        MainApp().run()
    except AttributeError as e:
        print(f"🚨 AttributeError: {e}")
    except Exception as e:
        print(f"🚨 ERROR: {e}")
