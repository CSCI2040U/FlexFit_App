[app]
title = FlexFit
package.name = flexfit
package.domain = org.flexfit
source.include_exts = py,png,jpg,kv,atlas

# Main file to launch
source.main = frontend/flexfit.py

# Icon (optional)
# icon.filename = icon.png

# Include all files in assets directory
# android.presplash = %(source.dir)s/data/presplash.png

# Requirements (all dependencies here)
requirements = python3,kivy,kivymd

# Supported orientation
orientation = portrait

# Android version
android.api = 31
android.minapi = 21

# Architectures (keep arm64-v8a at least)
android.archs = arm64-v8a

# Permissions (add only if needed)
android.permissions = INTERNET

# Package format
android.packaging = apk
