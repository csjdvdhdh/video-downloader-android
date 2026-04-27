here[app]
title = Video Downloader
package.name = videodownloader
package.domain = org.example
source.dir = .
source.include_exts = py
version = 1.0.0
requirements = python3,kivy,kivymd,yt-dlp,ffmpeg,android
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0

# أيقونة التطبيق (اختياري)
icon.filename = icon.png

# الأذونات
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.gradle_dependencies = 

# تضمين ffmpeg
android.add_src = 

[buildozer]
log_level = 2
warn_on_root = 1
