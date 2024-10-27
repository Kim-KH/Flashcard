[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,kivymd,pyjnius,pillow,requests,gtts,kivy_garden.graph
orientation = portrait
fullscreen = 0
android.gradle_dependencies = androidx.webkit:webkit:1.4.0
android.gradle_version = 8.0.2
osx.kivy_version = 2.2.1
python.version = 3.9

# Android specific settings
android.archs = arm64-v8a
android.allow_backup = True
android.add_build_tools_to_path = True
android.private_storage = True
android.accept_sdk_license = True
android.enable_androidx = True
android.gradle_use_latest = True
android.add_dependencies = ffmpeg
android.api = 33
android.minapi = 21
# android.sdk = 31
android.ndk = 25b
android.ndk_api = 21
android.release_artifact = aab
android.debug_artifact = apk
android.whitelist = lib-dynload/_ctypes.so
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.skip_update = False
android.sdk_build_tools_version = 33.0.0
garden_requirements =
android.gradle_args = --stacktrace --debug

android.java_version = 11
p4a.branch = master
p4a.fork = kivy
p4a.dist_name = pyjnius
p4a.bootstrap = sdl2
p4a.source_dir = /home/runner/work/Flashcard/Flashcard/python-for-android
# Build tools paths
#android.ant_path = /usr/share/ant
#android.sdk_path = /usr/local/lib/android/sdk
#android.ndk_path = /usr/local/lib/android/sdk/ndk/27.1.12297006
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager
android.add_gradle_repositories = maven { url 'https://maven.google.com' }
android.extra_gradle_args = -Pandroid.useAndroidX=true -Pandroid.enableJetifier=true

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
buildozer.enable_cache = False
