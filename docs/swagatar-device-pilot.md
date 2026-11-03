# Swagatar Android device pilot

The Swagatar fork is a separate app lineage from `Swagatar-LLC/hermes-mobile` (the existing iOS fork). Source: `Hy4ri/hermes-mobile`; changes enter through reviewed PRs. Do not install an upstream APK and call it a Swagatar build.

## Gates before connecting a real gateway

1. Review the exact fork commit and its upstream diff. Require the PR rigor-spine and security sections, an independent approval, Android CI, policy regression tests, dependency review, and CodeQL. A CI run is not an on-device test.
2. Release builds must reject HTTP/WS, including a migrated legacy connection. Use a verified HTTPS/WSS dashboard endpoint on the private network. Tailscale's private addressing alone does not make an HTTP LAN endpoint safe. Keep credentials out of debug builds: the upstream debug keystore is committed and shared.
3. The upstream in-app updater still points to upstream GitHub releases; do not accept its update prompt for a Swagatar installation. Fork-owned release verification and a signing identity are separate follow-up work. Do not tag or publish a release until its workflow checks the reviewed source SHA and the independently trusted fork signing certificate.
4. Disable or redact private notification previews, verify WebSocket URL logs omit both token and ticket, and exercise approvals against the actual gateway before treating the app as a daily driver. A desktop or emulator test alone does not prove the phone's lock-screen behavior.

**Known parity cost:** upstream supports an HTTP dashboard over its SSH socket tunnel. This fork's release policy rejects that URL before network access, so the SSH-tunnel feature is not release-compatible yet. Do not claim full upstream parity or use that connection mode on a real device until a narrowly scoped, tested tunnel exception exists.

## Build prerequisites and verification

The pinned project requires Java 21, Android SDK Platform 37, Build Tools 37.0.0, and Gradle 9.8.2 through its checked wrapper. On Jeff's Mac at first inspection, Java 23 and an SDK/adb were present, but Java 21, Platform/Build Tools 37, and a connected Android device were not confirmed available. Obtain approval before downloading project dependencies or SDK components; never run unreviewed Gradle tasks just to inspect a repository.

For an approved fork commit and provisioned tools, run the same tasks as CI (`./gradlew testDebugUnitTest lintDebug assembleDebug`), then verify the APK package, version, signer and declared network policy with SDK tools (`aapt`/`aapt2`, `apksigner`). The debug application ID is `com.m57.hermescontrol.dev`; release is `com.m57.hermescontrol`. Debug is for isolated, disposable testing only. A signed fork release needs a private keystore and the `RELEASE_CERTIFICATE_SHA256` repository variable; never reuse upstream's signer digest as our identity or store a signing key in Git.

Before installing, inspect `adb devices -l`, the device Android version, and whether either application ID is already installed. If it is installed, compare signatures and decide whether to update in place or preserve its data before installing a differently signed app. Ask Jeff to enable developer options/USB debugging, unlock the device, and accept its authorization prompt. Do not attempt to bypass a locked device. With an approved APK and the explicit device serial, use `adb -s <serial> install <verified.apk>`, then read back the package and launch result; visually inspect sign-in, TLS failure behavior, session reconnect, notification preview, and approval identity. Keep the actual gateway credentials out of logs and screenshots.

## Evidence levels

Source review < tests/lint < built APK and verified signer < installed package < exercised live gateway behavior. This pilot has only reached the source-review and offline policy-test levels; signing and device behavior remain unknown.
