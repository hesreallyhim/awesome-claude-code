# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Pareto Security Development Guide

## Build & Test Commands
- Build: `make build`
- Run tests: `make test`
- Run single test: `NSUnbufferedIO=YES xcodebuild -project "Pareto Security.xcodeproj" -scheme "Pareto Security" -test-timeouts-enabled NO -only-testing:ParetoSecurityTests/TestClassName/testMethodName -destination platform=macOS test`
- Format: `make fmt` or `mint run swiftformat --swiftversion 5 .`
- Archive builds: `make archive-debug`, `make archive-release`, `make archive-debug-setapp`, `make archive-release-setapp`
- Create DMG: `make dmg`
- Create PKG: `make pkg`

## Application Architecture

### Core Components
- **Main App (`/Pareto/`)**: SwiftUI-based status bar application
- **Helper Tool (`/ParetoSecurityHelper/`)**: XPC service for privileged operations requiring admin access
- **Security Checks (`/Pareto/Checks/`)**: Modular security check system organized by category

### Security Checks System
The app uses a modular check architecture with these categories:
- **Access Security**: Autologin, password policies, SSH keys, screensaver
- **System Integrity**: FileVault, Gatekeeper, Boot security, Time Machine
- **Firewall & Sharing**: Firewall settings, file sharing, remote access
- **macOS Updates**: System updates, automatic updates
- **Application Updates**: Third-party app update checks

Key files:
- `ParetoCheck.swift` - Base class for all security checks
- `Checks.swift` - Central registry organizing checks into claims
- `Claim.swift` - Groups related checks together

### XPC Helper Tool
The `ParetoSecurityHelper` is a privileged helper tool that:
- Handles firewall configuration checks
- Performs system-level operations requiring admin privileges
- Communicates with the main app via XPC

### Distribution Targets
- **Direct distribution**: Standard macOS app with auto-updater
- **SetApp**: Subscription service integration with separate build target
- **Team/Enterprise**: JWT-based licensing for organization management

## Code Style
- **Imports**: Group imports alphabetically, Foundation/SwiftUI first, then third-party libraries
- **Naming**: Use camelCase for variables/functions, PascalCase for types; be descriptive
- **Error Handling**: Use Swift's do/catch with specific error enums
- **Types**: Prefer explicit typing, especially for collections
- **Formatting**: Max line length 120 chars, use Swift's standard indentation (4 spaces)
- **Comments**: Only add comments for complex logic; include header comment for files
- **Code Organization**: Group related functionality with MARK comments
- **Testing**: All new features should include tests
- **Logging**: Use `os_log` for logging, with appropriate log levels

This project uses SwiftFormat for auto-formatting.

## Key Dependencies
- **Defaults**: User preferences management
- **LaunchAtLogin**: Auto-launch functionality
- **Alamofire**: HTTP networking for update checks
- **JWTDecode**: Team licensing authentication
- **Cache**: Response caching layer

## URL Scheme Support
The app supports custom URL scheme `paretosecurity://` for:
- `reset` - Reset to default settings
- `showMenu` - Open status bar menu
- `update` - Force update check (not available in SetApp build)
- `welcome` - Show welcome window
- `runChecks` - Trigger security checks
- `debug` - Output detailed check status (supports `?check=<checkname>` parameter)
- `logs` - Copy system logs
- `showPrefs` - Show preferences window
- `showBeta` - Enable beta channel
- `enrollTeam` - Enroll device to team (not available in SetApp build)

## Testing Strategy
- Unit tests in `ParetoSecurityTests/` cover core functionality
- UI tests in `ParetoSecurityUITests/` test user flows
- Tests are organized by feature area (checks, settings, team, updater, welcome)
- Use `make test` for full test suite with formatted output via xcbeautify

## Development Notes
- The app runs as a status bar utility (`LSUIElement: true`)
- Requires Apple Events permission for system automation
- No sandboxing to allow system security checks
- Uses privileged helper tool for admin operations
- Supports both individual and team/enterprise deployments

# Pareto Security App Structure

## Overview
Pareto Security is a macOS security monitoring app built with SwiftUI. It performs various security checks and uses a privileged helper tool for system-level operations on macOS 15+.

## Core Architecture

### Security Checks System
- **Base Class**: `ParetoCheck` (`/Pareto/Checks/ParetoCheck.swift`)
  - All security checks inherit from this base class
  - Key properties: `requiresHelper`, `isRunnable`, `isActive`
  - `menu()` method handles UI display including question mark icons for helper-dependent checks
  - `infoURL` redirects to helper docs when helper authorization missing

- **Check Categories**:
  - Firewall checks: `/Pareto/Checks/Firewall and Sharing/`
  - System checks: `/Pareto/Checks/System/`
  - Application checks: `/Pareto/Checks/Applications/`

### Helper Tool System (macOS 15+ Firewall Checks)
- **Helper Tool**: `/ParetoSecurityHelper/main.swift`
  - XPC service for privileged operations
  - Static version: `helperToolVersion = "1.0.3"`
  - Implements `ParetoSecurityHelperProtocol`
  - Functions: `isFirewallEnabled()`, `isFirewallStealthEnabled()`, `getVersion()`

- **Helper Management**: `/Pareto/Extensions/HelperTool.swift`
  - `HelperToolUtilities`: Static utility methods (non-actor-isolated)
  - `HelperToolManager`: Main actor class for XPC communication
  - Expected version: `expectedHelperVersion = "1.0.3"`
  - Auto-update logic: `ensureHelperIsUpToDate()`

- **Helper Configuration**: `/ParetoSecurityHelper/co.niteo.ParetoSecurityHelper.plist`
  - System daemon configuration
  - Critical: `BundleProgram` must be `Contents/MacOS/ParetoSecurityHelper`

### UI Structure

#### Main Views
- **Welcome Screen**: `/Pareto/Views/Welcome/PermissionsView.swift`
  - Permissions checker with continuous monitoring
  - Firewall permission section (macOS 15+ only)
  - Window size: 450×500

- **Settings**: `/Pareto/Views/Settings/`
  - `AboutSettingsView.swift`: Shows app + helper versions
  - `PermissionsSettingsView.swift`: Continuous permission monitoring
  - Various other settings views

#### Permission System
- **PermissionsChecker**: Continuous monitoring with 2-second timer
- **Properties**: `firewallAuthorized`, other permissions
- **UI States**: Authorized/Disabled buttons, consistent spacing (20pt)

### Key Technical Concepts

#### XPC Communication
- **Service Name**: `co.niteo.ParetoSecurityHelper`
- **Protocol**: `ParetoSecurityHelperProtocol`
- **Connection Management**: Automatic retry, timeout handling
- **Error Handling**: Comprehensive logging, graceful degradation

#### Concurrency & Threading
- **Main Actor**: UI components, HelperToolManager
- **Actor Isolation**: HelperToolUtilities for non-isolated static methods
- **Async/Await**: Proper continuation handling, avoid semaphores in async contexts
- **Thread Safety**: NSLock for XPC continuation management

#### Version Management
- **Manual Versioning**: Static constants for helper versions
- **Update Logic**: Compare current vs expected, auto-reinstall if outdated
- **Version Display**: About screen shows both app and helper versions

## Important Implementation Details

### Helper Tool Requirements
- **macOS 15+ Only**: Firewall checks require helper on macOS 15+
- **Authorization**: User must approve in System Settings > Login Items
- **Question Mark UI**: Shows when helper required but not authorized
- **Live Status Checks**: Always use `HelperToolUtilities.isHelperInstalled()`, never cached values

### Common Patterns
- **Check Implementation**: Override `requiresHelper` and `isRunnable` in check classes
- **Permission Monitoring**: Use Timer with 2-second intervals for continuous checking
- **Error Handling**: Use `os_log` for logging, specific error enums for Swift errors
- **UI Consistency**: 20pt spacing, medium font weight, secondary colors for labels

### Troubleshooting Tools
- **Helper Status**: `launchctl print system/co.niteo.ParetoSecurityHelper`
- **Helper Logs**: Check system logs for "Helper:" prefixed messages
- **XPC Debugging**: Comprehensive logging throughout XPC chain
- **Version Mismatches**: Check both static constants match when updating

## File Locations Reference

### Core Files
- **Base Check**: `/Pareto/Checks/ParetoCheck.swift`
- **Firewall Check**: `/Pareto/Checks/Firewall and Sharing/Firewall.swift`
- **Helper Tool**: `/ParetoSecurityHelper/main.swift`
- **Helper Manager**: `/Pareto/Extensions/HelperTool.swift`

### UI Files
- **Welcome**: `/Pareto/Views/Welcome/PermissionsView.swift`
- **About**: `/Pareto/Views/Settings/AboutSettingsView.swift`
- **Permissions Settings**: `/Pareto/Views/Settings/PermissionsSettingsView.swift`

### Configuration
- **Helper Plist**: `/ParetoSecurityHelper/co.niteo.ParetoSecurityHelper.plist`
- **Build Config**: Use `make build`, `make test`, `make lint`, `make fmt`

## Version Update Procedure
1. Increment `HelperToolUtilities.expectedHelperVersion` in HelperTool.swift
2. Increment `helperToolVersion` in helper's main.swift
3. Both versions must match for proper operation
4. App will auto-detect and reinstall helper on next check
