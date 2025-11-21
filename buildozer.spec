[app]

# (str) Title of your application
title = GPA Simulator

# (str) Package name
package.name = gpasimulator

# (str) Package domain (needed for android/ios packaging)
package.domain = org.deniscodez

# (source.dir) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,txt,db,ico

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, dist*, build, .git, .github, __pycache__

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,flask,werkzeug,jinja2,markupsafe,sqlite3

# (str) Supported orientation (landscape, sensorLandscape, portrait or sensorPortrait)
orientation = portrait

# (list) List of service to declare
#services = MyServiceLabel:myapp.Service

################################################################################
# Android specific
################################################################################

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash of the application (image or text+image)
# presplash.filename = %(source.dir)s/data/presplash.png

# (list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (list) Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a,armeabi-v7a

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) Android API level to target
android.api = 31

# (int) Minimum API level (depends on used features)
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 30

# (str) Android NDK version to use
#android.ndk = 23b

# (bool) Use legacy toolchain
android.use_legacy_toolchain = False

# (bool) Enable on screen keyboard on startup
android.keyboard_layout = qwerty

# Accept Android SDK licenses automatically
android.accept_sdk_license = True

# Gradle options to accept licenses
android.gradle_dependencies =

################################################################################
# iOS specific
################################################################################

# (str) Path to a custom kivy.spec file

################################################################################
# Buildozer logging and etc
################################################################################

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warnings (0 = off, 1 = on (default))
warn_on_root = 1
