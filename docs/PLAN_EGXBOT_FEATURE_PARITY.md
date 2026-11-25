# خطة تطوير Sahmi Kasban — مستوحاة من تحليلات egxbot.com

> مستند تصميم/تخطيط فقط — **بدون كود**. يكمّل `ROADMAP.md` ولا يعدّله.
> الغرض: سد الفجوات بين قدرات تحليل egxbot والقدرات الحالية لمشروع Sahmi Kasban.

---

## 1. الهدف والمبادئ

**الهدف:** رفع تغطية التحليل في Sahmi Kasban لتقارب ما يقدّمه egxbot، مع الحفاظ على نقاط القوة الحالية (محركات مستقلة + orchestrator + scoring موزون + fingerprint + backtesting).

**المبادئ الحاكمة:**
1. **إعادة الاستخدام أولًا:** معظم الرياضيات موجودة أصلًا في `src/sahmi_kasban/indicators.py` و`engines/`. المطلوب أساسًا طبقة تجميع/تقسيم (screening) + خزن + عرض.
2. **السيرفر هو مصدر الحقيقة:** كل الأرقام تُحسب في الباك-إند؛ الموبايل عرض فقط.
3. **الاتساق:** أي رقم جديد يمر بنفس `scoring`/الوحدات الموجودة بدل منطق مكرر.
4. **الأداء:** الأسكانر الجماعي ثقيل → caching + جدولة + حدود واضحة.
5. **الامتثال:** لا نعتمد على سحب egxbot كواجهة إنتاج (توكن شخصي + `robots.txt` يمنع `/api`). egxbot مرجع أفكار/حقول فقط.
6. **توافق الـ API:** البادئة `settings.api_v1_prefix` = `/api/v1`. مسارات جديدة تحت `/api/v1/scanner/...`.

---

## 2. مصفوفة التكافؤ (Parity Matrix)

| قدرة egxbot | الوضع في Sahmi Kasban | القرار |
|---|---|---|
| Technical bulk screener (كل السوق، vector فني) | غير موجود (تحليل فردي فقط) | **T1 — إضافة** |
| Fibonacci scanner (درجة/حالة/Golden zone) | غير موجود | **T1 — إضافة** |
| Harmonic pattern scanner (XABCD) | غير موجود | **T1 — إضافة** |
| SMC per symbol (BOS/CHoCH/OB/FVG) | موجود في `engines/smc.py` | إتاحته عبر endpoint مسطّح (ضمن T1) |
| تحليل لحظي (SSE/WS) | WS للأسعار فقط، التحليل batch/cached | **T6 — إضافة** |
| دورة حياة الإشارة t1/t2/t3 + Trailing SL | `trade_plan` موجود بلا تتبّع | **T2 — إضافة** |
| مركز تنبيهات + cooldowns | لا يوجد | **T2 — إضافة** |
| News + sentiment في القرار | أخبار كشاشة فقط | **T3 — إضافة** |
| Order flow / whales (order book, bulk trades) | لا يوجد | **T4 — إضافة** |
| ماكرو/عالمي (فوركس، معادن، مؤشرات عالمية) | لا يوجد | **T5 — إضافة** |
| Market status/session | جزئي (بيانات جلسة متفرقة) | **T5 — توحيد** |
| Sector leaderboard | `sector_reports.py` mock | **T5 — حساب حقيقي** |
| Portfolio analytics | لا يوجد | **T7 — إضافة** |
| Fundamentals داخل الـ score + تقويم أرباح | محرك منفصل خارج الـ pipeline | **T8 — دمج** |
| Expected VWAP / Intraday | لا يوجد | مدمج في T4/T5 (منخفض الأولوية) |

**الفجوات الموجودة حاليًا (من جرد الكود):** المحرك الأساسي خارج الـ score؛ لا تقويم أرباح؛ لا sentiment في الـ scoring؛ لا ML حقيقي؛ لا تحليلات محفظة؛ لا order-flow؛ لا ماكرو؛ لا بث لحظي للتحليل؛ leaderboards وهمية؛ index resolver ثابت؛ لا محرك تنبيهات؛ backtesting لا يغطي المسار الأساسي.

---

## 3. تفاصيل المسارات

### T1 — الأسكانر الجماعي (Technical / Fibonacci / Harmonic) — **P0**

**الهدف:** endpoint واحد يرجّع snapshot فني لكل أسهم EGX + أسكانرات متخصصة، مطابقة لحقول egxbot المرصودة.

**التصميم:**
- خدمة جديدة `backend/app/services/scanner.py` تستدعي الطبقة الحالية:
  - مصدر الشموع: `app.market_data.provider` (TradingView primary / YFinance fallback) بنفس طريقة `reusable_data_fetcher`.
  - المؤشرات: توسيع `src/sahmi_kasban/indicators.py` ليضم المحسوب حاليًا في `reusable_data_fetcher.TechnicalAnalysisService` (Stochastic, CCI, Williams %R, ROC, Bollinger, MFI, ADX, pivots) → **نقلها لمصدر واحد** في النواة.
- ثلاث عائلات في نفس الوحدة: `technical`, `fibonacci`, `harmonic`.

**الحقول المطلوبة (مرجع egxbot):**
- **Technical:** `technicalScore` (-100..100)، `technicalRating` (buy/sell/neutral)، `rsi14`، `macd/macdSignal/macdHistogram/macdBullish/macdCrossUp/macdCrossDown`، `adx14/plusDi14/minusDi14`، `atr14/atrPercent`، `bbUpper/Middle/Lower/bbPosition/bbBandwidth`، `sma20/50/200`، `ema20/50`، `priceVsSma20/50/200`، `ema20Above50/emaCross*`، `relativeVolume20`، `stochasticK/D`، `mfi14`، `obvTrend`، `breakout20/breakdown20`، `performance5d/20d/60d`، `high52Week/low52Week`، `timeframe`، `candlesUsed`.
- **Fibonacci:** anchors (low/high مع index/price/date)، `swingPercent`، `swingAtr`، `retracementPercent`، `currentZone` (golden 61.8–65% …)، `distancePercent/distanceAtr`، `status` (testing…)، `score`، `confidence`، `trendAligned`، `metrics`، `levels[]` (23.6/38.2/50/61.8/78.6).
- **Harmonic:** `patterns[]` (XABCD: نوع النمط + نسب + حالة)، `pivot_count`، `pivot_levels`، `engine_version`.

**الحسابات (تعريف دقيق):**
- `technicalScore`: مجموع مُوزّن مؤشرات (اتجاه MAs + RSI + MACD + ADX/DI + Bollinger position + Stoch/MFI + relative volume + breakout + أداء) → تطبيع لـ [-100, 100]. نوثّق الأوزان في `scoring.py` (قسم منفصل `SCANNER_WEIGHTS`).
- `technicalRating`: عتبات على `technicalScore` (مثال: ≥40 buy، ≤-40 sell، وإلا neutral).
- Fibonacci: كشف swing عبر آخر 2 pivots معتمدة (ZigZag بمضاعف ATR)، ثم حساب مستويات retracement؛ تحديد `currentZone` بأقرب نطاق؛ `score` = تقارب السعر + `trendAligned` + volume.
- Harmonic: pivots (نفس محرك SMC/zigzag) → تسلسل X,A,B,C,D → تحقق نسب (Gartley/Bat/Butterfly/Crab) → `patterns[]`.

**الـ Endpoints (تحت `/api/v1`):**
- `GET /scanner/technical` — كل السوق (paged/sortable/filter: sector, rating, minScore).
- `GET /scanner/fibonacci` — قائمة/فلترة؛ و`GET /scanner/fibonacci/{symbol}` للتفاصيل.
- `GET /scanner/harmonic/{symbol}`.
- (اختياري) `GET /scanner/smc/{symbol}` — تمرير مسطّح لنتيجة `engines/smc.py` للمقارنة/العرض.

**الخزن والجدولة:**
- جدول `scanner_snapshots` (شبه `market_data.py`): `kind`, `symbol`, `as_of`, `payload(JSONB)`, `score`, `rating`.
- job جديد `jobs/scanner_refresh.py` (يُسجّل في `jobs/scheduler.py`) يبنيه خلال/بعد الجلسة دوريًا (config: كل N دقيقة).
- كاش بنمط `app.market_data.cache.py`.

**الواجهة (Flutter):** شاشة "الماسح" (`mobile/lib`, route جديد) بتابات: فني / فيبوناتشي / هارمونيك، مع فرز وفلترة قطاع.

**إعادة الاستخدام:** `engines/technical.py`، `engines/smc.py`، `indicators.py`، `market_data/provider.py`، `market_data/cache.py`.

**معايير القبول:**
- `/scanner/technical` يرجّع كل الأسهم المدعومة في < 2s (من الكاش) وبترتيب صحيح.
- مطابقة `technicalScore` بشكل متسق مع `engine technical` لنفس الشمعة (اختبار وحدة).
- فيبوناتشي يكتشف Golden zone صحيح على سيناريو مُصنّع (fixture).
- اختبارات: `backend/tests` للـ endpoints + `src/tests` للحسابات.

---

### T2 — دورة حياة الإشارة + مركز التنبيهات — **P0**

**الهدف:** تتبّع كل توصية/إشارة حتى إغلاقها (t1/t2/t3/Trailing SL) + تنبيهات.

**التصميم:**
- نموذج `SignalLifecycle`: يرتبط بـ `daily_market_reports`/`watchlist`/`analysis_history`.
- حالات (من egxbot): `new → buy → t1done/t2done/t3done → tsl` + terminal `closed/expired`.
- جدول `signals`: `id, symbol, direction, entry, stop, targets(t1,t2,t3), state, opened_at, updated_at, closed_at, pnl_pct, source(report/watchlist/manual)`.
- جدول `signal_events`: التاريخ الزمني لكل انتقال (audit).
- جدول `alerts`: `user_id, type, ref_id, title, body, is_read, created_at` + cooldown tracking.
- خدمة `services/signal_lifecycle.py` (على غرار `watchlist_signals.py`): تُقاد إمّا بالـ scheduler (تقييم دوري مقابل الأسعار) أو عبر WS quotes.
- Trailing SL: يتتبع أعلى/أدنى سعر بعد التنشيط (زي `highestPriceAfterActivation`/`lowestPriceAfterActivation` عند egxbot).

**الـ Endpoints (`/api/v1`):**
- `GET /signals` (فلترة my/symbol/state)، `GET /signals/{id}`.
- `GET /alerts`، `POST /alerts/{id}/read`، `POST /alerts/read-all` (يُناسب `notifications.py` الموجود — يمكن التمديد بدل جدول جديد).
- `GET /performance/signals` (يُدمج مع `performance.py` الموجود).

**الموديلات/الـ migrations:** `0000` جديدة على غرار `0022_watchlist.py` / `0033_...`.

**الواجهة:** "مركز الإشارات + التنبيهات" (`mobile/lib`)، ربط بـ `notifications` الموجود.

**إعادة الاستخدام:** `engines/risk.py` (trade_plan/targets)، `services/watchlist_signals.py`، `services/report_performance.py`.

**معايير القبول:** انتقالات حالة صحيحة على fixtures؛ cooldown يمنع تكرار التنبيه؛ PnL محسوب صح.

---

### T3 — الأخبار + Sentiment في القرار — **P1**

**الهدف:** sentiment السهم/الخبر يصبح مدخلًا في الـ scoring + فلتر مخاطرة، بدل كونه شاشة منفصلة.

**التصميم:**
- خدمة `services/sentiment.py`: تجميع أخبار `services/news.py` لكل رمز → درجة sentiment (من -1..1) مع تلاشي زمني (decay).
- محرك جديد `engines/news_sentiment.py` (يشبه `sector.py`): يستهلك `context["news_sentiment"]`.
- إدراج وزنه في `scoring.DEFAULT_WEIGHTS` (وزن صغير، قابل للضبط) + gate خفيف (sentiment سلبي قوي + BUY → WATCH).
- مصادر أخبار قائمة فعليًا (لا يوجد crawler egxbot) — نستخدم `news_crawler` الموجود.

**الـ Endpoints:** `GET /stocks/{ticker}/sentiment`، وتوسيع `market.py` بالتضمين في التحليل.

**معايير القبول:** إعادة تشغيل التحليل تُنتج علامة sentiment ثابتة لنفس الأخبار؛ الوزن موثّق ويظهر في `analysis_quality`.

---

### T4 — Order flow / Whales — **P1**

**الهدف:** عمق السوق والصفقات والصفقات الضخمة (مكافئ `getOrderBook/getTrades/getBulkTrades/getMarketDepthRange`).

**التصميم:**
- الاعتماد على مزوّد البيانات: TradingView عمق محدود؛ قد نحتاج مصدر بورصة/باقات حسب `MARKET_DATA_STRATEGY.md`.
- وحدة `market_data/order_flow.py`: order book، تجميع الصفقات، كشف "whales" (صفقات > عتبة قيمة/حجم).
- تخزين لقطات خفيفة + بث.

**الـ Endpoints:** `GET /market/orderbook/{ticker}`، `GET /market/trades/{ticker}`، `GET /market/bulk-trades`، `GET /market/depth/{ticker}`.

**الواجهة:** تبويب "العمق/الصفقات" في شاشة السهم.

**معايير القبول:** بيانات متسقة مع الجلسة؛ كشف whales بحد أدنى موثّق.

---

### T5 — ماكرو/عالمي + Market status + Sector leaderboard محسوب — **P1**

**الهدف:** سياق عام + إصلاح leaderboards الوهمية.

**التصميم:**
- `market_data/global_market.py`: مؤشرات عالمية + فوركس + معادن/طاقة (مصدر خارجي، كاش طويل).
- توحيد حالة الجلسة: خدمة `market_status.py` (10:00–14:30 القاهرة، أحد–خميس) تُستخدم في كل الجداول.
- **إصلاح `services/sector_reports.py`**: استبدال الحمولة الثابتة بحساب حقيقي من `scanner` (T1) + `sector_quality.py`.

**الـ Endpoints:** `GET /market/global`، `GET /market/status`، وتصحيح `GET /reports/sectors/{sector_id}/leaderboard`.

**معايير القبول:** leaderboard يُحسب من بيانات فعلية (لا حقول ثابتة)؛ market status متسق مع كل الواجهات.

---

### T6 — بث التحليل لحظيًا — **P2**

**الهدف:** تحويل التحليل من batch/cached إلى دفع لحظي (مكافئ SSE `/Market/stream`).

**التصميم:** توسيع `market_data/broadcaster.py` ليبث إشارات/تنبيهات (T2) + تحديثات scanner (T1) عند تغيّر الحالة؛ قنوات WS + SSE اختيارية.

**معايير القبول:** رسالة فورية عند تغيّر حالة إشارة/تنبيه.

---

### T7 — تحليلات المحفظة — **P2**

**الهدف:** ارتباط/تنويع/تعرض قطاعي (فجوة صريحة).

**التصميم:** خدمة `services/portfolio_analytics.py` (من نقاط `performance` + holdings)، حساب correlation matrix، تنويع، حدود قطاعية.

**الـ Endpoints:** `GET /portfolio/analytics`، `POST /portfolio/scenarios`.

---

### T8 — دمج الأساسيات في الـ Score + تقويم الأرباح — **P2**

**الهدف:** إدخال `engines/investment.py` في الـ pipeline (اختياري بوزن) + بيانات تقويم أرباح/قوائم.

**التصميم:** توسيع `orchestrator.py` بمحرك اختياري `fundamental` (يُفعّل بالطلب/النوع)، وتوسيع `market_data/fundamental.py`، وإضافة جدول `earnings_calendar`.

---

## 4. اعتبارات عامة

- **الكاش:** كل مسار ثقيل يعتمد `market_data/cache.py` ببصمة (fingerprint) لتجنّب الضرب على المزود.
- **الحدود:** rate-limit على endpoints الأسكانر (كما في `auth_rate_limit.py`).
- **المصادر:** أي اعتماد على عمق/صفقات/ماكرو يجب أن يتوافق مع `MARKET_DATA_STRATEGY.md` وحقوق المصدر.
- **الامتثال:** لا نستخدم egxbot كواجهة إنتاج؛ حقول egxbot هنا مرجع للتصميم فقط.
- **الاختبارات:** اختبارات حساب في `src/tests`، واختبارات API في `backend/tests`، fixtures لأنماط (فيبوناتشي/هارمونيك).
- **التوثيق:** تحديث `README.md`/`ROADMAP.md` و`IMPLEMENTATION_LOG_*` بعد كل مرحلة.

---

## 5. الترقيم الزمني المقترح

| المرحلة | المسارات | المخرج |
|---|---|---|
| Phase A (P0) | T1 (technical) + T2 | أسكانر جماعي + دورة حياة إشارة/تنبيهات |
| Phase B (P0→P1) | T1 (fibonacci/harmonic) + T3 | أسكانرات متخصصة + sentiment في القرار |
| Phase C (P1) | T4 + T5 | order flow/whales + ماكرو + leaderboards حقيقية |
| Phase D (P2) | T6 + T7 + T8 | بث لحظي + محفظة + أساسيات في الـ score |

---

## 6. المخاطر والأسئلة المفتوحة

- **مصدر البيانات:** هل TradingView يكفي لحقول scanner (52w، performance)? أم يلزم مصدر ثانوي؟
- **حِمل الأسكانر:** حساب كل السوق أثناء الجلسة قد يكون ثقيلًا → نحتاج جدولة/تقسيم.
- **order flow:** توفّر عمق السوق قد يكون محدودًا/مدفوعًا.
- **تعارض الواجهة:** تسمية `technicalScore` تختلف عن `engine score` الحالي → نحتاج توثيق الحدود بينهما لمنع الالتباس.
- **الأولوية:** هل نُدخل sentiment/الأساسيات في الـ score فعليًا أم كطبقة عرض وتنبيه؟

---

## 7. ملحق — عقود egxbot المرصودة (مرجع حقول فقط)

- `GET /api/Scanner/technical` → `{"items":[{symbol,timeframe,candleTimestamp,candlesUsed,technicalScore,technicalRating,rsi14,macd,macdSignal,macdHistogram,macdBullish,macdCrossUp,macdCrossDown,adx14,plusDi14,minusDi14,atr14,atrPercent,bbUpper,bbMiddle,bbLower,bbPosition,bbBandwidth,sma20,sma50,sma200,ema20,ema50,priceVsSma20,priceVsSma50,priceVsSma200,ema20Above50,emaCrossUp,emaCrossDown,relativeVolume20,stochasticK,stochasticD,mfi14,obvTrend,breakout20,breakdown20,performance5d,performance20d,performance60d,high52Week,low52Week}]}`
- `GET /api/Scanner/fibonacci` → `{"enabled":true,"items":[{symbol,nameAr,sector,price,direction,timeframe,anchorStart{kind,index,price,timestamp,date},anchorEnd{...},swingPercent,swingAtr,retracementPercent,currentZone{kind,key,labelAr,labelEn,priceLow,priceHigh},distancePercent,distanceAtr,status,score,confidence,trendAligned,metrics{atr14,ema20,ema50,rsi14,relativeVolume20,turnover},levels[{key,kind,ratio,price,labelAr,labelEn}]}]}`
- `GET /api/Scanner/harmonic/{symbol}` → `{"symbol","patterns":[],"pivot_count","pivot_levels","engine_version"}`
- `GET /api/Scanner/smc/{symbol}` → `{"symbol","current_price","smc_score","institutional_bias","market_structure","liquidity_zones[{type,price,strength,is_active}]","order_blocks[{type,high,low,strength,is_broken}]","fair_value_gaps[]","reasoning[]"}`
- `GET /api/Scanner/momentum` → `{"enabled":false,...}` (feature_disabled)
- `GET /api/Scanner/analysis-alerts?minutes=&limit=` → `{"enabled":true,"items":[{activationPrice,activationTimestamp,breakoutBarsAgo,detectedAt,direction,highestPriceAfterActivation,id,invalidationPrice,lowestPriceAfterActivation,messageAr,nameAr,patternId,patternNameAr,patternSnapshot{boundaries[...]}}]}`
