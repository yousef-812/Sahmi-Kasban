# Android signing and update compatibility

Android only installs an APK as an update when the package name and signing certificate both match the installed application. Previous staging artifacts were signed with runner-generated debug certificates, so a later artifact could conflict with the installed package.

## One-time production/staging key setup

Generate one upload key on a trusted computer and keep the original JKS in an offline backup:

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

Run the **Signed Android Release** workflow. It validates the JKS, builds the APK, records its SHA-256 signing certificate, uploads the APK, and removes the key from the runner.

## Migration from old staging APKs

The first stable-key APK cannot update an APK signed by an old debug certificate. Uninstall the old app once, install the first artifact from **Signed Android Release**, and then all later artifacts from that workflow will update normally as long as the same key is retained.

Never commit the JKS, `key.properties`, passwords, or Base64 key to Git. Losing the key prevents direct updates to installations signed with it.

The warning shown when sideloading an APK can still appear because it was installed outside Google Play. Closed/Internal Testing through Google Play is the normal way to remove sideloading warnings and establish Play Protect trust.
