# ROADMAP تنفيذي — تطبيق تكافؤ egxbot في Sahmi Kasban

> مرجع التصميم: `docs/PLAN_EGXBOT_FEATURE_PARITY.md`.
> الغرض من هذا الملف: تقسيم كل مسار إلى **Work Packages (WP)** صغيرة مستقلة، كل واحدة ينفّذها نموذج واحد، ثم **تختبر نفسها** وتتوقف. أنت (المستخدم) تراجع معي الديزاين بعد كل WP ونعدّل قبل التالي.

---

## 0. كيف تُستخدم هذه الخطة (اقرأ أولًا)

### 0.1 قواعد ثابتة لكل نموذج منفّذ
1. ينفّذ **WP واحدة فقط** في الجلسة. لا ينتقل لغيرها.
2. يقرأ قسم **Context Pack** أدناه + الملفات المرجعية المذكورة في الـ WP قبل الكتابة.
3. يتبع النمط الموجود حرفيًا (نفس التسمية/الـ imports/الـ patterns).
4. لا يضيف مكتبات جديدة دون الحاجة، وإن لزم يحدّث `pyproject.toml` المعني.
5. **يمنع الكود الميت أو التعليقات غير الضرورية.**
6. بعد التنفيذ: يشغّل **الاختبارات + الـ lint** المذكورة في الـ WP، ثم يكتب تقريرًا: ماذا أنشأ/عدّل، نتيجة الأوامر، أي انحراف عن الخطة.
7. لا يعدّل `ROADMAP`/`PLAN`/docs بدون طلب.

### 0.2 Context Pack (يُمرّر لكل نموذج)

**مفتاح الحقيقة للمعرّفات:**
- بادئة الـ API: `settings.api_v1_prefix = "/api/v1"` (تطبيقها في `backend/app/main.py:120`).
- النواة: حزمة `sahmi_kasban` في `src/sahmi_kasban/` (تُستورد مباشرة؛ مثبتة editable).
- Backend: `backend/`، الحزمة `app`.

**أنماط Backend الإلزامية:**
- Settings: `from app.core.config import get_settings` → `settings = get_settings()`؛ المتغيرات تُعلن كحقول في `Settings` وتُقرأ من env بالاسم الكبير (مثال: `scanner_refresh_enabled` → `SCANNER_REFRESH_ENABLED`).
- DB: `from app.db.base import Base, TimestampMixin`؛ الجداول: `__tablename__` جمع snake_case صريح، PK افتراضيًا UUID: `id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)`؛ أعمدة وقت: ورّث `TimestampMixin`؛ JSON: `mapped_column(JSON, ...)`.
- الموديلات تُصرّح في `backend/app/models/<domain>.py` **وتُستورد في** `backend/app/models/__init__.py` (ضروري لـ Alembic/tests).
- الجلسة: `from app.db.session import get_db` عبر alias `DatabaseSession`؛ المستخدم عبر alias `CurrentUser`؛ من `app.api.dependencies`.
- الراوتر: `router = APIRouter(prefix="/<domain>", tags=["<domain>"])` في `backend/app/api/routes/<domain>.py`؛ يُسجّل في `backend/app/api/router.py`.
- Schemas: `backend/app/schemas/<domain>.py` بأنماط `*In` / `*Out` / `*Response`، واستخدم `ConfigDict(from_attributes=True)` عند التحويل من ORM.
- الخدمات: دوال async تأخذ `db: Session`؛ الاستعلامات بنمط SQLAlchemy 2.0 (`select(...)`, `db.scalars(...)`, `db.scalar(...)`).
- Jobs: ملف في `backend/app/jobs/<job>.py` يعرّف `async def run_<job>() -> dict` يفتح `with SessionLocal() as db:`؛ يُسجّل `asyncio.create_task(...)` في `lifespan` بـ `backend/app/main.py` (احترم حماية `Environment.TEST`).

**Migration:** الرأس الحالي `0047_news_resolved_url`. الـ WP الجديدة: `down_revision = "0047_news_resolved_url"` (أو رأس آخر WP سابقة). الأوامر من `backend/`: `python -m alembic upgrade head` و`python -m alembic downgrade -1`. استخدم `render_as_batch=True` (مضبوط مسبقًا).

**أنماط النواة الإلزامية:**
- الشموع: `pandas.DataFrame` بأعمدة `open, high, low, close, volume` (+`timestamp` اختياري). للمعالجة: `prepare_candles(...)` ثم `enrich_indicators(...)`.
- Engines: `class X(AnalysisEngine): name=...; def analyze(self, candles: pd.DataFrame, context: dict[str, object]) -> EngineResult`.
- `EngineResult(name, score(0..100), confidence(0..100), status, details, reasons)`.
- المؤشرات تُضاف في `src/sahmi_kasban/indicators.py` وتُدرج في `enrich_indicators` عند اللزوم.

**الأوامر:**
- اختبارات النواة (من الجذر `D:\sahmi_kasban`): `pytest -q --tb=short tests` ثم `ruff check src tests`.
- اختبارات/lint الـ Backend (من `D:\sahmi_kasban\backend`): `python -m pytest -q --tb=short` ثم `python -m ruff check .`.
- لا يوجد typecheck (mypy/pyright) في المشروع — لا تفترضه.

### 0.3 قالب البرومبت الموحّد (انسخه لكل نموذج)
```
أنت مطوّر في مشروع Sahmi Kasban (D:\sahmi_kasban).
اقرأ أولًا قسم "Context Pack" وكامل تعريف الـ Work Package <WP-XX> من الملف:
  D:\sahmi_kasban\docs\ROADMAP_EGXBOT_PARITY.md
ثم نفّذ WP-XX فقط، حرفيًا وحسب الأنماط المذكورة، بدون أي توسّع خارج نطاقها.
بعد الانتهاء: شغّل الأوامر المذكورة في قسم "الاختبارات" الخاص بـ WP-XX واعرض مخرجاتها.
التزم بمعايير "DoD". لا تعدّل ملفات خارج قائمة الملفات، ولا الـ ROADMAP/PLAN.
اكتب تقريرًا نهائيًا: الملفات المُنشأة/المُعدّلة، مخرجات الاختبارات/الـ lint، وأي انحراف.
```

---

## 1. خريطة المراحل والـ Work Packages

| Phase | WP | العنوان | الأولوية | التبعية |
|---|---|---|---|---|
| A | WP-01 | توسيع مؤشرات النواة | P0 | — |
| A | WP-02 | متجه الأسكانر الفني (Core) | P0 | WP-01 |
| A | WP-03 | أسكانر فيبوناتشي (Core) | P0 | WP-01 |
| A | WP-04 | أسكانر الأنماط الهارمونية (Core) | P1 | WP-01 |
| A | WP-05 | موديلات/هجرة لقطات الأسكانر | P0 | WP-02 |
| A | WP-06 | خدمة الأسكانر (Backend) | P0 | WP-02/05 |
| A | WP-07 | راوتر الأسكانر + Schemas | P0 | WP-06 |
| A | WP-08 | Job تحديث الأسكانر + Scheduler | P0 | WP-06 |
| A | WP-09 | شاشة الأسكانر (Flutter) | P0 | WP-07 |
| A | WP-10 | موديلات/هجرة الإشارات والتنبيهات | P0 | — |
| A | WP-11 | خدمة دورة حياة الإشارة | P0 | WP-10 |
| A | WP-12 | API الإشارات + التنبيهات | P0 | WP-11 |
| A | WP-13 | Job تقييم الإشارات | P0 | WP-11 |
| A | WP-14 | شاشات الإشارات/التنبيهات (Flutter) | P0 | WP-12 |
| B | WP-15 | محرك Sentiment في النواة + الـ scoring | P1 | — |
| B | WP-16 | خدمة Sentiment في Backend + Endpoint | P1 | WP-15 |
| B | WP-17 | عرض Sentiment (Flutter) | P2 | WP-16 |
| C | WP-18 | Order flow/Whales (Backend) | P1 | — |
| C | WP-19 | واجهات Order flow (Flutter) | P2 | WP-18 |
| C | WP-20 | السوق العالمي/الماكرو (Backend) | P1 | — |
| C | WP-21 | توحيد Market Status | P1 | — |
| C | WP-22 | Sector leaderboard حقيقي | P1 | WP-06 |
| D | WP-23 | بث التحليل لحظيًا | P2 | WP-11 |
| D | WP-24 | تحليلات المحفظة | P2 | — |
| D | WP-25 | دمج الأساسيات في الـ Score + تقويم الأرباح | P2 | — |
| E | WP-26 | بنية مزوّد العمق (DepthProvider Registry) | P0 | WP-18 |
| E | WP-27 | Top-of-book (bid/ask/spread) | P0 | WP-26 |
| E | WP-28 | لوحة مؤشرات لكل سهم (API + Flutter) | P0 | WP-07 |
| E | WP-29 | ضغط الشراء/البيع (Core + Backend + Flutter) | P0 | WP-26 |
| E | WP-30 | عمق الحجم POC/VAH/VAL | P1 | WP-29 |
| E | WP-31 | الأساسيات والأرباح (Flutter UI فقط) | P1 | WP-25 |
| E | WP-32 | إشارات السهم داخل صفحته (Flutter فقط) | P1 | WP-12 |
| E | WP-33 | اتساع السوق + شاشة الأسواق | P2 | WP-20 |
| E | WP-34 | شاشتا المتابعة + تحليلات المحفظة (Flutter فقط) | P2 | WP-12/24 |
| E | WP-35 | شاشة DOM (Ladder) كاملة | P2 | WP-26/19 |

---

## 2. تفاصيل الـ Work Packages

---

### WP-01 — توسيع مؤشرات النواة
- **التبعية/الأولوية:** لا يوجد / P0.
- **الهدف:** جعل كل الحقول التي يحتاجها الأسكانر قابلة للحساب في النواة (بدل `reusable_data_fetcher`).
- **الملفات:**
  - تعديل `src/sahmi_kasban/indicators.py`.
  - اختبار جديد `tests/test_scanner_indicators.py`.
- **التعاقد (أضف دوال عامة):**
  - `stochastic(df, k_window=14, d_window=3) -> tuple[pd.Series, pd.Series]` (`%K`, `%D`).
  - `adx(df, window=14) -> tuple[pd.Series, pd.Series, pd.Series]` (`adx`, `plus_di`, `minus_di`).
  - `bollinger(close, window=20, num_std=2.0) -> tuple[pd.Series, pd.Series, pd.Series]` (upper, middle, lower).
  - `mfi(df, window=14) -> pd.Series`.
  - `obv(df) -> pd.Series`؛ ودالة مساعدة `obv_trend(df, window=20) -> int` (1 صاعد / -1 هابط / 0).
  - `relative_volume(df, window=20) -> pd.Series`.
  - `performance_pct(close, periods) -> pd.Series`.
  - `high_52w(close, window=252) -> float`, `low_52w(close, window=252) -> float`.
  - `breakout_flag(close, window=20) -> pd.Series` و`breakdown_flag(...)`.
  - توسيع `enrich_indicators` لإضافة الأعمدة: `stoch_k, stoch_d, adx, plus_di, minus_di, bb_upper, bb_middle, bb_lower, bb_bandwidth, bb_position, mfi, obv, obv_trend, relative_volume_20`.
- **قواعد:** كل الدوال تأخذ/ترجع pandas؛ استخدم `safe_float`؛ أقواس صغيرة `min_periods` بأمان؛ لا تكسر الأعمدة الموجودة (tests القائمة يجب أن تبقى خضراء).
- **الاختبارات:**
  - `tests/test_scanner_indicators.py`: حالات صغيرة مُصنّعة لكل مؤشر (صف واحد على الأقل، قيم معروفة) + التأكد أن `enrich_indicators` تُنتج كل الأعمدة الجديدة.
  - تشغيل: `pytest -q --tb=short tests` و`ruff check src tests`.
- **DoD:** كل الدوال موجودة وموثّقة توقيعًا؛ `enrich_indicators` يضيف الأعمدة؛ الاختبارات والـ lint خضراء؛ لا تغيير في سلوك الأعمدة القديمة.

---

### WP-02 — متجه الأسكانر الفني (Core)
- **التبعية/الأولوية:** WP-01 / P0.
- **الهدف:** دالة تعطي snapshot فني كامل لسهم واحد يطابق حقول egxbot.
- **الملفات:**
  - إنشاء `src/sahmi_kasban/scanner/__init__.py` (يُصدّر الدوال العامة).
  - إنشاء `src/sahmi_kasban/scanner/technical.py`.
  - اختبار `tests/test_scanner_technical.py`.
- **التعاقد:**
  - `TECHNICAL_WEIGHTS: dict[str, float]` وثابت `SCANNER_VERSION = "scanner-tech-v1"`.
  - `def build_technical_snapshot(df: pd.DataFrame, *, timeframe: str = "1D") -> dict[str, object]` — يستدعي `enrich_indicators` داخليًا (أو يستقبل مؤشرًا مسبقًا) ويرجّع المفاتيح بالضبط: `symbol` يُضاف من الخارج؛ الحقول: `timeframe, candleTimestamp, candlesUsed, technicalScore, technicalRating, rsi14, macd, macdSignal, macdHistogram, macdBullish, macdCrossUp, macdCrossDown, adx14, plusDi14, minusDi14, atr14, atrPercent, bbUpper, bbMiddle, bbLower, bbPosition, bbBandwidth, sma20, sma50, sma200, ema20, ema50, priceVsSma20, priceVsSma50, priceVsSma200, ema20Above50, emaCrossUp, emaCrossDown, relativeVolume20, stochasticK, stochasticD, mfi14, obvTrend, breakout20, breakdown20, performance5d, performance20d, performance60d, high52Week, low52Week`.
  - `def technical_score(snapshot: dict[str, object]) -> float` (تطبيع [-100,100]) و`def technical_rating(score: float) -> str` (عتبات ≥40 `buy`، ≤-40 `sell`، غير ذلك `neutral`).
- **قواعد:** إعادة استخدام المؤشرات من WP-01 فقط؛ لا تكرار رياضيات؛ `ema20/ema50` تُحسب هنا (أضف `ema(close,20/50)`).
- **الاختبارات:** حالة سهم مُصنّعة (صاعد/هابط/عرضي) والتأكد من الإشارة والاتجاه؛ التأكد من وجود كل المفاتيح؛ حدود النطاق [-100,100].
- **DoD:** الدوال مُصدّرة من `scanner/__init__.py`؛ كل المفاتيح موجودة؛ اختبارات/lint خضراء.

---

### WP-03 — أسكانر فيبوناتشي (Core)
- **التبعية/الأولوية:** WP-01 / P0.
- **الملفات:** إنشاء `src/sahmi_kasban/scanner/swings.py` (كشف pivots عام)، `src/sahmi_kasban/scanner/fibonacci.py`، اختبار `tests/test_scanner_fibonacci.py`، وتصدير من `scanner/__init__.py`.
- **التعاقد:**
  - `swings.detect_pivots(df, *, left=3, right=3) -> list[dict]` — كل pivot: `{"index","timestamp","price","kind"("high"|"low")}`.
  - `swings.latest_impulse(pivots) -> tuple[dict, dict] | None` (آخر قاع→قمة أو قمة→قاع).
  - `fibonacci.scan_fibonacci(df, *, symbol: str, meta: dict | None = None) -> dict | None` — يرجّع: `symbol, nameAr, sector, price, direction, timeframe, anchorStart{kind,index,price,timestamp,date}, anchorEnd{...}, swingPercent, swingAtr, retracementPercent, currentZone{kind,key,labelAr,labelEn,priceLow,priceHigh}, distancePercent, distanceAtr, status, score, confidence, trendAligned, metrics{atr14,ema20,ema50,rsi14,relativeVolume20,turnover}, levels[{key,kind,ratio,price,labelAr,labelEn}]`.
- **قواعد:** مستويات 23.6/38.2/50/61.8/78.6؛ `golden` = نطاق 61.8–65%؛ `status` ∈ {`testing`,`approaching`,`broken`}؛ `score` من تقارب السعر + `trendAligned` + volume.
- **الاختبارات:** حالة swing مُصنّعة → مستوى ونطاق صحيحان؛ `None` عند عدم كفاية البيانات.
- **DoD:** التوقيع/الحقول مطابقة؛ اختبارات/lint خضراء.

---

### WP-04 — أسكانر الأنماط الهارمونية (Core)
- **التبعية/الأولوية:** WP-01 / P1.
- **الملفات:** إنشاء `src/sahmi_kasban/scanner/harmonic.py` + اختبار `tests/test_scanner_harmonic.py` + تصدير.
- **التعاقد:** `scan_harmonic(df, *, symbol: str) -> dict` يرجّع `symbol, patterns[{type,points{X,A,B,C,D},ratios,status,score}], pivot_count, pivot_levels, engine_version`.
- **قواعد:** أنماط Gartley/Bat/Butterfly/Crab بنسب فيبوناتشي على تسلسل XABCD من pivots؛ `engine_version=2`؛ `patterns=[]` عند عدم التطابق.
- **الاختبارات:** حالة نمط معروف (fixture) → اكتشاف صحيح؛ عدم إيجابيات كاذبة على بيانات عشوائية.
- **DoD:** اختبارات/lint خضراء؛ لا اعتماد على الشبكة.

---

### WP-05 — موديلات/هجرة لقطات الأسكانر
- **التبعية/الأولوية:** WP-02 / P0.
- **الملفات:**
  - إنشاء `backend/app/models/scanner.py`؛
  - تعديل `backend/app/models/__init__.py`;
  - إنشاء `backend/alembic/versions/0044_scanner_snapshots.py`.
- **التعاقد (موديل `ScannerSnapshot`):**
  - `__tablename__ = "scanner_snapshots"`؛ `TimestampMixin`.
  - `id: UUID` PK؛ `kind: str` (String(20))؛ `symbol: str` (String(24))؛ `timeframe: str` (String(8), default "1D")؛ `as_of: datetime`؛ `score: Decimal|None` (Numeric(6,2))؛ `rating: str|None` (String(16))؛ `payload: dict` (JSON).
  - فهارس: `ix_scanner_snapshots_kind_symbol` بحيث تُقرأ الأحدث بسرعة: `Index("ix_scanner_snapshots_kind_as_of", "kind", text("as_of DESC"))`.
- **الهجرة:** `revision="0044_scanner_snapshots"`, `down_revision="0043_stock_signatures"`؛ اتبع نمط `0022_watchlist.py` للـ JSONB.
- **الاختبارات:** من `backend/`: `python -m alembic upgrade head` ثم `downgrade -1` ثم `upgrade head`؛ `python -m pytest -q --tb=short`؛ `python -m ruff check .`.
- **DoD:** Migration صعودًا وهبوطًا نظيفة؛ الموديل مستورد في `__init__`؛ الاختبارات خضراء.

---

### WP-06 — خدمة الأسكانر (Backend)
- **التبعية/الأولوية:** WP-02 + WP-05 / P0.
- **الملفات:** إنشاء `backend/app/services/scanner.py`؛ اختبار `backend/tests/test_scanner_service.py`.
- **التعاقد:**
  - `async def refresh_scanner_snapshot(db, provider, *, kind: str, tickers: list[str] | None = None, force: bool = False) -> dict[str, object]` — يجلب الشموع عبر `get_cached_or_fresh_history(...)`، يحسب عبر `sahmi_kasban.scanner`، يخزّن صفًا في `ScannerSnapshot` لكل رمز (يستبدل الأحدث لنفس `kind/symbol/timeframe`)، ويرجّع `{"kind","count","as_of"}`.
  - `async def get_scanner_items(db, *, kind: str, sector: str | None = None, rating: str | None = None, min_score: float | None = None, limit: int = 500) -> list[dict]` — يقرأ أحدث `as_of` لكل رمز ويفلتر ويرتّب.
  - مصدر قائمة الرموز: استخدم كتالوج الأدوات الموجود (`app.market_data.catalog` / `_extended_universe`) كما في `generate_daily_top10.py`.
- **قواعد:** لا نادٍ لـ egxbot؛ المصدر هو المزوّد الداخلي؛ تعامل مع فشل رمز واحد دون إسقاط الكل.
- **الاختبارات:** Mock provider يرجّع شموعًا مُصنّعة؛ التأكد من العدد والفلترة والترتيب. `python -m pytest -q --tb=short` + `ruff check .` من `backend/`.
- **DoD:** الخدمة تعمل بلا شبكة في الاختبار؛ لا استثناءات غير مُعالجة.

---

### WP-07 — راوتر الأسكانر + Schemas
- **التبعية/الأولوية:** WP-06 / P0.
- **الملفات:** إنشاء `backend/app/schemas/scanner.py`، `backend/app/api/routes/scanner.py`، تعديل `backend/app/api/router.py`؛ اختبار `backend/tests/test_scanner_api.py`.
- **التعاقد (Endpoints تحت `/api/v1/scanner`):**
  - `GET /scanner/technical` → `{items:[...], count}`؛ query: `sector, rating, min_score, limit`.
  - `GET /scanner/fibonacci` → نفس الشكل؛ `GET /scanner/fibonacci/{symbol}` → عنصر واحد أو 404.
  - `GET /scanner/harmonic/{symbol}` → عنصر واحد أو 404.
  - `GET /scanner/smc/{symbol}` → تفاصيل SMC (من `engines/smc.py`).
  - الحماية: `CurrentUser` (تسجيل دخول مطلوب).
- **قواعد:** `router = APIRouter(prefix="/scanner", tags=["scanner"])`؛ سجّل في `api/router.py`.
- **الاختبارات:** عبر `client` fixture (stub provider) — كود 200/بنية صحيحة/401 بدون توكن. `python -m pytest -q --tb=short` + `ruff check .`.
- **DoD:** كل الـ endpoints مسجّلة وتعمل وتظهر في OpenAPI؛ الاختبارات خضراء.

---

### WP-08 — Job تحديث الأسكانر + Scheduler
- **التبعية/الأولوية:** WP-06 / P0.
- **الملفات:** إنشاء `backend/app/jobs/scanner_refresh.py`؛ تعديل `backend/app/jobs/scheduler.py` و`backend/app/main.py` و`backend/app/core/config.py` و`.env.example`.
- **التعاقد:**
  - `async def run_scanner_refresh() -> dict` يفتح `with SessionLocal() as db:` وينادي `refresh_scanner_snapshot(db, get_market_data_provider(), kind=...)` للأنواع `technical/fibonacci`.
  - Settings جديدة: `scanner_refresh_enabled: bool = True`, `scanner_refresh_minutes: int = 15`.
  - Register: إضافة استدعاء داخل `run_daily_scan_scheduler` (احترم الحماية/العلم) أو loop جديد `asyncio.create_task` في `lifespan`.
- **قواعد:** Idempotent؛ لا يعمل في `Environment.TEST`؛ يلتزم بجلسة السوق.
- **الاختبارات:** تشغيل `python -m app.jobs.scanner_refresh` (سيرجّع skipped/count)؛ `python -m pytest -q --tb=short`؛ `ruff check .`.
- **DoD:** الـ job يعمل يدويًا؛ لا يكسر السcheduler الحالي؛ الإعدادات موثّقة في `.env.example`.

---

### WP-09 — شاشة الأسكانر (Flutter)
- **التبعية/الأولوية:** WP-07 / P0.
- **الملفات:** إنشاء نماذج/خدمة API وإضافة route في `mobile/lib/app/router.dart` + شاشة `mobile/lib/features/scanner/...`.
- **التعاقد:** شاشة بتابات (فني/فيبوناتشي/هارمونيك)، فرز وفلترة قطاع/تقييم، RTL عربي.
- **قواعد:** اتبع أنماط الـ API client الموجودة في الموبايل.
- **الاختبارات:** `flutter analyze` (إن متاح) + تشغيل يدوي للشاشة.
- **DoD:** الشاشة تعرض بيانات حقيقية من `/api/v1/scanner/*`؛ لا أخطاء analyze.

---

### WP-10 — موديلات/هجرة الإشارات والتنبيهات
- **التبعية/الأولوية:** لا يوجد / P0.
- **الملفات:** إنشاء `backend/app/models/signals.py`؛ تعديل `backend/app/models/__init__.py`؛ هجرة `0045_signals_alerts.py`.
- **التعاقد:**
  - `Signal`: `id UUID`، `ticker String(24)`، `direction String(8)` (long/short)، `entry/stop/t1/t2/t3 Numeric(16,6)`، `state String(16)` ∈ {`new`,`buy`,`t1done`,`t2done`,`t3done`,`tsl`,`closed`,`expired`}، `opened_at/updated_at/closed_at DateTime`، `pnl_pct Numeric(10,4)`، `source String(24)`، `ref_report_id UUID|None`، `user_id UUID|None`، `meta JSON`.
  - `SignalEvent`: `id UUID`، `signal_id FK`، `event String(32)`، `price Numeric(16,6)`، `note String(255)|None`، `created_at`.
  - `Alert`: `id UUID`، `user_id FK`، `type String(32)`، `ref_id UUID|None`، `title String(160)`، `body Text`، `is_read Boolean default False`، `created_at`.
- **الهجرة:** `0045_signals_alerts` مع `down_revision="0044_scanner_snapshots"`.
- **الاختبارات:** upgrade/downgrade/upgrade + pytest + ruff.
- **DoD:** migrations نظيفة؛ موديلات مستوردة؛ لا تكسر اختبارات القائمة.

---

### WP-11 — خدمة دورة حياة الإشارة
- **التبعية/الأولوية:** WP-10 / P0.
- **الملفات:** إنشاء `backend/app/services/signal_lifecycle.py`؛ اختبار `backend/tests/test_signal_lifecycle.py`.
- **التعاقد:**
  - `def open_signal(db, *, ticker, direction, entry, stop, targets: tuple[float,float,float], source, user_id=None, ref_report_id=None) -> Signal`.
  - `def advance_signal(db, signal: Signal, *, high: float, low: float, close: float) -> list[SignalEvent]` — انتقالات الحالة + Trailing SL: بعد بلوغ هدف يتحوّل الـ stop لأعلى سعر/أدنى سعر بعد التنشيط.
  - `def close_signal(db, signal, *, reason: str, price: float) -> Signal` (يحسب `pnl_pct`).
  - `def state_transitions() -> dict[str, set[str]]` (لأغراض التوثيق/الاختبار).
- **قواعد:** منطق بحت لا يلمس الشبكة؛ يكتب `SignalEvent` لكل انتقال؛ يحترم تسلسل `t1→t2→t3→tsl`.
- **الاختبارات:** تسلسل شراء كامل يحقق الأهداف ثم trailing ثم close؛ وسيناريو ضرب الـ stop.
- **DoD:** كل الانتقالات مُختبرة؛ `pnl_pct` صحيح؛ لا انحدار.

---

### WP-12 — API الإشارات + التنبيهات
- **التبعية/الأولوية:** WP-11 / P0.
- **الملفات:** إنشاء `backend/app/schemas/signals.py`، `backend/app/api/routes/signals.py`؛ تعديل `api/router.py`؛ اختبار `backend/tests/test_signals_api.py`.
- **التعاقد:**
  - `GET /signals` (فلترة `state`, `ticker`, `mine`)، `GET /signals/{id}`.
  - `POST /signals` (إنشاء يدوي — Admin أو من report)، `POST /signals/{id}/advance` (Admin/test).
  - `GET /alerts`، `POST /alerts/{id}/read`، `POST /alerts/read-all`.
  - تكامل: عند توليد top10 اليومي (`services/daily_reports.py`) تُفتح إشارات تلقائيًا للـ BUY.
- **قواعد:** `prefix="/signals"` و`prefix="/alerts"` (يمكن راوتران في نفس الملف)؛ سجّل في `api/router.py`.
- **الاختبارات:** client fixture — 401/200، إنشاء→تقدّم→إغلاق.
- **DoD:** كل الـ endpoints تعمل؛ التكامل مع daily report لا يكسر `generate_daily_top10`.

---

### WP-13 — Job تقييم الإشارات
- **التبعية/الأولوية:** WP-11 / P0.
- **الملفات:** إنشاء `backend/app/jobs/signal_evaluation.py`؛ تعديل `scheduler.py` (+ العلم في `config.py`).
- **التعاقد:** `async def run_signal_evaluation() -> dict` — يقرأ الإشارات المفتوحة، يجلب السعر/الـ high/low (من `fetch_single_quote` أو شموع اليوم)، ينادي `advance_signal`/`close_signal`، ويولّد `Alert` عند كل انتقال.
- **قواعد:** Idempotent؛ احترم جلسة السوق؛ opcional العلم `signal_evaluation_enabled`.
- **الاختبارات:** mock للسعر + db؛ انتقال واحد يُنتج Alert؛ pytest+ruff.
- **DoD:** يعمل يدويًا وسجّل في الـ scheduler دون كسر الحالي.

---

### WP-14 — شاشات الإشارات/التنبيهات (Flutter)
- **التبعية/الأولوية:** WP-12 / P0.
- **الملفات:** route + شاشات في `mobile/lib` + ربط notifications الموجود.
- **التعاقد:** قائمة الإشارات (الحالة، PnL، الأهداف) + مركز تنبيهات (قراءة/تعليم الكل).
- **DoD:** بيانات حقيقية من `/signals` و`/alerts`؛ لا أخطاء analyze.

---

### WP-15 — محرك Sentiment في النواة + الـ scoring
- **التبعية/الأولوية:** لا يوجد / P1.
- **الملفات:** إنشاء `src/sahmi_kasban/engines/news_sentiment.py`؛ تعديل `src/sahmi_kasban/scoring.py` و`src/sahmi_kasban/orchestrator.py` و`engines/__init__.py`؛ اختبار `tests/test_news_sentiment_engine.py`.
- **التعاقد:**
  - `class NewsSentimentEngine(AnalysisEngine): name = "news_sentiment"` — يقرأ `context["news_sentiment"]` (float -1..1) + `context["news_sample_size"]`؛ يرجّع `EngineResult` (score 0..100؛ 50 عند غياب بيانات). `details`: `sentiment, sample_size, coverage`.
  - إضافة `"news_sentiment": 0.05` لـ `DEFAULT_WEIGHTS` + إدراج في `DIRECTIONAL_ENGINES`، وإضافتها للـ pipeline في `orchestrator.py` **بشكل اختياري** (تُدرج دائمًا؛ عند غياب السياق تعطي 50 محايد).
  - تعديل `_REQUIRED_PREPARED_COLUMNS` غير مطلوب (لا يقرأ أعمدة جديدة).
- **قواعد:** لا انحدار على الاختبارات القائمة (وزن صغير + سلوك محايد عند الغياب)؛ وثّق الأوزان.
- **الاختبارات:** `tests/test_news_sentiment_engine.py` + تشغيل كامل `pytest -q` للتأكد من عدم انحدار `test_core_v2.py`/`test_core_v23.py`.
- **DoD:** المحرك يعمل، الوزن مُدرج، لا انحدار.

---

### WP-16 — خدمة Sentiment في Backend + Endpoint
- **التبعية/الأولوية:** WP-15 / P1.
- **الملفات:** إنشاء `backend/app/services/sentiment.py`؛ تعديل `backend/app/services/stock_analysis.py` (تمرير `context["news_sentiment"]` للـ analyzer من أخبار `services/news.py`)؛ `backend/app/api/routes/market.py` + schema؛ اختبار.
- **التعاقد:**
  - `def compute_symbol_sentiment(db, ticker: str, *, days: int = 7) -> dict` (`{score:-1..1, sample_size, as_of}`) مع decay زمني.
  - `GET /stocks/{ticker}/sentiment` (أو ضمن مسار market) → schema.
  - في `execute_stock_analysis`: احسب sentiment ومرّره عبر `context={"news_sentiment": ..., "news_sample_size": ...}` عند استدعاء `analyzer.analyze(...)`.
- **قواعد:** لا تكسر مسار التحليل الحالي إن غابت الأخبار؛ الأداء عبر cache.
- **الاختبارات:** خدمة mock للأخبار → درجة صحيحة؛ pytest+ruff.
- **DoD:** Sentiment يظهر في التحليل ومختبر.

---

### WP-17 — عرض Sentiment (Flutter)
- **التبعية/الأولوية:** WP-16 / P2. **الملفات:** شاشة السهم. **DoD:** عرض الدرجة/عدد الأخبار.

---

### WP-18 — Order flow/Whales (Backend)
- **التبعية/الأولوية:** لا يوجد / P1.
- **الملفات:** إنشاء `backend/app/market_data/order_flow.py`؛ `backend/app/schemas/order_flow.py`؛ `backend/app/api/routes/market.py` (إضافة endpoints)؛ اختبار.
- **التعاقد:** `async def get_order_book(db, ticker) -> dict`، `async def get_recent_trades(db, ticker, limit=200) -> list[dict]`، `async def detect_whales(db, ticker, *, value_threshold) -> list[dict]`؛ Endpoints: `GET /market/orderbook/{ticker}`, `GET /market/trades/{ticker}`, `GET /market/bulk-trades`, `GET /market/depth/{ticker}`.
- **قواعد:** اعتمد موفّر البيانات الحالي؛ إن لم تتوفر بيانات العمق → ارجع `{"available": false}` بوضوح (لا 500).
- **DoD:** تعمل أو تفشل بأمان؛ pytest+ruff.

---

### WP-19 — واجهات Order flow (Flutter)
- **التبعية/الأولوية:** WP-18 / P2. تبويب في شاشة السهم. **DoD:** عرض العمق/الصفقات/whales.

---

### WP-20 — السوق العالمي/الماكرو (Backend)
- **التبعية/الأولوية:** لا يوجد / P1.
- **الملفات:** إنشاء `backend/app/market_data/global_market.py`؛ schema؛ endpoint `GET /market/global`؛ اختبار.
- **التعاقد:** مؤشرات عالمية + فوركس + معادن/طاقة (كاش طويل)؛ رجوع آمن عند فشل المصدر.
- **DoD:** endpoint يعمل بكاش؛ pytest+ruff.

---

### WP-21 — توحيد Market Status
- **التبعية/الأولوية:** لا يوجد / P1.
- **الملفات:** إنشاء `backend/app/services/market_status.py`؛ endpoint `GET /market/status`؛ استبدال أي حساب حالة مكرر في `market_data/quotes.py`/غيره ليعتمد الخدمة.
- **التعاقد:** `def market_status(now: datetime | None = None) -> dict` (فتح/إغلاق، الجلسة 10:00–14:30 القاهرة، أحد–خميس).
- **DoD:** مصدر واحد للحقيقة؛ الاختبارات خضراء؛ لا انحدار على `quotes`.

---

### WP-22 — Sector leaderboard حقيقي
- **التبعية/الأولوية:** WP-06 / P1.
- **الملفات:** تعديل `backend/app/services/sector_reports.py` و`backend/app/api/routes/sector_reports.py`؛ اختبار.
- **التعاقد:** احسب leaderboard من لقطات الأسكانر (WP-06) + `services/sector_quality.py` بدل الحمولة الثابتة.
- **DoD:** لا حمولات وهمية؛ pytest يتحقق من الحساب؛ آلية الخصم (2 coins) تبقى كما هي.

---

### WP-23 — بث التحليل لحظيًا
- **التبعية/الأولوية:** WP-11 / P2.
- **الملفات:** تعديل `backend/app/market_data/broadcaster.py` + endpoint WS/SSE.
- **التعاقد:** بث أحداث `signal.updated`, `alert.created` عند تغيّر الحالة.
- **DoD:** عميل تجريبي يستقبل الحدث؛ لا يكسر بث الأسعار.

---

### WP-24 — تحليلات المحفظة
- **التبعية/الأولوية:** لا يوجد / P2.
- **الملفات:** إنشاء `backend/app/services/portfolio_analytics.py` + schema + endpoints؛ اختبار.
- **التعاقد:** `GET /portfolio/analytics` (correlation matrix، تنويع، تعرض قطاعي).
- **DoD:** حساب صحيح على محفظة مُصنّعة؛ pytest+ruff.

---

### WP-25 — دمج الأساسيات في الـ Score + تقويم الأرباح
- **التبعية/الأولوية:** لا يوجد / P2.
- **الملفات:** تعديل `src/sahmi_kasban/orchestrator.py` (إدخال `FundamentalInvestmentEngine` اختياريًا عبر flag في `AnalysisConfig`)، `backend/app/market_data/fundamental.py`، موديل/هجرة `earnings_calendar`، endpoint، اختبار.
- **التعاقد:** flag `enable_fundamentals: bool = False` في `AnalysisConfig`، وتمرير بيانات الأساسيات عبر `context`؛ جدول `earnings_calendar` + endpoint `GET /market/earnings-calendar`.
- **DoD:** لا انحدار على المسار الافتراضي (flag مغلق)؛ الاختبارات خضراء.

---

### WP-26 — بنية مزوّد العمق (DepthProvider Registry)
- **التبعية/الأولوية:** WP-18 / P0.
- **الملفات:** `backend/app/market_data/types.py` (dataclasses `DepthLevel`/`OrderBookData`/`RecentTradeItem`/`RecentTradeData`/`DepthSummaryData` + بروتوكول `DepthProvider` وثوابت `DEPTH_CAP_ORDER_BOOK|TRADES|DEPTH|TOP_OF_BOOK`)، `backend/app/market_data/depth.py` (جديد: `get_depth_provider()` + `supports()`)، `backend/app/market_data/tradingview_depth.py` (جديد: هيكّل `TradingViewDepthProvider` بقدرات فارغة)، `backend/app/market_data/order_flow.py`، `backend/app/schemas/order_flow.py`، `backend/app/core/config.py` + `backend/.env.example`، `backend/tests/test_depth_provider.py` (جديد) + تحديث assertions في `backend/tests/test_order_flow.py`.
- **التعاقد:** إعداد `MARKET_DATA_DEPTH_PROVIDER` (افتراضي `none`؛ المسموح `none|tradingview`)؛ `get_order_book`/`get_recent_trades`/`get_market_depth` تمرّ عبر المزوّد المُفعّل ذي القدرة (`capabilities`) المطابقة، وإلا `available:false` + `reason` (وحقل اختياري `provider` في الاستجابة).
- **DoD:** `tests/test_depth_provider.py` + `tests/test_order_flow.py` خضراء؛ `ruff check` و`ruff format --check` نظيفان على الملفات المُعدّلة.

---

### WP-27 — Top-of-book (bid/ask/spread) الآن
- **التبعية/الأولوية:** WP-26 / P0.
- **الملفات:** `backend/app/market_data/top_of_book.py` (جديد)، `backend/app/schemas/order_flow.py`، `backend/app/api/routes/market.py`، `backend/tests/test_order_flow.py`؛ قسم Flutter اختياري في `mobile/lib/features/order_flow/`.
- **التعاقد:** `GET /market/top-of-book/{ticker}` → `{available, ticker, bid, ask, mid_price, spread, spread_bp, as_of, source}` من `StockDataFetcher.get_realtime_price` (bid/ask بدون أحجام) مع كاش قصير (5-10 ث)؛ الفشل → `available:false` + `reason` لا 500.
- **DoD:** اختبار مع fetcher وهمي + اختبار فشل؛ pytest+ruff.

---

### WP-28 — لوحة مؤشرات لكل سهم (API + Flutter)
- **التبعية/الأولوية:** WP-07 / P0.
- **الملفات:** `backend/app/services/scanner.py` (استخراج `build_technical_item(db, provider, symbol)` بنمط `build_harmonic_item` سطر366)، `backend/app/api/routes/scanner.py`، `backend/tests/test_scanner_api.py`، `mobile/lib/features/market/indicators_card.dart` (جديد) + repository/providers + إدراج قسم في `mobile/lib/features/market/stock_detail_screen.dart`.
- **التعاقد:** `GET /scanner/technical/{symbol}` يعيد لقطة الأسكانر الفني (تُحسب عند الغياب، 404 لرمز غير موجود)؛ القسم يعرض RSI/MACD/ADX/ATR%/MFI/Stoch/BB/relVolume/MA + badge التقييم.
- **DoD:** اختبارات API خضراء؛ `flutter analyze` خالٍ.

---

### WP-29 — ضغط الشراء/البيع (Core + Backend + Flutter)
- **التبعية/الأولوية:** WP-26 / P0.
- **الملفات:** `src/sahmi_kasban/indicators.py` (إضافة `close_location_value`، `buy_sell_volume`، `accumulation_distribution`، `ad_trend`، `flow_summary`)، `tests/test_flow_indicators.py` (جديد)، `backend/app/services/stock_flow.py` (جديد) + `backend/app/schemas/market.py` + `backend/app/api/routes/market.py` (بجانب `/stocks/{ticker}/sentiment` سطر690) + `backend/tests/test_stock_flow_api.py` (جديد)، `mobile/lib/features/flow/` (جديد: models/repository/providers/`flow_card.dart`) + إدراج في `stock_detail_screen.dart`.
- **التعاقد:** `GET /stocks/{ticker}/flow?days=90` → `{available, ticker, buy_share_pct, sell_share_pct, net_volume, ad_trend, mfi14, obv_trend, verdict(accumulate|distribute|neutral), as_of}`؛ محسوب من OHLCV لا أوامر فعلية (يُوضّح في تذييل القسم).
- **DoD:** اختبارات النواة (ثوابت مُصنّعة) + اختبار API + `flutter analyze`.

---

### WP-30 — عمق الحجم (POC/VAH/VAL)
- **التبعية/الأولوية:** WP-29 / P1.
- **الملفات:** `src/sahmi_kasban/volume_profile.py` (جديد) + `tests/test_volume_profile.py`، `backend/app/services/volume_profile.py` (جديد) + schema + endpoint + اختبار، قسم Flutter (histogram أفقي بـ CustomPaint أو أشرطة).
- **التعاقد:** `GET /stocks/{ticker}/volume-profile?days=250` → `{available, ticker, poc, value_area_high, value_area_low, bins[{price_low,price_high,volume}], above_value_pct, below_value_pct, as_of}` (منطقة القيمة 70%).
- **DoD:** مجموع أحجام المصفوفة = مجموع أحجم الشموم؛ POC ينتمي لأعلى bin؛ pytest+ruff+analyze.

---

### WP-31 — الأساسيات والأرباح (Flutter UI فقط)
- **التبعية/الأولوية:** WP-25 / P1.
- **الملفات:** `mobile/lib/features/market/stock_fundamentals_card.dart` (جديد) + providers + إدراج في `stock_detail_screen.dart`؛ لا backend جديد.
- **التعاقد:** عرض PE/PB/dividend yield/ROE/market cap/EPS/valuation/recommendation من `GET /stocks/{ticker}/investment` (market.py:675) + بطاقة الأرباح القادمة من `GET /market/earnings-calendar?ticker=` (earnings.py:13).
- **DoD:** `flutter analyze` خالٍ؛ حالات تحميل/خطأ/بيانات مكتملة.

---

### WP-32 — إشارات السهم داخل صفحته (Flutter فقط)
- **التبعية/الأولوية:** WP-12 / P1.
- **الملفات:** `mobile/lib/features/signals/` (تعديل `signals_providers.dart` لفلتر ticker + `signals_card.dart` جديد) + `stock_detail_screen.dart`؛ لا backend جديد (`GET /signals?ticker=` موجود في signals.py:47، و`SignalsRepository.list(ticker:)` موجود).
- **التعاقد:** قسم «الإشارات» يعرض إشارات السهم (الحالة/الدخول/الوقف/الأهداف/P&L) + زر يفتح `/signals`.
- **DoD:** `flutter analyze` خالٍ.

---

### WP-33 — اتساع السوق + شاشة الأسواق
- **التبعية/الأولوية:** WP-20 / P2.
- **الملفات:** `backend/app/services/market_breadth.py` (جديد) + `backend/app/schemas/market.py` + `backend/app/api/routes/market.py` + `backend/tests/test_market_breadth.py` (جديد)، `mobile/lib/features/markets/markets_screen.dart` (جديد) + route `/markets` في `mobile/lib/router.dart` + مدخل في الدرج (`dashboard_screen.dart`).
- **التعاقد:** `GET /market/breadth` → `{advancers, decliners, unchanged, total, advance_decline_ratio, sector_performance[{sector, avg_change_pct}], as_of}` محسوبة من `fetch_market_quotes()`؛ الشاشة بتبويبات: عالمي (`GET /market/global`، موجود بلا UI) + اتساع + حالة السوق (`GET /market/status`).
- **DoD:** اختبار breadth (سوق مُصنّع) + `flutter analyze`.

---

### WP-34 — شاشتا المتابعة + تحليلات المحفظة (Flutter فقط)
- **التبعية/الأولوية:** WP-12/24 / P2.
- **الملفات:** `mobile/lib/features/watchlist/watchlist_screen.dart` + `mobile/lib/features/portfolio/portfolio_screen.dart` (جديدان) + repositories/providers + routes `/watchlist`, `/portfolio` في `mobile/lib/router.dart`؛ لا backend جديد (`GET /watchlist` watchlist.py:30 + `GET /portfolio/analytics` portfolio_analytics.py:14 موجودان).
- **التعاقد:** شاشة المتابعة تُدار من `GET /watchlist`؛ شاشة المحفظة تعرض correlation/diversification/sector exposure من `GET /portfolio/analytics`.
- **DoD:** `flutter analyze` خالٍ.

---

### WP-35 — شاشة DOM (Ladder) كاملة
- **التبعية/الأولوية:** WP-26/19 / P2.
- **الملفات:** `mobile/lib/features/order_flow/` (تعديل: `dom_screen.dart` جديد + route)؛ تعديل اختياري طفيف في `backend/app/schemas/order_flow.py` (حقل imbalance اختياري).
- **التعاقد:** سلّم كامل من `OrderBookSnapshot` (bids/asks + cumulative + imbalance ratio + spread)؛ عند `available:false` تُعرض رسالة صادقة «يتطلب مزوّد بيانات عمق» بدل ادعاء أرقام؛ تعمل فعليًا لحظة تفعيل `MARKET_DATA_DEPTH_PROVIDER`.
- **DoD:** `flutter analyze` خالٍ؛ لا كسر `order_flow_card.dart` الحالي.

---

## 3. بوابات الجودة لكل WP (Gates)
1. الاختبارات الخاصة بالـ WP + اختبارات الحزمة الكاملة (لا انحدار): `pytest -q` (النواة) و`python -m pytest -q --tb=short` (backend).
2. `ruff check` على النطاق المتأثر.
3. الهجرات: `upgrade head` → `downgrade -1` → `upgrade head` (للوحدات التي فيها هجرة).
4. تقرير انحراف مكتوب + اقتراح تعديل ديزاين إن لزم.

## 4. ترتيب التنفيذ الموصى به
`WP-01 → WP-02 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09` ثم `WP-10 → WP-11 → WP-12 → WP-13 → WP-14` (Phase A كاملة)، وبعدها تباعًا حسب الجدول. مرحلة E: `WP-26 → WP-27 → WP-29 → WP-28 → WP-30 → WP-31 → WP-32 → WP-33 → WP-34 → WP-35` (WP-26 الأساس الذي يبني عليه 27/29/35).

## 5. أسئلة تصميم مفتوحة (تحتاج قرارك قبل تنفيذ المعني بها)
- **WP-02:** هل `technicalScore` يُعرض كرقم مستقل عن `final_score` (توصية: نعم، لتقارب egxbot)؟
- **WP-06:** مصدر كتالوج الرموز الكامل — نعتمد الكتالوج الحالي أم نوسّعه؟
- **WP-18:** ~~هل نموفّر عمق السوق فعليًا؟~~ **أُجيب (WP-26):** لا يوجد مزوّد عمق مجاني لـ EGX؛ الإطار مبني (`DepthProvider` registry) والحقول تُرجع `available:false` + `reason` افتراضيًا، والتفعيل لاحقًا يتطلب مزوّدًا مرخصًا عبر `MARKET_DATA_DEPTH_PROVIDER` دون أي تغيير في الطبقات العلوية.
- **WP-15:** وزن sentiment النهائي (مقترح 0.05) وإعادة توازن الأوزان.
