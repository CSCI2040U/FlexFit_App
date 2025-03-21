
# 🚀 FlexFit App Setup Guide

Welcome to the **setup** folder for the FlexFit App!  
This folder contains scripts to help you get the project running smoothly on different operating systems.

---

## 🖥️ Windows Users

Run the following file:

```
setup.bat
```

### How:
- Double-click the file, or
- Open Command Prompt, navigate to the `setup` directory, and run:
  ```
  setup.bat
  ```

---

## 🐧 Linux / macOS Users

Run the following file:

```
setup.sh
```

### How:
```bash
cd setup
chmod +x setup.sh
./setup.sh
```

---

## 📦 What These Scripts Do

- Create a virtual environment
- Activate it
- Upgrade pip
- Install all Python dependencies from `requirements.txt`

---

> ⚠️ NOTE: These scripts do **not** build the Android APK.  
> The `buildozer.spec` file is included for future use after development is complete and APK building is required on a Linux machine.

---

Happy coding!
