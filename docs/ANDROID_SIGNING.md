# Android signing and update compatibility

Android only installs an APK as an update when all three values are compatible:

- the package name is unchanged;
- the signing certificate is the same certificate used by the installed app;
- the new APK has a higher version code.

## Two intentionally different APK types

### Signed update APK

Only artifacts produced by **Signed Android Release** use the real package ID:

`com.sahmikasban.sahmi_kasban_mobile`

Their artifact name starts with:

`sahmi-kasban-signed-update-`

The workflow validates the package ID, records the version code and certificate SHA-256 fingerprint, and uploads `release-metadata.txt` beside the APK. This is the only APK type that should be sent to users as an update.

### CI preview APK

Ordinary pull-request and repository checks do not have access to the protected release key. Their APK now uses the separate package ID:

`com.sahmikasban.sahmi_kasban_mobile.ci`

Its artifact and file names contain `ci-preview-not-an-update`. It can be installed beside the real app for testing, but it cannot replace or update the real app. Older artifacts named `sahmi-kasban-staging-apk-*` were runner-debug-signed previews and must not be distributed as updates.

## One-time stable key setup

Generate one upload key on a trusted computer and keep the original JKS in at least one offline backup:

```powershell
keytool -genkeypair -v `
  -keystore sahmi-kasban-upload.jks `
  -alias sahmi-kasban `
  -keyalg RSA -keysize 4096 -validity 10000
```

Convert it to a single-line Base64 value:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("sahmi-kasban-upload.jks")) |
  Set-Clipboard
```

Add these GitHub Actions secrets:

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

`ANDROID_EXPECTED_CERT_SHA256` is optional but recommended after the first successful stable build. Copy the fingerprint from `release-metadata.txt`; later builds will fail if someone replaces the signing key accidentally.

Run **Signed Android Release**. It validates the JKS, builds the APK, confirms the original package ID, records its SHA-256 signing certificate, uploads a versioned APK, and removes protected files from the runner.

## Existing installations

A certificate mismatch cannot be repaired by changing the version number or package manifest. When the currently installed copy was signed by an old runner-generated debug certificate, it must be uninstalled once before the first stable-key APK is installed. Application data stored only on the device may be removed, but server accounts, wallet balances, reports, and subscriptions remain on the server.

After that one-time transition, every APK from **Signed Android Release** updates normally as long as the exact same JKS and alias remain in GitHub Secrets.

Never commit the JKS, `key.properties`, passwords, or Base64 key to Git. Losing the private key prevents direct updates to installations signed with it.

The warning shown when sideloading an APK can still appear because it was installed outside Google Play. Closed or Internal Testing through Google Play is the normal distribution route for Play Protect trust and managed updates.
