
# FlexFit App

FlexFit is a fitness application designed to help users achieve a healthier lifestyle by logging workouts, searching for new exercises, and utilizing additional fitness features. The app aims to revolutionize the fitness industry by giving users complete control over every aspect of their workouts.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Team](#team)
- [License](#license)

## Features
- **Workout Logging:** Log your completed workouts and track your progress day by day.
- **Search Workouts:** Discover exercises tailored to your fitness goals, preferences, and equipment access.
- **Exercise Editing & Deletion:** Edit or delete workouts, including their name, reps, difficulty, image, and more.
- **Saved Workouts:** Bookmark your favorite exercises to easily access them later.
- **User Profile:** Create and update your personalized profile to reflect your goals and preferences.
- **Progress Tracking:**
  - Log and track height, weight, and BMI over time.
  - Visual graphs for **Height over Time**, **Weight over Time**, and **BMI trends**.
- **Media Support:** Upload and associate images with exercises using cloud integration.
- **Modern UI:** Smooth, intuitive interface built using KivyMD with real-time updates and interactive components.


## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CSCI2040U/FlexFit_App.git
    ```


### 🚀 FlexFit App Setup Guide

Welcome to the **setup** folder for the FlexFit App!  
This folder contains scripts to help you get the project running smoothly on different operating systems.

---

### 🖥️ Windows Users

Run the following file:

```
setup\setup.bat
```

### How:
- Double-click the file, or
- Open Command Prompt, navigate to the `setup` directory, and run:
  ```
  setup.bat
  ```

---

### 🐧 Linux / macOS Users

Run the following file:

```
setup\setup.sh
```

### How:
```bash
cd setup
chmod +x setup.sh
./setup.sh
```

---

> ⚠️ NOTE: These scripts do **not** build the Android APK.  
> The `buildozer.spec` file is included for that. APK building is required on a Linux machine.

## Usage

1. Launch the app and create a new user profile if you're a first-time user.
2. Navigate to the "Workout Logging" section to start tracking your exercises.
3. Use the "Discover Workouts" feature to explore new workout routines based on your fitness goals.
4. Monitor your progress by checking the "Progress" section to see your stats over time.
5. Customize your settings, goals, and preferences from the profile menu.

## Contributing

1. Fork this repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request with a clear description of the changes.

We appreciate any contributions, whether it's reporting bugs, suggesting improvements, or submitting code!

## Technologies Used

### 🧠 **Backend**
- **FastAPI** – High-performance Python web framework for building RESTful APIs.
- **SQLAlchemy** – Database ORM used for handling models and queries.
- **SQLite** – Lightweight, serverless database used for storing user data, workouts, progress logs, and achievements.
- **Cloudinary** – Cloud-based media management for storing and serving workout images.

### 🎨 **Frontend**
- **Kivy** – Cross-platform Python framework for building multi-touch applications.
- **KivyMD** – Material Design components for Kivy to enhance the UI/UX.
- **Matplotlib** – Visualization library used for generating graphs and progress charts.
- **Pillow (PIL)** – Image processing library used for handling image uploads and previews.

### 🔧 **Dev Tools & Deployment**
- **Buildozer** – Tool for packaging the app for Android (Linux-only build).
- **Python 3.x** – Core programming language for both frontend and backend.
- **Setup Scripts (Batch/Shell)** – Easy cross-platform setup using `.bat` and `.sh` files.
- **Git & GitHub** – Version control and collaboration.

## Team

Meet the passionate developers behind FlexFit:

- [@devarshh](https://github.com/devarshh)
- [@kandoimansi](https://github.com/kandoimansi) 
- [@patelaryan5](https://github.com/patelaryan5)
- [@Jollysoni](https://github.com/Jollysoni)
- [@22mihirghosh](https://github.com/22mihirghosh)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## THE END
