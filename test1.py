from kivymd.app import MDApp  # ✅ Use MDApp instead of App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivy.factory import Factory

# ✅ Ensure HomeScreen is registered
class HomeScreen(Screen):
    pass

class WithEquipmentScreen(Screen):
    pass

class WithoutEquipmentScreen(Screen):
    pass

class OutdoorScreen(Screen):
    pass

class WellnessScreen(Screen):
    pass

# ✅ Clickable MDCard Class
class ClickableCard(ButtonBehavior, MDCard):
    target_screen = StringProperty("")

    def on_release(self):
        if self.target_screen:
            print(f"🔄 Navigating to {self.target_screen}")  # Debugging
            self.parent.parent.parent.manager.current = self.target_screen  # Ensure screen switching

# ✅ Register classes in Factory
Factory.register("HomeScreen", cls=HomeScreen)
Factory.register("WithEquipmentScreen", cls=WithEquipmentScreen)
Factory.register("WithoutEquipmentScreen", cls=WithoutEquipmentScreen)
Factory.register("OutdoorScreen", cls=OutdoorScreen)
Factory.register("WellnessScreen", cls=WellnessScreen)
Factory.register("ClickableCard", cls=ClickableCard)

# ✅ Load KV file (Ensure the path is correct)
kv = Builder.load_file("test1.kv")  # Adjust if necessary

# ✅ Initialize App
class MainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(WithEquipmentScreen(name="with_equipment"))
        sm.add_widget(WithoutEquipmentScreen(name="without_equipment"))
        sm.add_widget(OutdoorScreen(name="outdoor"))
        sm.add_widget(WellnessScreen(name="wellness"))
        return sm

if __name__ == "__main__":
    MainApp().run()
