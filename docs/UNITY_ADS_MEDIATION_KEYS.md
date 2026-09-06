# Unity Ads Monetization & Mediation Credentials

تم حفظ المعرفات والبيانات الخاصة بـ Unity Ads لاستخدامها عند دمج وساطة الإعلانات (Unity Ads Mediation / AdMob Mediation).

## 📌 المعرفات الخاصة بالمشروع (AdWatchApp)

- **اسم المشروع في Unity:** `AdWatchApp`
- **معرف المؤسسة (Organization Core ID):** `11270420492778`
- **معرف اللعبة/التطبيق لنظام Android (Game ID - Android):** `6185715`
- **معرف اللعبة/التطبيق لنظام iOS (Game ID - iOS):** `6185714`
- **Monetization Stats API Key:** `892d081555897c1d8e37ad7728270720f9fe5ea2c566da734b9afa10006011eb`
- **رابط المشروع على Unity Dashboard:** `https://cloud.unity.com/home/organizations/11270420492778/projects/698134c8-18f6-4c0c-86fb-e9af7d1fee49/monetization/about`

---

## 🎯 مواقع ووحدات الإعلانات (Placements / Ad Units)

| النوع (Ad Format) | المنصة (Platform) | اسم الوحدة (Placement Name) | معرف الوحدة (Placement ID) |
| :--- | :--- | :--- | :--- |
| **Interstitial** | Android | Interstitial Android | `Interstitial_Android` |
| **Interstitial** | iOS | Interstitial iOS | `Interstitial_iOS` |
| **Rewarded** | Android | Rewarded Android | `Rewarded_Android` |
| **Rewarded** | iOS | Rewarded iOS | `Rewarded_iOS` |
| **Banner** | Android | Banner Android | `Banner_Android` |
| **Banner** | iOS | Banner iOS | `Banner_iOS` |

---

## 📝 خطوات الدمج المستقبلي (Next Steps for Mediation Integration)

1. **في AdMob Dashboard:**
   - الانتقال إلى **Mediation** ➔ **Waterfall Groups**.
   - إضافة **Unity Ads** كمصدر إعلانات (Ad Source).
   - إدخال الـ `Organization Core ID` (`11270420492778`) والـ `Game ID` الخاص بالمنصة (`6185715` للاندرويد، `6185714` للايفون).
   - ربط وحدات الإعلانات (Placement IDs) الموضحة بالجدول أعلاه مع كل نوع إعلان متطابق في AdMob.

2. **في تطبيق Flutter:**
   - إضافة حزمة `google_mobile_ads_unity_ads` أو المحول المناسب (Adapter) عند تفعيل الوساطة المباشرة.
