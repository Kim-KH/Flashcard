[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd,pyjnius,audiostream
orientation = portrait
osx.kivy_version = 2.2.1
python.version = 3.8
fullscreen = 0
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
android.ndk = 25b
android.ndk_api = 21
p4a.branch = master
p4a.fork = kivy
android.release_artifact = aab
android.debug_artifact = apk
android.p4a_whitelist = lib-dynload/_ctypes.so
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.skip_update = False
android.sdk_build_tools_version = 33.0.0
pip_upgrade_command = python -m pip install --upgrade pip

android.ant_path = /path/to/apache-ant-1.9.4
android.sdk_path = /github/workspace/.buildozer/android/platform/android-sdk
android.ndk_path = /github/workspace/.buildozer/android/platform/android-ndk-r25b
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_dir = ./.buildozer

