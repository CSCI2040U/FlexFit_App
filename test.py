import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle

# Set window size to match mobile dimensions
Window.size = (400, 800)

# Define color constants
PRIMARY_COLOR = get_color_from_hex('#8B5CF6')  # Purple color from the design
BACKGROUND_COLOR = get_color_from_hex('#F9FAFB')
TEXT_COLOR = get_color_from_hex('#1F2937')
LIGHT_TEXT_COLOR = get_color_from_hex('#6B7280')
CARD_BACKGROUND = get_color_from_hex('#F3F4F6')


class LogoWidget(FloatLayout):
    def __init__(self, **kwargs):
        super(LogoWidget, self).__init__(**kwargs)
        with self.canvas:
            # Purple background
            Color(*PRIMARY_COLOR[:3], 1)
            self.circle = Ellipse(pos=self.pos, size=self.size)

            # White "F" letter
            Color(1, 1, 1, 1)
            # Vertical line of F
            self.line1 = Rectangle(pos=(self.x + self.width * 0.35, self.y + self.height * 0.25),
                                   size=(self.width * 0.1, self.height * 0.5))
            # Top horizontal line of F
            self.line2 = Rectangle(pos=(self.x + self.width * 0.35, self.y + self.height * 0.65),
                                   size=(self.width * 0.4, self.height * 0.1))
            # Middle horizontal line of F
            self.line3 = Rectangle(pos=(self.x + self.width * 0.35, self.y + self.height * 0.45),
                                   size=(self.width * 0.3, self.height * 0.1))

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.circle.pos = self.pos
        self.circle.size = self.size
        self.line1.pos = (self.x + self.width * 0.35, self.y + self.height * 0.25)
        self.line1.size = (self.width * 0.1, self.height * 0.5)
        self.line2.pos = (self.x + self.width * 0.35, self.y + self.height * 0.65)
        self.line2.size = (self.width * 0.4, self.height * 0.1)
        self.line3.pos = (self.x + self.width * 0.35, self.y + self.height * 0.45)
        self.line3.size = (self.width * 0.3, self.height * 0.1)


class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super(WelcomeScreen, self).__init__(**kwargs)

        layout = FloatLayout()
        layout.canvas.before = BACKGROUND_COLOR

        # Logo
        logo_container = FloatLayout(
            size_hint=(0.4, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        )
        logo = LogoWidget()
        logo_container.add_widget(logo)

        # App name
        app_name = Label(
            text='FlexFit',
            font_size=dp(32),
            color=PRIMARY_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            bold=True
        )

        # Login button
        login_btn = Button(
            text='Login',
            background_color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            background_normal=''
        )
        login_btn.bind(on_press=self.go_to_login)

        # Register button
        register_btn = Button(
            text='Register',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.22},
            background_normal=''
        )
        register_btn.bind(on_press=self.go_to_register)

        layout.add_widget(logo_container)
        layout.add_widget(app_name)
        layout.add_widget(login_btn)
        layout.add_widget(register_btn)

        self.add_widget(layout)

    def go_to_login(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'login'

    def go_to_register(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'register'


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Title
        title = Label(
            text='Welcome Back!',
            font_size=dp(24),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            bold=True
        )

        # Email input
        email_input = TextInput(
            hint_text='Email',
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            multiline=False
        )

        # Password input
        password_input = TextInput(
            hint_text='Password',
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            multiline=False,
            password=True
        )

        # Login button
        login_btn = Button(
            text='Login',
            background_color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            background_normal=''
        )
        login_btn.bind(on_press=self.go_to_home)

        # Register link
        register_link = Label(
            text="Don't have an account? Sign up",
            font_size=dp(14),
            color=LIGHT_TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.35}
        )

        # Back button
        back_btn = Button(
            text='Back',
            size_hint=(0.2, 0.05),
            pos_hint={'x': 0.05, 'top': 0.95},
            background_color=(0, 0, 0, 0),
            color=TEXT_COLOR
        )
        back_btn.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(email_input)
        layout.add_widget(password_input)
        layout.add_widget(login_btn)
        layout.add_widget(register_link)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Title
        title = Label(
            text='Create an Account',
            font_size=dp(24),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            bold=True
        )

        # Name input
        name_input = TextInput(
            hint_text='Full Name',
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
            multiline=False
        )

        # Email input
        email_input = TextInput(
            hint_text='Email',
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            multiline=False
        )

        # Password input
        password_input = TextInput(
            hint_text='Password',
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.55},
            multiline=False,
            password=True
        )

        # Register button
        register_btn = Button(
            text='Register',
            background_color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_normal=''
        )
        register_btn.bind(on_press=self.go_to_onboarding)

        # Login link
        login_link = Label(
            text="Already have an account? Sign in",
            font_size=dp(14),
            color=LIGHT_TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )

        # Back button
        back_btn = Button(
            text='Back',
            size_hint=(0.2, 0.05),
            pos_hint={'x': 0.05, 'top': 0.95},
            background_color=(0, 0, 0, 0),
            color=TEXT_COLOR
        )
        back_btn.bind(on_press=self.go_back)

        layout.add_widget(title)
        layout.add_widget(name_input)
        layout.add_widget(email_input)
        layout.add_widget(password_input)
        layout.add_widget(register_btn)
        layout.add_widget(login_link)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def go_to_onboarding(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'onboarding'

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'welcome'


class OnboardingScreen(Screen):
    def __init__(self, **kwargs):
        super(OnboardingScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Title
        title = Label(
            text='Let\'s Select Your Goal',
            font_size=dp(20),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.85},
            bold=True
        )

        # Goal options (using images and labels)
        # In a real app, these would be proper selectable cards
        goal_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(0.8, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Goal options (simplified)
        goals = ["Lose Weight", "Build Muscle", "Improve Fitness", "Reduce Stress"]

        for goal in goals:
            goal_btn = Button(
                text=goal,
                background_color=CARD_BACKGROUND,
                color=TEXT_COLOR,
                size_hint=(1, None),
                height=dp(50),
                background_normal=''
            )
            goal_layout.add_widget(goal_btn)

        # Next button
        next_btn = Button(
            text='Continue',
            background_color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            background_normal=''
        )
        next_btn.bind(on_press=self.go_to_home)

        layout.add_widget(title)
        layout.add_widget(goal_layout)
        layout.add_widget(next_btn)

        self.add_widget(layout)

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'home'


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Header
        header = Label(
            text='Welcome, User!',
            font_size=dp(24),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.9},
            bold=True
        )

        # Workout categories
        categories_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(0.9, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )

        # Category cards (simplified)
        categories = ["Yoga", "Cardio", "Strength", "HIIT", "Stretching"]

        for category in categories:
            category_btn = Button(
                text=category,
                background_color=CARD_BACKGROUND,
                color=TEXT_COLOR,
                size_hint=(1, None),
                height=dp(80),
                background_normal=''
            )
            category_btn.bind(on_press=lambda x, c=category: self.go_to_category(c))
            categories_layout.add_widget(category_btn)

        # Bottom navigation
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0},
            spacing=dp(10),
            padding=[dp(20), 0]
        )

        # Home button (active)
        home_btn = Button(
            text='Home',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR,
            size_hint=(1, 1)
        )

        # Workouts button
        workouts_btn = Button(
            text='Workouts',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        workouts_btn.bind(on_press=self.go_to_workouts)

        # Profile button
        profile_btn = Button(
            text='Profile',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        profile_btn.bind(on_press=self.go_to_profile)

        nav_layout.add_widget(home_btn)
        nav_layout.add_widget(workouts_btn)
        nav_layout.add_widget(profile_btn)

        layout.add_widget(header)
        layout.add_widget(categories_layout)
        layout.add_widget(nav_layout)

        self.add_widget(layout)

    def go_to_category(self, category):
        # Store the selected category in App.selected_category
        App.get_running_app().selected_category = category
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'workout'

    def go_to_workouts(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'workout'

    def go_to_profile(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'profile'


class WorkoutScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Header with back button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )

        back_btn = Button(
            text='Back',
            size_hint=(0.2, 1),
            background_color=(0, 0, 0, 0),
            color=TEXT_COLOR
        )
        back_btn.bind(on_press=self.go_back)

        self.title_label = Label(
            text='Yoga',
            font_size=dp(20),
            color=TEXT_COLOR,
            size_hint=(0.6, 1),
            bold=True
        )

        header_layout.add_widget(back_btn)
        header_layout.add_widget(self.title_label)

        # Workout list
        self.workouts_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(0.9, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        # Bottom navigation (same as home)
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0},
            spacing=dp(10),
            padding=[dp(20), 0]
        )

        # Home button
        home_btn = Button(
            text='Home',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        home_btn.bind(on_press=self.go_to_home)

        # Workouts button (active)
        workouts_btn = Button(
            text='Workouts',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR,
            size_hint=(1, 1)
        )

        # Profile button
        profile_btn = Button(
            text='Profile',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        profile_btn.bind(on_press=self.go_to_profile)

        nav_layout.add_widget(home_btn)
        nav_layout.add_widget(workouts_btn)
        nav_layout.add_widget(profile_btn)

        layout.add_widget(header_layout)
        layout.add_widget(self.workouts_layout)
        layout.add_widget(nav_layout)

        self.add_widget(layout)

    def on_pre_enter(self):
        # This is called when the screen is about to be shown
        app = App.get_running_app()
        category = getattr(app, 'selected_category', 'Yoga')
        self.title_label.text = category

        # Clear previous workouts
        self.workouts_layout.clear_widgets()

        # Add workouts for the selected category
        workouts = self.get_workouts_for_category(category)
        for workout in workouts:
            workout_btn = Button(
                text=workout,
                background_color=CARD_BACKGROUND,
                color=TEXT_COLOR,
                size_hint=(1, None),
                height=dp(80),
                background_normal=''
            )
            workout_btn.bind(on_press=lambda x, w=workout: self.go_to_workout_detail(w))
            self.workouts_layout.add_widget(workout_btn)

    def get_workouts_for_category(self, category):
        workouts = {
            'Yoga': [
                'Beginner Yoga Flow - 20 min',
                'Morning Yoga Routine - 15 min',
                'Power Yoga - 30 min',
                'Yoga for Flexibility - 25 min'
            ],
            'Cardio': [
                'HIIT Cardio - 20 min',
                'Running Intervals - 30 min',
                'Jump Rope Workout - 15 min',
                'Cardio Kickboxing - 25 min'
            ],
            'Strength': [
                'Full Body Strength - 30 min',
                'Upper Body Focus - 20 min',
                'Lower Body Workout - 25 min',
                'Core Strength - 15 min'
            ],
            'HIIT': [
                'Tabata Intervals - 20 min',
                'Full Body HIIT - 30 min',
                'HIIT for Beginners - 15 min',
                'Advanced HIIT Circuit - 25 min'
            ],
            'Stretching': [
                'Full Body Stretch - 15 min',
                'Post-Workout Stretch - 10 min',
                'Morning Flexibility - 20 min',
                'Deep Stretch Routine - 25 min'
            ]
        }
        return workouts.get(category, workouts['Yoga'])

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def go_to_workout_detail(self, workout):
        app = App.get_running_app()
        app.selected_workout = workout
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'workout_detail'

    def go_to_profile(self, instance):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'profile'


class WorkoutDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(WorkoutDetailScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Header with back button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'top': 0.98}
        )

        back_btn = Button(
            text='Back',
            size_hint=(0.2, 1),
            background_color=(0, 0, 0, 0),
            color=TEXT_COLOR
        )
        back_btn.bind(on_press=self.go_back)

        self.title_label = Label(
            text='Yoga Session',
            font_size=dp(20),
            color=TEXT_COLOR,
            size_hint=(0.6, 1),
            bold=True
        )

        header_layout.add_widget(back_btn)
        header_layout.add_widget(self.title_label)

        # Workout image (placeholder)
        image_placeholder = BoxLayout(
            size_hint=(0.9, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        with image_placeholder.canvas.before:
            Color(*CARD_BACKGROUND[:3], 1)
            self.rect = Rectangle(pos=image_placeholder.pos, size=image_placeholder.size)
        image_placeholder.bind(pos=self.update_rect, size=self.update_rect)

        # Workout details
        details_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(0.9, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.45}
        )

        # Details
        self.description = Label(
            text='A gentle yoga flow perfect for beginners. This session focuses on basic poses and proper breathing techniques.',
            text_size=(Window.width * 0.85, None),
            halign='left',
            valign='top',
            color=TEXT_COLOR
        )

        self.info = Label(
            text='Duration: 20 minutes\nDifficulty: Beginner\nEquipment: Yoga mat',
            text_size=(Window.width * 0.85, None),
            halign='left',
            valign='top',
            color=TEXT_COLOR
        )

        details_layout.add_widget(self.description)
        details_layout.add_widget(self.info)

        # Start workout button
        start_btn = Button(
            text='Start Workout',
            background_color=PRIMARY_COLOR,
            size_hint=(0.8, 0.06),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            background_normal=''
        )

        layout.add_widget(header_layout)
        layout.add_widget(image_placeholder)
        layout.add_widget(details_layout)
        layout.add_widget(start_btn)

        self.add_widget(layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_pre_enter(self):
        # This is called when the screen is about to be shown
        app = App.get_running_app()
        workout = getattr(app, 'selected_workout', 'Beginner Yoga Flow - 20 min')

        # Update title and info
        if ' - ' in workout:
            name, duration = workout.split(' - ')
            self.title_label.text = name
            self.info.text = f'Duration: {duration}\nDifficulty: Beginner\nEquipment: Yoga mat'
        else:
            self.title_label.text = workout

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'workout'


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

        layout = FloatLayout()

        # Header
        header = Label(
            text='Profile',
            font_size=dp(24),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.9},
            bold=True
        )

        # Profile picture (placeholder)
        profile_pic_container = FloatLayout(
            size_hint=(0.3, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.8}
        )
        with profile_pic_container.canvas.before:
            Color(*CARD_BACKGROUND[:3], 1)
            self.profile_rect = Ellipse(pos=profile_pic_container.pos, size=profile_pic_container.size)
        profile_pic_container.bind(pos=self.update_profile_pic, size=self.update_profile_pic)

        # User name
        user_name = Label(
            text='John Doe',
            font_size=dp(18),
            color=TEXT_COLOR,
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            bold=True
        )

        # Stats
        stats_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            spacing=dp(10)
        )

        workouts_completed = Label(
            text='Workouts\n15',
            halign='center',
            color=TEXT_COLOR
        )

        minutes = Label(
            text='Minutes\n320',
            halign='center',
            color=TEXT_COLOR
        )

        calories = Label(
            text='Calories\n1,250',
            halign='center',
            color=TEXT_COLOR
        )

        stats_layout.add_widget(workouts_completed)
        stats_layout.add_widget(minutes)
        stats_layout.add_widget(calories)

        # Settings options
        settings_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint=(0.9, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.35}
        )

        # Settings items
        settings = ["Edit Profile", "Notifications", "Privacy", "Help & Support", "Logout"]

        for setting in settings:
            setting_btn = Button(
                text=setting,
                background_color=CARD_BACKGROUND,
                color=TEXT_COLOR,
                size_hint=(1, None),
                height=dp(40),
                background_normal=''
            )
            settings_layout.add_widget(setting_btn)

        # Bottom navigation
        nav_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.08),
            pos_hint={'center_x': 0.5, 'y': 0},
            spacing=dp(10),
            padding=[dp(20), 0]
        )

        # Home button
        home_btn = Button(
            text='Home',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        home_btn.bind(on_press=self.go_to_home)

        # Workouts button
        workouts_btn = Button(
            text='Workouts',
            background_color=(0, 0, 0, 0),
            color=LIGHT_TEXT_COLOR,
            size_hint=(1, 1)
        )
        workouts_btn.bind(on_press=self.go_to_workouts)

        # Profile button (active)
        profile_btn = Button(
            text='Profile',
            background_color=(0, 0, 0, 0),
            color=PRIMARY_COLOR,
            size_hint=(1, 1)
        )

        nav_layout.add_widget(home_btn)
        nav_layout.add_widget(workouts_btn)
        nav_layout.add_widget(profile_btn)

        layout.add_widget(header)
        layout.add_widget(profile_pic_container)
        layout.add_widget(user_name)
        layout.add_widget(stats_layout)
        layout.add_widget(settings_layout)
        layout.add_widget(nav_layout)

        self.add_widget(layout)

    def update_profile_pic(self, instance, value):
        self.profile_rect.pos = instance.pos
        self.profile_rect.size = instance.size

    def go_to_home(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'home'

    def go_to_workouts(self, instance):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'workout'


class FlexFitApp(App):
    selected_category = 'Yoga'
    selected_workout = 'Beginner Yoga Flow - 20 min'

    def build(self):
        # Create the screen manager
        sm = ScreenManager(transition=SlideTransition())

        # Add screens
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(OnboardingScreen(name='onboarding'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WorkoutScreen(name='workout'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        sm.add_widget(ProfileScreen(name='profile'))

        return sm


if __name__ == '__main__':
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')

    FlexFitApp().run()