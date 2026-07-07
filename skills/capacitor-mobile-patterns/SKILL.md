---
name: capacitor-mobile-patterns
description: Capacitor Android wrapper, APK signing, native plugins, build configuration
---

# Capacitor Mobile Patterns

Patterns for building and shipping mobile apps with Capacitor.

## When to use

- Wrapping a web app in a native Android/iOS container
- Configuring APK signing for production releases
- Integrating Capacitor native plugins

## Instructions

1. **Initialize Capacitor** — `npx cap init` to add Android/iOS platforms
2. **Configure the Android wrapper** — update `android/app/build.gradle` with signing config, app name, and icons
3. **Set up APK signing**:
   - Generate a keystore: `keytool -genkey -v -keystore my-app.keystore -alias my-app -keyalg RSA -keysize 2048`
   - Add signing config to `build.gradle`
4. **Integrate native plugins** — `npx cap sync` after adding plugins
5. **Build and sign** — `cd android && ./gradlew assembleRelease`
6. **Deploy** — upload the signed APK/AAB to Google Play or distribute directly

## Common patterns

- **Splash screen**: configure via Capacitor Splash Screen plugin
- **Push notifications**: Firebase Cloud Messaging + Capacitor Push Notifications
- **Deep linking**: configure intent filters in AndroidManifest.xml
- **File access**: use Capacitor Filesystem plugin for reading/writing files

## Edge cases

- ProGuard rules (keep Capacitor and plugin classes from being stripped)
- Android 13+ notification permission (must request at runtime)
- App bundle vs APK (App Bundles are required for Google Play)
