from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty
from kivy.factory import Factory

# ✅ Workout Item Class (For Clickable List Items)
class WorkoutItem(RecycleDataViewBehavior, ButtonBehavior, MDBoxLayout):
    """A clickable workout item inside the RecycleView."""
    title = StringProperty("")
    image_source = StringProperty("")
    target_screen = StringProperty("")

    def on_release(self):
        """Switch to the target screen when clicked."""
        if self.target_screen:
            print(f'Navigating to {self.target_screen}!')
            app = MDApp.get_running_app()
            app.root.current = self.target_screen

# ✅ Register the class so Kivy can use it in KV
Factory.register("WorkoutItem", cls=WorkoutItem)

# ✅ Saved Workouts Screen
class SavedScreen(Screen):
    def on_enter(self):
        """Populate the saved workout list dynamically when entering the screen."""
        self.populate_saved_workout_list()

    def populate_saved_workout_list(self):
        """Dynamically add saved workouts to the list."""
        data = [
            {"title": "With Equipment", "image_source": "assets/indoor_workout.jpg", "target_screen": "with_equipment"},
            {"title": "Exercise #2", "image_source": "assets/exercise2.jpg", "target_screen": "exercise_2"},
            {"title": "Without Equipment", "image_source": "assets/indoor_workout.jpg", "target_screen": "without_equipment"},
            {"title": "Outdoor", "image_source": "assets/outdoor_workout.jpg", "target_screen": "outdoor"},
            {"title": "Wellness", "image_source": "assets/wellness_workout.jpg", "target_screen": "wellness"},
        ]

        rv_list = self.ids.saved_workout_list
        rv_list.data = [
            {
                "title": item["title"],
                "image_source": item["image_source"],
                "target_screen": item["target_screen"]
            } for item in data
        ]  # ✅ Load data into RecycleView

# ✅ Workout Detail Screens
class WithEquipmentScreen(Screen):
    pass

class WithoutEquipmentScreen(Screen):
    pass

class OutdoorScreen(Screen):
    pass

class WellnessScreen(Screen):
    pass

# ✅ Initialize App
class MainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SavedScreen(name="saved"))
        sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        sm.add_widget(OutdoorScreen(name="outdoor"))
        sm.add_widget(WellnessScreen(name="wellness"))
        return sm

if __name__ == "__main__":
    MainApp().run()
