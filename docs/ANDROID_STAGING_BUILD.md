# Android staging build

The staging APK connects to `https://sahmi-kasban.fly.dev` with demo mode disabled.

## Startup stability

The Android application does not schedule WorkManager jobs. A transitive dependency registers `androidx.work.WorkManagerInitializer` through AndroidX Startup. On affected devices, eager initialization attempted to create `WorkDatabase` before Flutter reached `main()` and terminated the process.

The application manifest removes only the WorkManager initializer metadata while retaining AndroidX Startup for other libraries. Optional Firebase and Google Mobile Ads initialization is also isolated from Flutter startup, encrypted session reads recover safely, and Android backup is disabled for local encrypted state.

## Clean installation

Uninstall any older build with the same package name before installing this APK so stale application databases and restored encrypted state are removed.
