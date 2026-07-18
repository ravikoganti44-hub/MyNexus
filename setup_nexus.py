"""
MyNexus v1.1.0 — Initial Setup Script
Run this once after first launch to populate the app with sample data.

What this sets up:
  - 28 Financial Connected Applications (Banks, Credit Cards, Insurance, Utilities)
  - 29 Recurring Financial Activities (Bills, Payments, Maintenance, Subscriptions)
  - 1 Sample Net Worth Snapshot (starting baseline with placeholder values)
  - 1 Sample Budget Period with common spending category limits
"""

import sys
import os
from datetime import datetime, date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _add_sample_net_worth():
    """Create a starter net worth snapshot with common placeholder categories."""
    from src.database.config import get_session
    from src.database.operations import NetWorthManager

    session = get_session()
    try:
        # Skip if snapshots already exist
        existing = NetWorthManager.get_all_snapshots(session)
        if existing:
            print("  - Net worth snapshots already exist, skipping.")
            return

        assets = {
            "Checking Account":          5_000,
            "Savings / Emergency Fund":  10_000,
            "Retirement 401k":           35_000,
            "Investments / Stocks":       8_000,
            "Vehicle (estimated value)": 18_000,
        }
        liabilities = {
            "Car Loan":       12_000,
            "Credit Card 1":   2_500,
            "Student Loan":   22_000,
        }
        NetWorthManager.create_snapshot(
            session,
            assets,
            liabilities,
            notes="Initial baseline snapshot — update with your real figures",
            snapshot_date=datetime.now(),
        )
        nw = sum(assets.values()) - sum(liabilities.values())
        print(f"  + Sample net worth snapshot created  (baseline NW: ${nw:,.0f})")
    finally:
        session.close()


def _add_sample_budget():
    """Create a starter monthly budget period with common category limits."""
    from src.database.config import get_session
    from src.database.operations import BudgetManager

    session = get_session()
    try:
        existing = session.execute(
            __import__('sqlalchemy').text("SELECT COUNT(*) FROM budget_periods")
        ).scalar()
        if existing:
            print("  - Budget periods already exist, skipping.")
            return
    except Exception:
        pass
    finally:
        session.close()

    # BudgetManager handles its own session internally for create calls
    try:
        session2 = get_session()
        today = date.today()
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end = today.replace(month=today.month + 1, day=1)

        from src.database.models import BudgetPeriod
        period = BudgetPeriod(
            name=f"Budget — {start.strftime('%B %Y')}",
            start_date=datetime.combine(start, datetime.min.time()),
            end_date=datetime.combine(end, datetime.min.time()),
        )
        session2.add(period)
        session2.commit()

        from src.database.models import BudgetLimit
        default_limits = [
            ("Groceries",       600),
            ("Dining Out",      300),
            ("Transportation",  250),
            ("Utilities",       200),
            ("Entertainment",   150),
            ("Health & Medical",200),
            ("Subscriptions",   100),
            ("Clothing",        150),
            ("Savings",         500),
            ("Miscellaneous",   200),
        ]
        for category, amount in default_limits:
            bl = BudgetLimit(
                period_id=period.id,
                category=category,
                limit_amount=float(amount),
            )
            session2.add(bl)
        session2.commit()
        session2.close()
        print(f"  + Sample budget created for {start.strftime('%B %Y')} "
              f"with {len(default_limits)} category limits")
    except Exception as e:
        print(f"  ! Budget setup skipped ({e})")


def setup_nexus():
    """Run complete first-time setup for MyNexus v1.1.0."""
    print("\n" + "=" * 70)
    print("  MyNexus v1.1.0 - First-Time Setup")
    print("=" * 70)
    print("\nThis will populate your MyNexus with:")
    print("  - 28 Financial Connected Applications")
    print("  - 29 Recurring Financial Activities & Reminders")
    print("  - 1  Starter Net Worth Snapshot (baseline)")
    print("  - 1  Monthly Budget with 10 category limits")
    print("\nStarting setup...\n")

    try:
        # Step 1: Connected applications
        print("Step 1: Adding Financial Application Templates...")
        print("-" * 70)
        from add_sample_apps import add_sample_apps
        add_sample_apps()

        # Step 2: Activities & reminders
        print("\nStep 2: Adding Financial Activities & Reminders...")
        print("-" * 70)
        from add_sample_activities import add_sample_activities
        add_sample_activities()

        # Step 3: Net worth baseline snapshot
        print("\nStep 3: Creating Starter Net Worth Snapshot...")
        print("-" * 70)
        _add_sample_net_worth()

        # Step 4: Budget period
        print("\nStep 4: Creating Starter Budget Period...")
        print("-" * 70)
        _add_sample_budget()

        print("\n" + "=" * 70)
        print("  SETUP COMPLETE!")
        print("=" * 70)
        print("""
  Your MyNexus is now ready:

  Connected Apps   28 financial application templates
  Activities       29 recurring bills, payments & reminders
  Net Worth        Starter snapshot — edit with your real balances
  Budget           This month's budget with 10 spending categories

  Next steps:
    1. Open the app:  python app.py
    2. Go to Connected Apps  -> update with your real account details
    3. Go to Net Worth       -> click New Snapshot, values pre-filled,
                                update each figure to match reality
    4. Go to Budget Tracker  -> adjust category limits to your lifestyle
    5. Go to Settings        -> enable notifications & reminders
""")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n  Setup Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    success = setup_nexus()
    sys.exit(0 if success else 1)
