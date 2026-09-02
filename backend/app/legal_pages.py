# ruff: noqa: E501
from __future__ import annotations

import html

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

from app.core.config import get_settings

router = APIRouter(include_in_schema=False)
_UPDATED_AT = "28 يوليو 2026"
_APP_ADS_TXT_CONTENT = "google.com, pub-4624889874966809, DIRECT, f08c47fec0942fa0\n"

_STYLE = """
:root{color-scheme:light;--green:#176f54;--deep:#173c30;--gold:#bd8b2f;--bg:#f4f7f5;--card:#fff;--muted:#60736b;--line:#dce9e3;--danger:#a93838}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--deep);font-family:Tahoma,Arial,sans-serif;line-height:1.9}
a{color:var(--green)}header{background:linear-gradient(135deg,#125c46,#1b8061);color:#fff;padding:34px 18px;text-align:center}
header h1{margin:0;font-size:30px}header p{margin:6px 0 0;opacity:.9}.wrap{max-width:920px;margin:auto;padding:24px 16px 48px}
nav{display:flex;flex-wrap:wrap;gap:9px;margin:0 0 20px}nav a{background:#fff;border:1px solid var(--line);padding:7px 12px;border-radius:999px;text-decoration:none;font-weight:700}
.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:22px;margin:0 0 16px;box-shadow:0 8px 30px rgba(20,76,57,.06)}
h2{font-size:21px;margin:0 0 8px}h3{font-size:17px;margin:18px 0 6px}p,li{color:#344e45}.muted{color:var(--muted);font-size:14px}.warning{border-right:5px solid var(--gold)}
table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}
label{display:block;font-weight:700;margin-top:12px}input{width:100%;padding:13px;border:1px solid #b9d0c7;border-radius:12px;font:inherit;direction:ltr}
button{margin-top:18px;border:0;border-radius:12px;padding:13px 20px;background:var(--danger);color:#fff;font:inherit;font-weight:800;cursor:pointer}
#result{margin-top:14px;font-weight:700}.ok{color:#16704d}.error{color:var(--danger)}footer{text-align:center;color:var(--muted);font-size:13px;padding:22px}
"""


def _navigation() -> str:
    return """
<nav aria-label="الصفحات القانونية">
  <a href="/legal">الصفحات القانونية</a>
  <a href="/privacy">سياسة الخصوصية</a>
  <a href="/terms">شروط الاستخدام</a>
  <a href="/financial-disclaimer">إخلاء المسؤولية المالية</a>
  <a href="/data-safety">سلامة البيانات</a>
  <a href="/financial-features">الإقرار بالميزات المالية</a>
  <a href="/delete-account">حذف الحساب</a>
  <a href="/app-ads.txt">app-ads.txt</a>
</nav>
"""


def _page(title: str, intro: str, body: str) -> HTMLResponse:
    settings = get_settings()
    support_email = html.escape(settings.smtp_from_email)
    document = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} — سهمي كسبان</title><style>{_STYLE}</style></head>
<body>
<header><h1>سهمي كسبان</h1><p>{html.escape(title)}</p></header>
<main class="wrap">{_navigation()}<section class="card"><h2>{html.escape(title)}</h2><p>{html.escape(intro)}</p><p class="muted">آخر تحديث: {_UPDATED_AT}</p></section>{body}
<section class="card"><h2>التواصل</h2><p>للاستفسارات المتعلقة بالخصوصية أو الحساب أو هذه الشروط: <a href="mailto:{support_email}">{support_email}</a>.</p></section>
</main><footer>سهمي كسبان — معلومات وتحليلات آلية وليست توصية استثمارية.</footer>
</body></html>"""
    return HTMLResponse(document)


@router.get("/legal", response_class=HTMLResponse)
def legal_index() -> HTMLResponse:
    return _page(
        "الصفحات القانونية",
        "هذه الصفحة تجمع الروابط القانونية وسياسات البيانات الخاصة بالتطبيق.",
        """
<section class="card"><h2>روابط النشر على Google Play و AdMob</h2><ul>
<li>سياسة الخصوصية: <code>/privacy</code></li>
<li>شروط الاستخدام: <code>/terms</code></li>
<li>إخلاء المسؤولية المالية: <code>/financial-disclaimer</code></li>
<li>سلامة البيانات: <code>/data-safety</code></li>
<li>الإقرار بالميزات المالية: <code>/financial-features</code></li>
<li>حذف الحساب والبيانات: <code>/delete-account</code></li>
<li>ملف إعلانات التطبيقات (app-ads.txt): <code>/app-ads.txt</code></li>
</ul></section>
""",
    )


@router.get("/app-ads.txt", response_class=PlainTextResponse)
def app_ads_txt() -> PlainTextResponse:
    return PlainTextResponse(_APP_ADS_TXT_CONTENT)


@router.get("/privacy", response_class=HTMLResponse)
def privacy_policy() -> HTMLResponse:
    return _page(
        "سياسة الخصوصية",
        "توضح هذه السياسة البيانات التي يجمعها تطبيق سهمي كسبان وكيف نستخدمها ونحميها ونتعامل مع طلبات الحذف.",
        """
<section class="card"><h2>البيانات التي نعالجها</h2><ul>
<li><strong>بيانات الحساب:</strong> البريد الإلكتروني، الاسم الظاهر، الصورة الرمزية، حالة التحقق والحساب.</li>
<li><strong>بيانات الاستخدام:</strong> تحليلات الأسهم التي يطلبها المستخدم، التقارير المفتوحة، قائمة المعاملات والرصيد، وإعدادات التطبيق.</li>
<li><strong>المحتوى الذي ينشئه المستخدم:</strong> المناقشات والتوقعات والبلاغات والاستئنافات وإجراءات الإشراف.</li>
<li><strong>بيانات الشراء والإعلانات:</strong> معرف المنتج، حالة الشراء أو الاشتراك، سجل المكافآت، ومعرفات التحقق. لا نخزن رقم البطاقة البنكية.</li>
<li><strong>بيانات الجهاز والتشغيل:</strong> رمز الإشعارات المشفر، معرفه المجزأ، سجلات الأخطاء والتشخيص والأداء وعنوان الشبكة ضمن سجلات الحماية والتشغيل.</li>
</ul></section>
<section class="card"><h2>أغراض الاستخدام</h2><ul>
<li>إنشاء الحساب وتأمينه واستعادته وتقديم وظائف التطبيق.</li><li>تنفيذ المحفظة والاشتراكات والتحليلات والتقارير ومنع الخصم المكرر.</li>
<li>مراجعة محتوى المجتمع ومنع الاحتيال والإساءة والرسائل المزعجة.</li><li>إرسال الإشعارات ورسائل التحقق والدعم.</li>
<li>تشخيص الأعطال، قياس الجودة، حماية الخدمة والالتزام بالمتطلبات القانونية.</li></ul></section>
<section class="card"><h2>مزودو الخدمة</h2><p>قد تعالج البيانات، بالقدر اللازم لتقديم الخدمة، جهات استضافة وقاعدة بيانات وبريد وإشعارات ودفع وإعلانات ومراقبة أخطاء ومزودو ذكاء اصطناعي، ومنهم Fly.io وNeon وGoogle Play وFirebase وAdMob وGmail وSentry عند تفعيله وGroq أو Open WebUI. لا نرسل كلمات المرور أو رموز الشراء إلى مزود الذكاء الاصطناعي، لكن قد يُرسل نص المناقشة أو البيانات اللازمة للشرح والمراجعة.</p></section>
<section class="card"><h2>الحماية والاحتفاظ</h2><p>يُنقل الاتصال عبر HTTPS، وتُجزأ كلمات المرور، وتُشفّر الرموز الحساسة المخزنة. نحتفظ ببيانات الحساب طوال نشاطه. عند الحذف تُلغى الجلسات ويُستبدل البريد والاسم ببيانات مجهولة، بينما قد تُحتفظ سجلات المحفظة والشراء والتدقيق والأمان بالقدر اللازم لمنع الاحتيال، تسوية المنازعات، المحاسبة أو الالتزام القانوني. تختفي النسخ القديمة مع دوران النسخ الاحتياطية وفق مدة الاحتفاظ لدى مزود الاستضافة.</p></section>
<section class="card"><h2>حقوق المستخدم</h2><p>يمكنك تعديل اسمك وصورتك، مراجعة سجل المحفظة، حذف الحساب من التطبيق، أو استخدام صفحة الحذف العامة. يمكنك التواصل لطلب الوصول أو التصحيح أو الحذف الإضافي، مع احتمال الاحتفاظ بسجلات محدودة عندما يفرض القانون أو الأمن ذلك.</p></section>
<section class="card"><h2>الإعلانات والأطفال</h2><p>قد تعرض الخطة المجانية إعلانات عبر Google AdMob، وقد يستخدم المزود معرفات الجهاز وفق إعدادات المستخدم وسياسات Google. التطبيق غير موجه للأطفال دون 13 عامًا، ولا ينبغي لمن لا يملك الأهلية القانونية لاتخاذ قرارات مالية استخدامه دون إشراف ولي مسؤول.</p></section>
""",
    )


@router.get("/terms", response_class=HTMLResponse)
def terms_of_use() -> HTMLResponse:
    return _page(
        "شروط الاستخدام",
        "باستخدام التطبيق أو إنشاء حساب، يوافق المستخدم على هذه الشروط.",
        """
<section class="card warning"><h2>طبيعة الخدمة</h2><p>سهمي كسبان أداة معلومات وتحليل آلي للأسهم المصرية. التطبيق ليس شركة سمسرة، ولا ينفذ أوامر تداول، ولا يحتفظ بأموال المستخدم، ولا يقدم إدارة محافظ أو ضمانًا للربح.</p></section>
<section class="card"><h2>مسؤولية المستخدم</h2><ul><li>التحقق من بيانات السوق ومن ملاءمة القرار لظروفه وقدرته على تحمل الخسارة.</li><li>حماية كلمة المرور ورمز التحقق وعدم مشاركة الحساب.</li><li>عدم استخدام التطبيق للتلاعب أو الاحتيال أو نشر روابط أو بيانات تواصل أو إساءة أو وعود ربح مضللة.</li><li>الالتزام بالقوانين واللوائح المعمول بها في مكان إقامته.</li></ul></section>
<section class="card"><h2>العملات والاشتراكات</h2><p>عملات التطبيق رصيد رقمي للاستخدام داخل الخدمة فقط، ولا تمثل نقودًا، ولا تُسحب أو تُحوّل بين المستخدمين. المشتريات والاشتراكات تتم عبر Google Play وتخضع لسياساته. يمنع تكرار الخصم لنفس العملية، وقد تُرد العملات المحجوزة عند رفض مناقشة وفق قواعد التطبيق.</p></section>
<section class="card"><h2>المحتوى والمراجعة</h2><p>يظل المستخدم مسؤولًا عن محتواه. يجوز فحص المناقشات آليًا وبشريًا، وقبولها أو رفضها أو إخفاؤها، وتجميد التوقع المنشور لتقييمه لاحقًا. لا يعني النشر اعتماد صحة التوقع أو ضمان نتيجته.</p></section>
<section class="card"><h2>توافر الخدمة</h2><p>قد تتأخر بيانات السوق أو تتوقف خدمات خارجية، وقد تكون النتائج ناقصة أو غير دقيقة. يجوز إجراء الصيانة أو تغيير الميزات والأسعار والحدود مع إخطار مناسب عندما يكون التغيير مؤثرًا.</p></section>
<section class="card"><h2>التعليق والإنهاء</h2><p>يجوز تعليق أو حذف الحساب عند الاحتيال أو الإساءة أو اختراق الشروط. يمكن للمستخدم حذف حسابه في أي وقت. لا يؤثر الحذف على السجلات التي يلزم الاحتفاظ بها قانونيًا أو أمنيًا.</p></section>
<section class="card"><h2>القانون والحدود</h2><p>تُفسر هذه الشروط وفق القوانين الواجبة التطبيق في جمهورية مصر العربية، دون الإخلال بحقوق المستهلك الإلزامية. إلى الحد الذي يسمح به القانون، لا يتحمل مشغل التطبيق خسائر التداول أو القرارات المبنية على التحليل الآلي.</p></section>
""",
    )


@router.get("/financial-disclaimer", response_class=HTMLResponse)
def financial_disclaimer() -> HTMLResponse:
    return _page(
        "إخلاء المسؤولية المالية",
        "يجب قراءة هذا التنبيه قبل الاعتماد على أي تحليل أو تقرير أو مناقشة داخل التطبيق.",
        """
<section class="card warning"><h2>ليس توصية استثمارية</h2><p>كل الإشارات والدرجات والسيناريوهات والأهداف ووقف الخسارة واحتمالات الصعود أو الهبوط ناتجة عن نماذج آلية وبيانات تاريخية، وتُعرض لأغراض المعلومات والتعليم ودعم القرار فقط. لا تمثل توصية شخصية بالشراء أو البيع أو الاحتفاظ.</p></section>
<section class="card"><h2>لا ضمان للنتائج</h2><p>الأداء السابق لا يضمن الأداء المستقبلي. الأسواق قد تتحرك بعكس النموذج، وقد تحدث فجوات سعرية أو توقفات أو تغيرات جوهرية لا تظهر في البيانات التاريخية.</p></section>
<section class="card"><h2>بيانات السوق</h2><p>قد تعتمد الخدمة على TradingView ومصادر احتياطية، وقد تكون البيانات متأخرة أو مصححة أو غير مكتملة. يجب مراجعة السعر الفعلي وبيانات البورصة والوسيط قبل تنفيذ أي قرار.</p></section>
<section class="card"><h2>المخاطر</h2><p>الاستثمار في الأسهم ينطوي على احتمال خسارة جزء من رأس المال أو كله. المستخدم وحده مسؤول عن حجم الصفقة والسيولة والضرائب والعمولات والقرار النهائي، وينبغي طلب مشورة متخصص مرخص عند الحاجة.</p></section>
""",
    )


@router.get("/data-safety", response_class=HTMLResponse)
def data_safety() -> HTMLResponse:
    return _page(
        "ملخص سلامة البيانات",
        "مسودة تشغيلية لمساعدة صاحب التطبيق في تعبئة نموذج Data safety في Google Play، ويجب مراجعتها مقابل النسخة الفعلية والـSDKs قبل الإرسال.",
        """
<section class="card"><h2>التصريح المقترح</h2><table><thead><tr><th>فئة البيانات</th><th>أمثلة</th><th>الغرض</th></tr></thead><tbody>
<tr><td>المعلومات الشخصية</td><td>البريد الإلكتروني، الاسم، معرف المستخدم</td><td>إدارة الحساب والأمان والدعم</td></tr>
<tr><td>المعلومات المالية</td><td>سجل المشتريات والاشتراكات داخل Google Play</td><td>تنفيذ المشتريات ومنع الاحتيال؛ لا تُجمع بيانات البطاقة</td></tr>
<tr><td>الرسائل والمحتوى</td><td>المناقشات والبلاغات والاستئنافات</td><td>وظائف المجتمع والمراجعة</td></tr>
<tr><td>نشاط التطبيق</td><td>طلبات التحليل وفتح التقارير وسجل الرصيد</td><td>تقديم الوظائف ومنع الخصم المكرر</td></tr>
<tr><td>معلومات التطبيق والأداء</td><td>سجلات الأعطال والتشخيص وزمن الاستجابة</td><td>الأمان وتحسين الجودة</td></tr>
<tr><td>معرفات الجهاز</td><td>رمز FCM ومعرفات AdMob عند تفعيل الإعلانات</td><td>الإشعارات والإعلانات ومنع الاحتيال</td></tr>
</tbody></table></section>
<section class="card"><h2>إجابات عامة</h2><ul><li>البيانات مشفرة أثناء النقل: نعم، عبر HTTPS.</li><li>يمكن طلب حذف البيانات: نعم، من داخل التطبيق ومن صفحة <code>/delete-account</code>.</li><li>إنشاء الحساب يتطلب البريد الإلكتروني، أما نشر المناقشات ومشاهدة الإعلانات فاختياري.</li><li>لا يجمع التطبيق جهات الاتصال أو الصور الشخصية أو الصوت أو الموقع الدقيق أو الرسائل النصية.</li><li>يجب مراجعة إفصاحات Firebase وAdMob وGoogle Play وSentry وأي SDK مضاف قبل الإرسال النهائي.</li></ul></section>
""",
    )


@router.get("/financial-features", response_class=HTMLResponse)
def financial_features() -> HTMLResponse:
    return _page(
        "الإقرار بالميزات المالية",
        "ملخص جاهز للاستخدام عند تعبئة Financial features declaration في Play Console.",
        """
<section class="card warning"><h2>التصنيف الصحيح للتطبيق</h2><p>يقدم التطبيق معلومات وتحليلات آلية مرتبطة بالأسهم وإدارة مخاطر افتراضية، لذلك يجب الإفصاح عن وجود ميزة مالية مرتبطة بالاستثمار أو الأسهم وفق الخيارات التي يعرضها Play Console وقت التقديم.</p></section>
<section class="card"><h2>ما لا يقدمه التطبيق</h2><ul><li>لا ينفذ صفقات ولا يربط المستخدم بوسيط.</li><li>لا يحتفظ بأموال أو أوراق مالية.</li><li>لا يقدم قروضًا أو ائتمانًا أو تحويل أموال أو تأمينًا أو عملات مشفرة.</li><li>لا يقدم خيارات ثنائية أو وعود ربح مضمون.</li><li>لا يطلب بيانات بطاقة أو حساب بنكي.</li></ul></section>
<section class="card"><h2>وصف مقترح للمراجعة</h2><p>«سهمي كسبان تطبيق معلومات وتحليل آلي لأسهم البورصة المصرية. يعرض مؤشرات فنية وسيناريوهات احتمالية وسجل أداء تعليمي، ولا ينفذ عمليات تداول أو يدير أموال العملاء أو يقدم استشارات استثمارية شخصية. جميع النتائج مصحوبة بإخلاء مسؤولية واضح.»</p></section>
""",
    )


@router.get("/delete-account", response_class=HTMLResponse)
def delete_account_page() -> HTMLResponse:
    return _page(
        "حذف الحساب والبيانات",
        "يمكن حذف الحساب مباشرة من هذه الصفحة أو من قسم «حسابي» داخل التطبيق. يجب إدخال البريد وكلمة المرور لتأكيد الملكية.",
        """
<section class="card warning"><h2>ما الذي سيحدث؟</h2><ul><li>إلغاء كل جلسات تسجيل الدخول والاشتراكات النشطة داخل النظام.</li><li>إخفاء البريد والاسم واستبدالهما ببيانات مجهولة.</li><li>إزالة إمكانية الدخول للحساب نهائيًا.</li><li>قد تبقى سجلات مالية وأمنية وتدقيقية محدودة عند الضرورة القانونية أو لمكافحة الاحتيال.</li></ul></section>
<section class="card"><h2>تأكيد الحذف</h2>
<form id="delete-form"><label for="email">البريد الإلكتروني</label><input id="email" name="email" type="email" autocomplete="email" required>
<label for="password">كلمة المرور</label><input id="password" name="password" type="password" autocomplete="current-password" required>
<button type="submit">حذف الحساب نهائيًا</button><div id="result" role="status" aria-live="polite"></div></form></section>
<script>
const form=document.getElementById('delete-form');const result=document.getElementById('result');
form.addEventListener('submit',async(event)=>{event.preventDefault();if(!confirm('هل أنت متأكد من حذف الحساب نهائيًا؟'))return;
result.className='';result.textContent='جارٍ التحقق والحذف...';const email=document.getElementById('email').value.trim();const password=document.getElementById('password').value;
try{const login=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
if(!login.ok)throw new Error('تعذر التحقق من البريد أو كلمة المرور.');const tokens=await login.json();
const deletion=await fetch('/api/v1/profile/me',{method:'DELETE',headers:{'Content-Type':'application/json','Authorization':'Bearer '+tokens.access_token},body:JSON.stringify({password})});
if(!deletion.ok)throw new Error('تعذر حذف الحساب. راجع كلمة المرور وحاول مرة أخرى.');result.className='ok';result.textContent='تم حذف الحساب بنجاح.';form.reset();}
catch(error){result.className='error';result.textContent=error.message||'حدث خطأ أثناء حذف الحساب.';}});
</script>
""",
    )
