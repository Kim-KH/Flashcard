[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pillow,requests,gtts,pyjnius,kivymd
orientation = portrait
osx.kivy_version = 2.2.1
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25
android.ndk_api = 21
p4a.branch = master
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.skip_update = True
android.sdk_build_tools_version = 33.0.0
android.add_build_tools_to_path = True

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_dir = ./.buildozer
p4a.source_dir = /home/buildozer/app/.buildozer/android/platform/python-for-android
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager
