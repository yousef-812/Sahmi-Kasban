import 'dart:async';
import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:in_app_purchase/in_app_purchase.dart';

import '../auth/session_controller.dart';
import '../wallet/wallet_providers.dart';
import 'monetization_models.dart';
import 'monetization_repository.dart';
import 'rewarded_ad_gateway.dart';

const _unset = Object();

class MonetizationState {
  const MonetizationState({
    this.loading = true,
    this.storeAvailable = false,
    this.catalog,
    this.status,
    this.products = const <String, ProductDetails>{},
    this.adBusy = false,
    this.purchasingProductId,
    this.message,
    this.error,
  });

  final bool loading;
  final bool storeAvailable;
  final MonetizationCatalog? catalog;
  final MonetizationStatusModel? status;
  final Map<String, ProductDetails> products;
  final bool adBusy;
  final String? purchasingProductId;
  final String? message;
  final String? error;

  MonetizationState copyWith({
    bool? loading,
    bool? storeAvailable,
    Object? catalog = _unset,
    Object? status = _unset,
    Map<String, ProductDetails>? products,
    bool? adBusy,
    Object? purchasingProductId = _unset,
    Object? message = _unset,
    Object? error = _unset,
  }) {
    return MonetizationState(
      loading: loading ?? this.loading,
      storeAvailable: storeAvailable ?? this.storeAvailable,
      catalog: identical(catalog, _unset)
          ? this.catalog
          : catalog as MonetizationCatalog?,
      status: identical(status, _unset)
          ? this.status
          : status as MonetizationStatusModel?,
      products: products ?? this.products,
      adBusy: adBusy ?? this.adBusy,
      purchasingProductId: identical(purchasingProductId, _unset)
          ? this.purchasingProductId
          : purchasingProductId as String?,
      message: identical(message, _unset) ? this.message : message as String?,
      error: identical(error, _unset) ? this.error : error as String?,
    );
  }
}

class MonetizationController extends StateNotifier<MonetizationState> {
  MonetizationController({
    required MonetizationRepository repository,
    required InAppPurchase store,
    required RewardedAdGateway rewardedAdGateway,
    required Future<void> Function() onEntitlementChanged,
  }) : _repository = repository,
       _store = store,
       _rewardedAdGateway = rewardedAdGateway,
       _onEntitlementChanged = onEntitlementChanged,
       super(const MonetizationState()) {
    _purchaseSubscription = _store.purchaseStream.listen(
      _handlePurchaseUpdates,
      onError: _handlePurchaseStreamError,
    );
    unawaited(refresh());
  }

  final MonetizationRepository _repository;
  final InAppPurchase _store;
  final RewardedAdGateway _rewardedAdGateway;
  final Future<void> Function() _onEntitlementChanged;
  late final StreamSubscription<List<PurchaseDetails>> _purchaseSubscription;

  Future<void> refresh() async {
    state = state.copyWith(loading: true, error: null, message: null);
    try {
      final results = await Future.wait<Object>([
        _repository.getCatalog(),
        _repository.getStatus(),
      ]);
      final catalog = results[0] as MonetizationCatalog;
      final status = results[1] as MonetizationStatusModel;
      final storeAvailable = Platform.isAndroid && await _store.isAvailable();
      var products = const <String, ProductDetails>{};
      if (storeAvailable && catalog.storeProductIds.isNotEmpty) {
        final response = await _store.queryProductDetails(
          catalog.storeProductIds,
        );
        products = <String, ProductDetails>{
          for (final product in response.productDetails) product.id: product,
        };
        if (response.error != null) {
          state = state.copyWith(
            message: 'تعذر تحميل بعض أسعار Google Play حاليًا.',
          );
        }
      }
      if (mounted) {
        state = state.copyWith(
          loading: false,
          storeAvailable: storeAvailable,
          catalog: catalog,
          status: status,
          products: products,
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(loading: false, error: error.toString());
      }
    }
  }

  Future<void> showRewardedAd() async {
    final status = state.status;
    if (state.adBusy || status == null || !status.rewardedAd.eligible) {
      return;
    }
    final platform = Platform.isAndroid
        ? 'android'
        : Platform.isIOS
        ? 'ios'
        : null;
    if (platform == null) {
      state = state.copyWith(error: 'الإعلانات متاحة على Android وiOS فقط.');
      return;
    }

    state = state.copyWith(adBusy: true, error: null, message: null);
    try {
      final beforeCount = status.rewardedAd.rewardsUsedToday;
      final session = await _repository.createRewardedAdSession(
        platform: platform,
      );
      final watched = await _rewardedAdGateway.loadAndShow(session);
      if (!watched) {
        state = state.copyWith(
          adBusy: false,
          message: 'لم يكتمل الإعلان، لذلك لم تُضف أي عملات.',
        );
        return;
      }

      var verified = false;
      try {
        await _repository.claimRewardedAdSession(session: session);
        verified = true;
      } catch (_) {
        if (session.testMode) {
          await _repository.simulateRewardedAd(session: session);
        }
        verified = await _waitForReward(beforeCount);
      }

      await _onEntitlementChanged();
      final updatedStatus = await _repository.getStatus();
      if (mounted) {
        state = state.copyWith(
          adBusy: false,
          status: updatedStatus,
          message: verified
              ? 'تم التحقق من الإعلان وإضافة المكافأة إلى المحفظة.'
              : 'اكتمل الإعلان، والتحقق من Google ما زال قيد المعالجة. حدّث الصفحة بعد قليل.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        final rawStr = error.toString();
        final displayErr = rawStr.contains('403')
            ? 'تعذر بدء جلسة الإعلان (رمز 403). يرجى التأكد من تفعيل البريد الإلكتروني أو إعادة تسجيل الدخول.'
            : rawStr;
        state = state.copyWith(adBusy: false, error: displayErr);
      }
    }
  }

  Future<void> purchaseProduct(String productId) async {
    if (state.purchasingProductId != null) {
      return;
    }
    if (!Platform.isAndroid) {
      state = state.copyWith(
        error: 'المشتريات في هذه المرحلة مرتبطة بـGoogle Play على Android.',
      );
      return;
    }
    final catalog = state.catalog;
    final product = state.products[productId];
    if (catalog == null || product == null) {
      state = state.copyWith(error: 'المنتج غير متاح في Google Play حاليًا.');
      return;
    }

    state = state.copyWith(
      purchasingProductId: productId,
      error: null,
      message: null,
    );
    final purchaseParam = PurchaseParam(productDetails: product);
    try {
      final started = catalog.isCoinPack(productId)
          ? await _store.buyConsumable(
              purchaseParam: purchaseParam,
              autoConsume: false,
            )
          : await _store.buyNonConsumable(purchaseParam: purchaseParam);
      if (!started && mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: 'لم يبدأ طلب الشراء من Google Play.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: error.toString(),
        );
      }
    }
  }

  Future<void> restorePurchases() async {
    if (!Platform.isAndroid || !state.storeAvailable) {
      state = state.copyWith(
        error: 'استعادة المشتريات غير متاحة على هذا الجهاز.',
      );
      return;
    }
    state = state.copyWith(message: 'جارٍ استعادة مشتريات Google Play...');
    try {
      await _store.restorePurchases();
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(error: error.toString());
      }
    }
  }

  Future<bool> _waitForReward(int beforeCount) async {
    for (var attempt = 0; attempt < 7; attempt += 1) {
      final current = await _repository.getStatus();
      if (!mounted) {
        return false;
      }
      state = state.copyWith(status: current);
      if (current.rewardedAd.rewardsUsedToday > beforeCount) {
        return true;
      }
      await Future<void>.delayed(
        Duration(milliseconds: attempt == 0 ? 500 : 1200),
      );
    }
    return false;
  }

  Future<void> _handlePurchaseUpdates(List<PurchaseDetails> purchases) async {
    for (final purchase in purchases) {
      switch (purchase.status) {
        case PurchaseStatus.pending:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: purchase.productID,
              message: 'عملية الشراء معلّقة لدى Google Play.',
            );
          }
          break;
        case PurchaseStatus.error:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: null,
              error: purchase.error?.message ?? 'فشلت عملية الشراء.',
            );
          }
          break;
        case PurchaseStatus.canceled:
          if (mounted) {
            state = state.copyWith(
              purchasingProductId: null,
              message: 'تم إلغاء عملية الشراء.',
            );
          }
          break;
        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          await _verifyAndComplete(purchase);
          break;
      }
    }
  }

  Future<void> _verifyAndComplete(PurchaseDetails purchase) async {
    if (!Platform.isAndroid) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: 'التحقق الحالي يدعم مشتريات Google Play فقط.',
        );
      }
      return;
    }
    final purchaseToken = purchase.verificationData.serverVerificationData;
    if (purchaseToken.isEmpty) {
      state = state.copyWith(
        purchasingProductId: null,
        error: 'Google Play لم يرجع رمز تحقق صالحًا.',
      );
      return;
    }

    try {
      final result = await _repository.verifyGooglePlayPurchase(
        productId: purchase.productID,
        purchaseToken: purchaseToken,
      );
      if (!result.entitlementGranted) {
        throw StateError('السيرفر لم يؤكد استحقاق المنتج.');
      }
      if (purchase.pendingCompletePurchase) {
        await _store.completePurchase(purchase);
      }
      await _onEntitlementChanged();
      final updatedStatus = await _repository.getStatus();
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          status: updatedStatus,
          message: result.idempotent
              ? 'تمت استعادة الاستحقاق المسجل سابقًا.'
              : 'تم التحقق من الشراء وتحديث حسابك بنجاح.',
        );
      }
    } on Object catch (error) {
      if (mounted) {
        state = state.copyWith(
          purchasingProductId: null,
          error: error.toString(),
        );
      }
    }
  }

  void _handlePurchaseStreamError(Object error) {
    if (mounted) {
      state = state.copyWith(
        purchasingProductId: null,
        error: error.toString(),
      );
    }
  }

  @override
  void dispose() {
    unawaited(_purchaseSubscription.cancel());
    super.dispose();
  }
}

final inAppPurchaseProvider = Provider<InAppPurchase>((ref) {
  return InAppPurchase.instance;
});

final rewardedAdGatewayProvider = Provider<RewardedAdGateway>((ref) {
  return GoogleRewardedAdGateway(ref.watch(monetizationRepositoryProvider));
});

final monetizationControllerProvider =
    StateNotifierProvider.autoDispose<
      MonetizationController,
      MonetizationState
    >((ref) {
      return MonetizationController(
        repository: ref.watch(monetizationRepositoryProvider),
        store: ref.watch(inAppPurchaseProvider),
        rewardedAdGateway: ref.watch(rewardedAdGatewayProvider),
        onEntitlementChanged: () async {
          ref.invalidate(walletSummaryProvider);
          await ref.read(sessionControllerProvider.notifier).refreshProfile();
        },
      );
    });
