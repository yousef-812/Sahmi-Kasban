import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_mobile_ads/google_mobile_ads.dart';

import '../../core/config/app_config.dart';

class PlanBannerAd extends ConsumerStatefulWidget {
  const PlanBannerAd({required this.enabled, super.key});

  final bool enabled;

  @override
  ConsumerState<PlanBannerAd> createState() => _PlanBannerAdState();
}

class _PlanBannerAdState extends ConsumerState<PlanBannerAd> {
  BannerAd? _bannerAd;
  bool _loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (widget.enabled && _bannerAd == null && !_loading) {
      _load();
    }
  }

  @override
  void didUpdateWidget(covariant PlanBannerAd oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (!widget.enabled && oldWidget.enabled) {
      _disposeAd();
    } else if (widget.enabled && !oldWidget.enabled) {
      _load();
    }
  }

  Future<void> _load() async {
    if (kIsWeb || (!Platform.isAndroid && !Platform.isIOS)) {
      return;
    }
    _loading = true;
    final config = ref.read(appConfigProvider);
    final adUnitId = Platform.isAndroid
        ? config.admobAndroidBannerId
        : config.admobIosBannerId;
    final width = MediaQuery.sizeOf(context).width.truncate();
    final size = await AdSize.getLargeAnchoredAdaptiveBannerAdSize(width);
    if (!mounted || size == null) {
      _loading = false;
      return;
    }

    final banner = BannerAd(
      adUnitId: adUnitId,
      request: const AdRequest(),
      size: size,
      listener: BannerAdListener(
        onAdLoaded: (ad) {
          if (!mounted || !widget.enabled) {
            ad.dispose();
            return;
          }
          setState(() {
            _loading = false;
            _bannerAd = ad as BannerAd;
          });
        },
        onAdFailedToLoad: (ad, error) {
          ad.dispose();
          if (mounted) {
            setState(() {
              _loading = false;
              _bannerAd = null;
            });
          }
        },
      ),
    );
    await banner.load();
  }

  void _disposeAd() {
    _bannerAd?.dispose();
    _bannerAd = null;
    _loading = false;
  }

  @override
  void dispose() {
    _disposeAd();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final banner = _bannerAd;
    if (!widget.enabled || banner == null) {
      return const SizedBox.shrink();
    }
    return SafeArea(
      top: false,
      child: ColoredBox(
        color: Theme.of(context).colorScheme.surface,
        child: Center(
          child: SizedBox(
            width: banner.size.width.toDouble(),
            height: banner.size.height.toDouble(),
            child: AdWidget(ad: banner),
          ),
        ),
      ),
    );
  }
}
