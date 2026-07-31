import java.util.Properties
import org.gradle.api.GradleException

plugins {
    id("com.android.application")
    id("dev.flutter.flutter-gradle-plugin")
}

val keystorePropertiesFile = rootProject.file("key.properties")
val googleServicesFile = file("google-services.json")
if (googleServicesFile.exists()) {
    apply(plugin = "com.google.gms.google-services")
}

val keystoreProperties = Properties()
val releaseSigningConfigured = keystorePropertiesFile.exists().also { exists ->
    if (exists) {
        keystorePropertiesFile.inputStream().use(keystoreProperties::load)
    }
}
val allowCiPreviewSigning =
    providers.environmentVariable("SAHMI_ALLOW_CI_PREVIEW_SIGNING").orNull == "true" ||
        providers.environmentVariable("GITHUB_ACTIONS").orNull == "true"
val productionBuild =
    providers.environmentVariable("SAHMI_PRODUCTION_BUILD").orNull == "true"
val admobAndroidAppId =
    providers.environmentVariable("ADMOB_ANDROID_APP_ID").orNull
        ?: "ca-app-pub-3940256099942544~3347511713"

if (productionBuild) {
    if (!releaseSigningConfigured) {
        throw GradleException("Production Android builds require the protected release signing key.")
    }
    if (!googleServicesFile.exists()) {
        throw GradleException("Production Android builds require google-services.json.")
    }
    if (admobAndroidAppId.contains("3940256099942544")) {
        throw GradleException("Production Android builds must not use the Google AdMob test app ID.")
    }
}

android {
    namespace = "com.sahmikasban.sahmi_kasban_mobile"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    defaultConfig {
        applicationId = "com.sahmikasban.sahmi_kasban_mobile"
        minSdk = 24
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName
        manifestPlaceholders["admobAppId"] = admobAndroidAppId
    }

    signingConfigs {
        if (releaseSigningConfigured) {
            create("release") {
                keyAlias = keystoreProperties.getProperty("keyAlias")
                keyPassword = keystoreProperties.getProperty("keyPassword")
                storeFile = file(keystoreProperties.getProperty("storeFile"))
                storePassword = keystoreProperties.getProperty("storePassword")
            }
        }
    }

    buildTypes {
        release {
            when {
                releaseSigningConfigured -> {
                    signingConfig = signingConfigs.getByName("release")
                }
                allowCiPreviewSigning -> {
                    // CI previews are deliberately a different Android package. They can be
                    // installed beside the real app but can never be mistaken for an update.
                    signingConfig = signingConfigs.getByName("debug")
                    applicationIdSuffix = ".ci"
                    versionNameSuffix = "-ci"
                }
                else -> {
                    throw GradleException(
                        "Release signing is not configured. Use Signed Android Release, or set " +
                            "SAHMI_ALLOW_CI_PREVIEW_SIGNING=true for a separate .ci preview package.",
                    )
                }
            }
        }
    }
}

kotlin {
    compilerOptions {
        jvmTarget = org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17
    }
}

flutter {
    source = "../.."
}
