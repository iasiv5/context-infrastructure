# iOS Test Acceleration

Use this skill when iterating on iOS unit tests, XCTest UI tests, or Xcode build/test failures in your iOS project.

## Core Rule

Build and test sequentially. Do not run parallel `xcodebuild` jobs against the same project or DerivedData because Xcode can fail with `build.db: database is locked`.

## Fast Loop

Prefer one build followed by repeated `test-without-building` runs:

```bash
xcodebuild build-for-testing -scheme <your-scheme> -destination 'id=<simulator-uuid>'
xcodebuild test-without-building -scheme <your-scheme> -destination 'id=<simulator-uuid>' -only-testing:<bundle>/<suite>/<test>
```

Use a fixed simulator UUID when available so build cache and test results stay stable across runs:

```text
<simulator-uuid>
```

## Targeted Runs

Run the smallest stable target first:

```bash
xcodebuild test-without-building -scheme <your-scheme> -destination 'id=<simulator-uuid>' -only-testing:<YourApp>Tests/HostProfileTests
```

For a single UI test:

```bash
xcodebuild test-without-building -scheme <your-scheme> -destination 'id=<simulator-uuid>' -only-testing:<YourApp>UITests/<YourApp>UITests/testImportSSHTunnelHostProfileFlow
```

For a focused group, pass multiple `-only-testing:` flags in one command.

## UI Test Stability

Anchor UI tests on app-owned accessibility identifiers, not system menus, paste popovers, coordinates, or SwiftUI text layout details.

Prefer launch arguments for deterministic fixtures:

```swift
app.launchArguments = ["UITEST_HOST_PROFILES_FIXTURE", "UITEST_HOST_IMPORT_JSON_PREFILL"]
```

Use these for data prefill instead of `UIPasteboard` or system Paste menus. System UI adds timing and permission noise that obscures product regressions.

## Failure Inspection

When `xcodebuild` only says `TEST EXECUTE FAILED`, inspect the `.xcresult` path printed near the end:

```bash
xcrun xcresulttool get test-results tests --path "<path>.xcresult"
```

This usually gives the failing test and source line faster than reading the full build log.

## Escalation Order

1. Run the single failing test with `test-without-building`.
2. If source changed, run `build-for-testing` once, then retry the single test.
3. Run the focused suite that covers the feature.
4. Run full `xcodebuild test` only after focused tests pass.

## Cleanup Notes

Xcode may create simulator clones such as `Clone 1 of iPhone 16`. Treat clone names as normal unless the runner fails before test code starts. If runner launch fails but the test also reports a normal assertion failure, inspect the assertion first.