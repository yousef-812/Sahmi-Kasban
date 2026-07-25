from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text()
    if old not in text:
        if new in text:
            return
        raise SystemExit(f"Expected text was not found in {path}")
    target.write_text(text.replace(old, new, 1))


replace_once(
    "backend/app/core/config.py",
    'google_play_package_name: str = "com.sahmikasban.app"',
    'google_play_package_name: str = "com.sahmikasban.sahmi_kasban_mobile"',
)

replace_once(
    "backend/app/services/monetization.py",
    """    current_settings = settings or get_settings()
    now = moment or datetime.now(UTC)
    eligibility = rewarded_ad_eligibility(
""",
    """    current_settings = settings or get_settings()
    if current_settings.admob_ssv_verification_mode == "disabled":
        raise RewardedAdsUnavailableError("verification_disabled")
    now = moment or datetime.now(UTC)
    eligibility = rewarded_ad_eligibility(
""",
)

controller_path = Path(
    "mobile/lib/features/monetization/monetization_controller.dart"
)
controller = controller_path.read_text()
for old, new in (
    (
        """            );
          }
        case PurchaseStatus.error:
""",
        """            );
          }
          break;
        case PurchaseStatus.error:
""",
    ),
    (
        """            );
          }
        case PurchaseStatus.canceled:
""",
        """            );
          }
          break;
        case PurchaseStatus.canceled:
""",
    ),
    (
        """            );
          }
        case PurchaseStatus.purchased:
""",
        """            );
          }
          break;
        case PurchaseStatus.purchased:
""",
    ),
    (
        """        case PurchaseStatus.restored:
          await _verifyAndComplete(purchase);
      }
""",
        """        case PurchaseStatus.restored:
          await _verifyAndComplete(purchase);
          break;
      }
""",
    ),
):
    if old in controller:
        controller = controller.replace(old, new, 1)
controller_path.write_text(controller)

replace_once(
    "mobile/lib/features/home/dashboard_screen.dart",
    """                    OutlinedButton.icon(
                      onPressed: () => context.push('/wallet/history'),
                      icon: const Icon(Icons.receipt_long_outlined),
                      label: const Text('عرض سجل العمليات'),
                    ),
""",
    """                    OutlinedButton.icon(
                      onPressed: () => context.push('/wallet/history'),
                      icon: const Icon(Icons.receipt_long_outlined),
                      label: const Text('عرض سجل العمليات'),
                    ),
                    const SizedBox(height: 10),
                    FilledButton.icon(
                      onPressed: () => context.push('/monetization'),
                      icon: const Icon(Icons.workspace_premium_outlined),
                      label: const Text('الخطط وشراء العملات'),
                    ),
""",
)
