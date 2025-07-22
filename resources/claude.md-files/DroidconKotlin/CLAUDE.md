# DroidconKotlin Development Guide

## Build Commands
- Build: `./gradlew build`
- Clean build: `./gradlew clean build`
- Check (includes lint): `./gradlew check`
- Android lint: `./gradlew lint`
- Run tests: `./gradlew test`
- ktlint check: `./gradlew ktlintCheck`
- ktlint format: `./gradlew ktlintFormat`
- Build ios: `cd /Users/kevingalligan/devel/DroidconKotlin/ios/Droidcon && xcodebuild -scheme Droidcon -sdk iphonesimulator`

## Modules

- android: The Android app
- ios: The iOS app
- shared: Shared logic code
- shared-ui: UI implemented with Compose Multiplatform and used by both Android and iOS

## Libraries

- Hyperdrive: KMP-focused architecture library. It is open source but rarely used by other apps. See docs/HyperDrivev1.md

## Code Style
- Kotlin Multiplatform project (Android/iOS)
- Use ktlint for formatting (version 1.4.0)
- Follow dependency injection pattern with Koin
- Repository pattern for data access
- Compose UI for shared UI components
- Class/function names: PascalCase for classes, camelCase for functions
- Interface implementations: Prefix with `Default` (e.g., `DefaultRepository`)
- Organize imports by package, no wildcard imports
- Type-safe code with explicit type declarations
- Coroutines for asynchronous operations
- Proper error handling with try/catch blocks

## Claude Document Formats and Instructions
See APISummaryFormat.md and StructuredInstructionFormats.md

## Architecture Notes
- App startup logic is handled in `co.touchlab.droidcon.viewmodel.ApplicationViewModel`

## Current Task

Cleaning up the app and prepping for release