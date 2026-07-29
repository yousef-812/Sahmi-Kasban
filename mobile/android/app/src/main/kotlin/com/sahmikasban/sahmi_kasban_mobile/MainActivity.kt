package com.sahmikasban.sahmi_kasban_mobile

import android.content.ContentValues
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File

class MainActivity : FlutterActivity() {
    private val downloadsChannel = "sahmi_kasban/downloads"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            downloadsChannel,
        ).setMethodCallHandler { call, result ->
            if (call.method != "saveCsv") {
                result.notImplemented()
                return@setMethodCallHandler
            }
            val requestedName = call.argument<String>("filename") ?: "sahmi-engine-replay.csv"
            val bytes = call.argument<ByteArray>("bytes")
            if (bytes == null || bytes.isEmpty()) {
                result.error("EMPTY_FILE", "CSV payload is empty", null)
                return@setMethodCallHandler
            }
            try {
                result.success(saveCsv(requestedName, bytes))
            } catch (error: Exception) {
                result.error("SAVE_FAILED", error.message, null)
            }
        }
    }

    private fun saveCsv(requestedName: String, bytes: ByteArray): String {
        val safeName = requestedName
            .replace(Regex("[^A-Za-z0-9._-]"), "-")
            .let { if (it.endsWith(".csv", ignoreCase = true)) it else "$it.csv" }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, safeName)
                put(MediaStore.Downloads.MIME_TYPE, "text/csv")
                put(
                    MediaStore.Downloads.RELATIVE_PATH,
                    Environment.DIRECTORY_DOWNLOADS + "/SahmiKasban",
                )
                put(MediaStore.Downloads.IS_PENDING, 1)
            }
            val resolver = contentResolver
            val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                ?: error("Could not create a Downloads file")
            try {
                resolver.openOutputStream(uri)?.use { stream ->
                    stream.write(bytes)
                    stream.flush()
                } ?: error("Could not open the Downloads file")
                values.clear()
                values.put(MediaStore.Downloads.IS_PENDING, 0)
                resolver.update(uri, values, null, null)
                return uri.toString()
            } catch (error: Exception) {
                resolver.delete(uri, null, null)
                throw error
            }
        }

        val directory = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
            ?: filesDir
        val file = File(directory, safeName)
        file.writeBytes(bytes)
        return file.absolutePath
    }
}
