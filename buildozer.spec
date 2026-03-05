[app]

# Title of the application
title = Synopsis - MBBS Study Companion

# Package name
package.name = synopsis

# Package domain
package.domain = org.gaurav.synopsis

# Source directory
source.dir = .

# Source includes - files to include
source.include_exts = py,png,jpg,kv,atlas,txt,pdf

# Version
version = 0.1

# Requirements - all dependencies
requirements = python3,kivy,streamlit,google-genai,PyPDF2,python-dotenv,gspread,google-auth-oauthlib,google-auth-httplib2,requests,urllib3,certifi,charset-normalizer,idna,typing-extensions,protobuf,pydantic-core

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Icon and presplash - using medical theme
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png

# Permissions for Android
android.permissions = INTERNET,CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Features
android.features = android.hardware.camera

# API levels
android.api = 31
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Arch
android.archs = arm64-v8a,armeabi-v7a

# Meta-data
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# Uses network state
android.uses_feature = android.hardware.camera

# Enable AndroidX
android.enable_androidx = True

# Gradle options
android.gradle_dependencies = 

# Entrypoint - use mobile_app.py for mobile-optimized version
p4a.bootstrap = webview
p4a.private_storage = True

[buildozer]

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning
warn_on_root = 1

# Specify the path to Android SDK
android_sdk_path = 

# Specify the path to Android NDK
android_ndk_path = 

[app:mobile]
# This section is for mobile-specific configuration
source.include_patterns = *.py,*.kv,*.png,*.jpg
