[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd,pyttsx3
orientation = portrait
osx.kivy_version = 2.2.1
python.version = 3.8
fullscreen = 0
android.archs = arm64-v8a
android.allow_backup = True
android.add_build_tools_to_path = True
android.private_storage = True
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
p4a.branch = master
p4a.fork = kivy
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.skip_update = False
android.sdk_build_tools_version = 33.0.0

# android.sdk_path = /usr/local/lib/android/sdk
# android.ndk_path = /usr/local/lib/android/sdk/ndk-bundle
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_dir = ./.buildozer

