[app]
title = MissingApp
package.name = missingapp
package.domain = org.missingapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,kivymd,requests,plyer,urllib3,idna,chardet,certifi,geopy,kivy_garden.mapview,openssl
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 31
android.minapi = 21
p4a.branch = master
[buildozer]
log_level = 2
warn_on_root = 1