"""
MyNexus - First-Run Sample Data Seeder
---------------------------------------
Seeds demonstration data for ALL features on a FRESH install only.
If the user already has data (prior version), nothing is overwritten.

Features covered:
  - My Activities (recurring bills, subscriptions, tasks)
  - Connected Apps (banking, mortgage, insurance, utilities)
  - Document Vault (metadata entries - no real files needed)
  - Integrations (email services)
"""

import os
import sys

# Ensure project root is on the path when called from installer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────────────────────────
# Per-feature guards: each table is checked independently
# ─────────────────────────────────────────────────────────────────────────────

def _table_has_data(session, model) -> bool:
    """Return True if the given model's table already has rows."""
    try:
        return session.query(model).count() > 0
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Activities
# ─────────────────────────────────────────────────────────────────────────────

def _seed_activities(session):
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta
    from src.database.models import Activity, RecurrenceType, CategoryType

    now = datetime.now()
    month_start = now.replace(day=1)

    activities = [
        # ── Monthly payments ──
        Activity(
            title="Mortgage Payment",
            description="Monthly mortgage payment – update the amount to match your statement.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=month_start + relativedelta(months=1),
            reminder_days_before=3,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Rent Payment",
            description="Monthly rent – edit or delete this if you own your home.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=month_start + relativedelta(months=1),
            reminder_days_before=3,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Credit Card Payment",
            description="Pay your primary credit card statement balance.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now + timedelta(days=10),
            reminder_days_before=2,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Electric Bill",
            description="Monthly electricity bill – connect to your utility account.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now.replace(day=15) if now.day < 15 else now.replace(day=15) + relativedelta(months=1),
            reminder_days_before=3,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Internet & Cable Bill",
            description="Monthly broadband/cable service payment.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now.replace(day=20) if now.day < 20 else now.replace(day=20) + relativedelta(months=1),
            reminder_days_before=2,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Gas / Water Bill",
            description="Utility bills – split into separate activities if needed.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now.replace(day=10) if now.day < 10 else now.replace(day=10) + relativedelta(months=1),
            reminder_days_before=2,
            send_notification=True,
            is_active=True,
        ),
        # ── Subscriptions ──
        Activity(
            title="Netflix Subscription",
            description="Monthly streaming subscription. Edit amount in description.",
            category=CategoryType.SUBSCRIPTION,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now + timedelta(days=5),
            reminder_days_before=1,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Gym Membership",
            description="Monthly gym or fitness club membership fee.",
            category=CategoryType.SUBSCRIPTION,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=month_start + relativedelta(months=1),
            reminder_days_before=1,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Amazon Prime / Cloud Storage",
            description="Annual or monthly subscription renewal.",
            category=CategoryType.SUBSCRIPTION,
            recurrence_type=RecurrenceType.YEARLY,
            start_date=now,
            next_due_date=now + relativedelta(years=1),
            reminder_days_before=7,
            send_notification=True,
            is_active=True,
        ),
        # ── Yearly / Insurance ──
        Activity(
            title="Auto Insurance Renewal",
            description="Annual car insurance policy renewal – shop for quotes 30 days early.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.YEARLY,
            start_date=now,
            next_due_date=now + relativedelta(years=1),
            reminder_days_before=30,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Home / Renters Insurance",
            description="Annual property insurance renewal.",
            category=CategoryType.PAYMENT,
            recurrence_type=RecurrenceType.YEARLY,
            start_date=now,
            next_due_date=now + relativedelta(years=1),
            reminder_days_before=30,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Annual Tax Filing",
            description="Reminder to file federal and state income tax returns.",
            category=CategoryType.TASK,
            recurrence_type=RecurrenceType.YEARLY,
            start_date=now,
            next_due_date=now.replace(month=4, day=15) if now.month < 4 or (now.month == 4 and now.day < 15) else now.replace(month=4, day=15) + relativedelta(years=1),
            reminder_days_before=30,
            send_notification=True,
            is_active=True,
        ),
        # ── Maintenance / Health ──
        Activity(
            title="Car Oil Change",
            description="Regular vehicle maintenance – every 3 months or 5,000 miles.",
            category=CategoryType.MAINTENANCE,
            recurrence_type=RecurrenceType.QUARTERLY,
            start_date=now,
            next_due_date=now + relativedelta(months=3),
            reminder_days_before=7,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Dental Check-up",
            description="Bi-annual dental cleaning and examination.",
            category=CategoryType.HEALTH,
            recurrence_type=RecurrenceType.MONTHLY,
            start_date=now,
            next_due_date=now + relativedelta(months=6),
            reminder_days_before=14,
            send_notification=True,
            is_active=True,
        ),
        Activity(
            title="Annual Physical / Doctor Visit",
            description="Yearly wellness checkup with primary care physician.",
            category=CategoryType.HEALTH,
            recurrence_type=RecurrenceType.YEARLY,
            start_date=now,
            next_due_date=now + relativedelta(years=1),
            reminder_days_before=14,
            send_notification=True,
            is_active=True,
        ),
    ]

    session.bulk_save_objects(activities)
    print(f"  ✓ Added {len(activities)} sample activities")


# ─────────────────────────────────────────────────────────────────────────────
# Connected Applications
# ─────────────────────────────────────────────────────────────────────────────

def _seed_connected_apps(session):
    from src.database.models import ConnectedApplication

    apps = [
        # ── Banking ──
        ConnectedApplication(
            name="Primary Checking Account",
            app_type="banking",
            app_name="Chase Bank",
            category="banking",
            website_url="https://www.chase.com",
            login_url="https://secure06a.chase.com/id/client/login",
            username="your.email@example.com",
            account_number="****1234",
            account_holder="Your Name",
            icon_emoji="🏦",
            notes="Edit this entry with your real credentials. Login URL opens the bank's sign-in page.",
            is_active=True,
        ),
        ConnectedApplication(
            name="Savings Account",
            app_type="banking",
            app_name="Bank of America",
            category="banking",
            website_url="https://www.bankofamerica.com",
            login_url="https://www.bankofamerica.com/login",
            username="your.email@example.com",
            account_number="****5678",
            account_holder="Your Name",
            icon_emoji="🏦",
            notes="High-yield savings – update account number and credentials.",
            is_active=True,
        ),
        # ── Credit Cards ──
        ConnectedApplication(
            name="Primary Credit Card",
            app_type="credit_card",
            app_name="Chase Sapphire",
            category="credit_card",
            website_url="https://www.chase.com/personal/credit-cards",
            login_url="https://creditcards.chase.com/login",
            username="your.email@example.com",
            account_number="****1111",
            account_holder="Your Name",
            icon_emoji="💳",
            notes="Replace with your actual card details. Click 'Connect' to open the login page.",
            is_active=True,
        ),
        ConnectedApplication(
            name="Rewards Credit Card",
            app_type="credit_card",
            app_name="American Express",
            category="credit_card",
            website_url="https://www.americanexpress.com",
            login_url="https://myca.americanexpress.com",
            username="your.email@example.com",
            account_number="****2222",
            account_holder="Your Name",
            icon_emoji="💳",
            notes="AmEx Gold / Platinum – update with your real account info.",
            is_active=True,
        ),
        # ── Mortgage ──
        ConnectedApplication(
            name="Home Mortgage",
            app_type="mortgage",
            app_name="Your Mortgage Servicer",
            category="mortgage",
            website_url="https://www.example-mortgage.com",
            login_url="https://www.example-mortgage.com/login",
            username="your.email@example.com",
            account_number="MG-000000000",
            account_holder="Your Name",
            icon_emoji="🏠",
            notes="Update with your lender's URL and account number. Payment due date: 1st of month.",
            is_active=True,
        ),
        # ── Insurance ──
        ConnectedApplication(
            name="Auto Insurance",
            app_type="insurance",
            app_name="Geico / Your Insurer",
            category="insurance",
            website_url="https://www.geico.com",
            login_url="https://login.geico.com",
            username="your.email@example.com",
            account_number="AUTO-0000000",
            account_holder="Your Name",
            icon_emoji="🚗",
            notes="Replace with your actual auto insurance provider and policy number.",
            is_active=True,
        ),
        ConnectedApplication(
            name="Home / Renters Insurance",
            app_type="insurance",
            app_name="State Farm / Your Insurer",
            category="insurance",
            website_url="https://www.statefarm.com",
            login_url="https://www.statefarm.com/auth/login",
            username="your.email@example.com",
            account_number="HOME-0000000",
            account_holder="Your Name",
            icon_emoji="🏡",
            notes="Update with your home/renters insurance provider.",
            is_active=True,
        ),
        # ── Utilities ──
        ConnectedApplication(
            name="Electric Company",
            app_type="utilities",
            app_name="Duke Energy / Your Provider",
            category="utilities",
            website_url="https://www.duke-energy.com",
            login_url="https://www.duke-energy.com/home/account-tools/login",
            username="your.email@example.com",
            account_number="ELEC-0000000",
            account_holder="Your Name",
            icon_emoji="⚡",
            notes="Replace with your actual electricity provider and account number.",
            is_active=True,
        ),
        ConnectedApplication(
            name="Internet Service",
            app_type="utilities",
            app_name="Xfinity / Your Provider",
            category="utilities",
            website_url="https://www.xfinity.com",
            login_url="https://login.xfinity.com/login",
            username="your.email@example.com",
            account_number="INET-0000000",
            account_holder="Your Name",
            icon_emoji="🌐",
            notes="Update with your ISP details. Monthly billing auto-pay recommended.",
            is_active=True,
        ),
        # ── Investment / Retirement ──
        ConnectedApplication(
            name="Investment / 401(k)",
            app_type="investment",
            app_name="Fidelity / Vanguard",
            category="investment",
            website_url="https://www.fidelity.com",
            login_url="https://login.fidelity.com/ftgw/Fas/fidelity/RtlPublic/login",
            username="your.email@example.com",
            account_number="INV-0000000",
            account_holder="Your Name",
            icon_emoji="📈",
            notes="Track your retirement or brokerage account here. Review quarterly.",
            is_active=True,
        ),
    ]

    session.bulk_save_objects(apps)
    print(f"  ✓ Added {len(apps)} sample connected applications")


# ─────────────────────────────────────────────────────────────────────────────
# Integrations
# ─────────────────────────────────────────────────────────────────────────────

def _seed_integrations(session):
    from src.database.models import Integration

    integrations = [
        Integration(
            name="Personal Email (Gmail)",
            app_type="email",
            username="your.email@gmail.com",
            is_active=True,
            config_data='{"provider": "gmail", "note": "Used for activity notifications"}',
        ),
        Integration(
            name="Work Email (Outlook)",
            app_type="email",
            username="your.name@company.com",
            is_active=True,
            config_data='{"provider": "outlook", "note": "Work calendar sync placeholder"}',
        ),
    ]

    session.bulk_save_objects(integrations)
    print(f"  ✓ Added {len(integrations)} sample integrations")


# ─────────────────────────────────────────────────────────────────────────────
# Document Vault (metadata placeholders – no actual files)
# ─────────────────────────────────────────────────────────────────────────────

def _seed_documents(session):
    """
    Add metadata placeholders so the vault has example rows.
    file_path points to a readme inside the install folder – safe to keep.
    """
    from datetime import datetime
    from pathlib import Path
    from dateutil.relativedelta import relativedelta
    from src.database.models import Document, DocumentCategory, DocumentType

    example_dir = os.path.join(Path.home(), '.mynexus', 'data', 'documents')
    os.makedirs(example_dir, exist_ok=True)
    readme_path = os.path.join(example_dir, 'EXAMPLE_README.txt')

    # Write a small readme so the file_path is valid
    if not os.path.exists(readme_path):
        with open(readme_path, 'w') as f:
            f.write(
                "MyNexus Document Vault – Example Entry\n\n"
                "This file was created as a placeholder during installation.\n"
                "You can safely delete this file and its database entry.\n\n"
                "To add real documents, click '+ Upload Document' in the Document Vault.\n"
            )

    now = datetime.now()

    docs = [
        Document(
            original_filename="Passport_Example.pdf",
            stored_filename="example_passport_001.txt",
            file_path=readme_path,
            file_size=512,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            title="My Passport (Example)",
            description="Replace this with your actual passport scan. Never share this file.",
            category=DocumentCategory.PASSPORT,
            sub_category="US Passport",
            issue_date=now - relativedelta(years=2),
            expiry_date=now + relativedelta(years=8),
            reference_number="PASS-EXAMPLE-001",
            is_favorite=False,
            is_archived=False,
            notes="This is a placeholder. Upload your real passport copy and delete this entry.",
        ),
        Document(
            original_filename="Tax_Return_2024_Example.pdf",
            stored_filename="example_tax_2024_001.txt",
            file_path=readme_path,
            file_size=1024,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            title="2024 Tax Return (Example)",
            description="Placeholder for your annual federal/state tax return documents.",
            category=DocumentCategory.TAX_DOCUMENTS,
            sub_category="2024",
            issue_date=now.replace(month=4, day=15),
            expiry_date=None,
            reference_number="TAX-EXAMPLE-2024",
            is_favorite=True,
            is_archived=False,
            notes="Recommended: keep 7 years of tax returns. Upload your real files here.",
        ),
        Document(
            original_filename="Insurance_Policy_Example.pdf",
            stored_filename="example_insurance_001.txt",
            file_path=readme_path,
            file_size=768,
            file_type=DocumentType.TEXT,
            mime_type="text/plain",
            title="Auto Insurance Policy (Example)",
            description="Placeholder for your auto insurance policy document.",
            category=DocumentCategory.INSURANCE_DOCUMENTS,
            sub_category="Auto",
            issue_date=now - relativedelta(months=6),
            expiry_date=now + relativedelta(months=6),
            reference_number="INS-EXAMPLE-AUTO",
            is_favorite=False,
            is_archived=False,
            notes="Replace with your actual policy PDF. Set an expiry date for renewal reminders.",
        ),
    ]

    session.bulk_save_objects(docs)
    print(f"  ✓ Added {len(docs)} sample document vault entries")


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def seed_sample_data(force: bool = False) -> bool:
    """
    Seed sample data into the database.

    Parameters
    ----------
    force : bool
        If True, skip the "already seeded" guard and always seed.
        Use only for development / testing.

    Returns True on success, False on error.
    """
    from pathlib import Path
    from src.database.config import get_session, init_db

    print("\n" + "=" * 70)
    print("  MyNexus – First-Run Sample Data Setup")
    print("=" * 70)

    # Initialise tables in case this is the very first run
    init_db()

    session = get_session()
    try:
        from src.database.models import Activity, ConnectedApplication, Document, Integration

        # When forcing, clear existing rows so unique constraints don't fire
        if force:
            for model in (Activity, ConnectedApplication, Document, Integration):
                session.query(model).delete()
            session.flush()

        seeded_any = False
        skipped_any = False

        print("\n  Seeding demonstration data …\n")

        if force or not _table_has_data(session, Activity):
            _seed_activities(session)
            seeded_any = True
        else:
            print("  – Activities: existing data found, skipping")
            skipped_any = True

        if force or not _table_has_data(session, ConnectedApplication):
            _seed_connected_apps(session)
            seeded_any = True
        else:
            print("  – Connected Apps: existing data found, skipping")
            skipped_any = True

        if force or not _table_has_data(session, Integration):
            _seed_integrations(session)
            seeded_any = True
        else:
            print("  – Integrations: existing data found, skipping")
            skipped_any = True

        if force or not _table_has_data(session, Document):
            _seed_documents(session)
            seeded_any = True
        else:
            print("  – Document Vault: existing data found, skipping")
            skipped_any = True

        if not seeded_any:
            print("\n  ✓ All features already have data – nothing was changed.")
            print("    (Run with --force to re-seed everything.)\n")
            return True

        session.commit()

        print("\n" + "=" * 70)
        print("  \u2705 Sample data setup complete!")
        if skipped_any:
            print("  (Features with existing data were skipped to preserve your data.)")
        print("=" * 70)
        print("""
  What was added for empty features:
    • 15 recurring activities (bills, subscriptions, maintenance)
    • 10 connected application templates (banking, mortgage, insurance …)
    •  2 email integration placeholders
    •  3 document vault example entries

  Next steps:
    1. Open each Connected App and replace placeholder credentials
    2. Delete or edit activities that don't apply to you
    3. Upload your real documents to the Document Vault
    4. Enable notifications in Settings → Notifications
""")
        return True

    except Exception as exc:
        session.rollback()
        print(f"\n  ❌ Seeding error: {exc}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()


if __name__ == '__main__':
    force_flag = '--force' in sys.argv
    ok = seed_sample_data(force=force_flag)
    sys.exit(0 if ok else 1)
