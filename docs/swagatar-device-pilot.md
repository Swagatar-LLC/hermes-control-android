# Swagatar Android device pilot

The Swagatar fork is a separate app lineage from `Swagatar-LLC/hermes-mobile` (the existing iOS fork). Source: `Hy4ri/hermes-mobile`; changes enter through reviewed PRs. Do not install an upstream APK and call it a Swagatar build.

## Gates before connecting a real gateway

1. Review the exact fork commit and its upstream diff. Require the PR rigor-spine and security sections, an independent approval, Android CI, policy regression tests, dependency review, and CodeQL. A CI run is not an on-device test.
2. Release builds must reject HTTP/WS, including a migrated legacy connection. Use a verified HTTPS/WSS dashboard endpoint on the private network. Tailscale's private addressing alone does not make an HTTP LAN endpoint safe. Keep credentials out of debug builds: the upstream debug keystore is committed and shared.
3. The in-app updater checks this fork's GitHub releases, not upstream's differently signed APKs. Main-branch artifacts are not GitHub releases and are installed manually after verification. Stable public release publishing remains a separate, manual gate.
4. Disable or redact private notification previews, verify WebSocket URL logs omit both token and ticket, and exercise approvals against the actual gateway before treating the app as a daily driver. A desktop or emulator test alone does not prove the phone's lock-screen behavior.

**Known parity cost:** upstream supports an HTTP dashboard over its SSH socket tunnel. This fork's release policy rejects that URL before network access, so the SSH-tunnel feature is not release-compatible yet. Do not claim full upstream parity or use that connection mode on a real device until a narrowly scoped, tested tunnel exception exists.

## Build prerequisites and verification

The pinned project requires Java 21, Android SDK Platform 37, Build Tools 37.0.0, and Gradle 9.8.2 through its checked wrapper. On Jeff's Mac at first inspection, Java 23 and an SDK/adb were present, but Java 21, Platform/Build Tools 37, and a connected Android device were not confirmed available. Obtain approval before downloading project dependencies or SDK components; never run unreviewed Gradle tasks just to inspect a repository.

For an approved fork commit and provisioned tools, run the same tasks as CI (`./gradlew testDebugUnitTest lintDebug assembleDebug`), then verify the APK package, version, signer and declared network policy with SDK tools (`aapt`/`aapt2`, `apksigner`). The debug application ID is `com.m57.hermescontrol.dev`; release is `com.m57.hermescontrol`. Debug is for isolated, disposable testing only.

On every successful `main` run, the CI Summary gate precedes a separately signed release-variant build. Download the `hermes-control-android-main-<source SHA>-<run ID>-<attempt>` artifact from that run. Check `SHA256SUMS` against the APK and `version.txt`, compare `sourceSha` to the merged commit, and verify its signer, package, version name/code with `apksigner` and `aapt`. The private signing key is restricted to the `android-main-signing` GitHub environment on protected branches; the owner's recovery copy is stored outside Git. A green PR build is not a signed main artifact.

`VERSION` holds the reviewed SemVer `MAJOR.MINOR.PATCH` base. CI gives each main run a numeric `-dev.<run number>` prerelease and uses 100 × that run number as Android's monotonically increasing versionCode; reruns retain their number. Bump the base under PR review for breaking/feature/fix releases according to SemVer before publishing a stable tag.

## Stable release gate

Only a stable `vMAJOR.MINOR.PATCH` tag matching `VERSION` is supported; RC tags are deliberately rejected until their upgrade path has tests. After the tagged commit's **signed main run succeeds**, the manual release workflow must be dispatched from `main` with that tag as input. It refuses a tag pointing anywhere but the exact current main commit. The release code is that main run's code + 99, so it upgrades the preview and the next main run has a higher Android code. CI blocks the next PR/merge while `VERSION` is equal to or older than the latest published stable release; bump it to the next SemVer base before merging so no `-dev` build appears to downgrade from stable. Do not publish or install a stable release until its APK, attestation, signer and in-place upgrade have been checked against a real device.

Before installing, inspect `adb devices -l`, the device Android version, and whether either application ID is already installed. If an upstream app with `com.m57.hermescontrol` is installed, its different signer cannot be updated in place; back up its data, then explicitly approve uninstall/reinstall rather than bypass signature enforcement. Ask Jeff to enable developer options/USB debugging, unlock the device, and accept its authorization prompt. Do not attempt to bypass a locked device. With an approved APK and the explicit device serial, use `adb -s <serial> install <verified.apk>`, then read back the package and launch result; visually inspect sign-in, TLS failure behavior, session reconnect, notification preview, and approval identity. Keep the actual gateway credentials out of logs and screenshots.

## Evidence levels

Source review < tests/lint < built APK and verified signer < installed package < exercised live gateway behavior. The signing identity is provisioned, but a signed main APK and on-device behavior remain unverified until this change lands and its first `main` run succeeds.
