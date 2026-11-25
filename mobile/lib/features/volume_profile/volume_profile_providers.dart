import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'volume_profile_models.dart';
import 'volume_profile_repository.dart';

/// حجم السعر (POC/منطقة القيمة) لسهم واحد.
final volumeProfileProvider = FutureProvider.autoDispose
    .family<StockVolumeProfileSnapshot, String>((ref, ticker) {
      return ref.watch(volumeProfileRepositoryProvider).volumeProfile(ticker);
    });
