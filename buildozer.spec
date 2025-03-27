[app]
title = Ytify
package.name = ytify
package.domain = org.yourorganization
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
orientation = portrait

# (list) Application requirements
requirements = python3,kivy,innertube,requests

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (list of orientations)
orientation = portrait, landscape

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 30

# (int) Minimum API your APK will support.
android.minapi = 24

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk = 

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# Gradle dependencies
android.gradle_dependencies = com.google.android.material:material:1.4.0

# Allow turning screen orientation
android.whitelist = lib-main.so

# Allow loading so library
android.add_aars = 

# (list) Java .jar files to add (currently only for p4a projects)
#android.add_jars = 

# (bool) Indicate whether the screen should stay on
#android.wakelock = False

# (list) Supported ABIs, specify architectures to build your app for
android.archs = arm64-v8a

# Ensure you have the following packages
android.accept_sdk_license = True
