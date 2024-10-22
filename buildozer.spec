[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,kivymd,pyjnius,audiostream,pillow,requests,gtts
orientation = portrait
fullscreen = 0

# Python and Kivy versions
osx.kivy_version = 2.2.1
python.version = 3.9

# Android specific settings
android.archs = arm64-v8a
android.allow_backup = True
android.add_build_tools_to_path = True
android.private_storage = True
android.accept_sdk_license = True
android.enable_androidx = True
android.add_dependencies = ffmpeg
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25.2.9519653
android.ndk_api = 21
android.release_artifact = aab
android.debug_artifact = apk
android.whitelist = lib-dynload/_ctypes.so
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.skip_update = False
android.sdk_build_tools_version = 33.0.0

android.java_version = 11
p4a.branch = develop
p4a.fork = kivy
p4a.dist_name = pyjnius
p4a.bootstrap = sdl2
p4a.source_dir = /home/runner/.buildozer/android/platform/python-for-android 
# Build tools paths
#android.ant_path = /usr/share/ant
#android.sdk_path = /usr/local/lib/android/sdk
#android.ndk_path = /usr/local/lib/android/sdk/ndk/27.1.12297006
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager

# iOS specific settings
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

# Pip upgrade command
pip_upgrade_command = python -m pip install --upgrade pip

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_dir = ./.buildozer
p4a.source_dir = /home/runner/.buildozer/android/platform/python-for-android
