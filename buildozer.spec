[app]
title = Flashcard App
package.name = flashcardapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,kivymd,pyjnius==1.4.2,audiostream,pillow,requests,gtts
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
<<<<<<< HEAD
p4a.branch = master
android.accept_sdk_license = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.skip_update = True
android.sdk_build_tools_version = 33.0.0
android.add_build_tools_to_path = True
=======
p4a.branch = develop
p4a.fork = kivy
p4a.dist_name = pyjnius
p4a.bootstrap = sdl2

android.release_artifact = aab
android.debug_artifact = apk
android.p4a_whitelist = lib-dynload/_ctypes.so
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,RECORD_AUDIO
android.skip_update = False
android.sdk_build_tools_version = 33.0.0
pip_upgrade_command = python -m pip install --upgrade pip

android.ant_path = /usr/share/ant
android.sdk_path = /github/workspace/.buildozer/android/platform/android-sdk
android.ndk_path = /github/workspace/.buildozer/android/platform/android-ndk-r25b
android.sdkmanager_path = /home/buildozer/.buildozer/android/platform/android-sdk/cmdline-tools/latest/bin/sdkmanager

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0
ios.codesign.allowed = false
>>>>>>> 5f8b3313e3b64489c74f5959e077aedaf4461a8c

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_dir = ./.buildozer

