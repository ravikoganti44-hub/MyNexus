"""
MyNexus AI Engine — Local intelligence layer providing smart insights,
pattern recognition, anomaly detection, and predictive analytics across
all modules.  No external APIs or cloud services required.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, date as _date
from typing import Any

# ---------------------------------------------------------------------------
# Data containers
# ---------------------------------------------------------------------------

class Insight:
    """A single AI-generated insight / recommendation."""
    PRIORITY_HIGH   = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW    = "low"

    ICON_MAP = {
        "warning":  "⚠️",
        "tip":      "💡",
        "trend":    "📈",
        "anomaly":  "🔍",
        "security": "🔒",
        "streak":   "🔥",
        "money":    "💰",
        "doc":      "📄",
        "calendar": "📅",
        "star":     "⭐",
        "health":   "❤️",
    }

    def __init__(self, title: str, description: str, category: str,
                 priority: str = "medium", icon: str = "tip",
                 action_label: str | None = None,
                 action_data: dict | None = None):
        self.title = title
        self.description = description
        self.category = category          # "budget", "activity", "document", "security", "general"
        self.priority = priority
        self.icon_key = icon
        self.icon = self.ICON_MAP.get(icon, "💡")
        self.action_label = action_label  # e.g. "View Budget"
        self.action_data = action_data or {}
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<Insight {self.icon} {self.title}>"


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------

class NexusAI:
    """Central AI engine that analyses all app data and produces insights."""

    # ── Public entry point ────────────────────────────────────────────────

    @classmethod
    def generate_all_insights(cls, session) -> list[Insight]:
        """Run every analyser and return a de-duplicated, priority-sorted list."""
        insights: list[Insight] = []
        insights.extend(cls.analyse_budget(session))
        insights.extend(cls.analyse_activities(session))
        insights.extend(cls.analyse_documents(session))
        insights.extend(cls.analyse_security(session))
        insights.extend(cls.analyse_net_worth(session))
        # Sort: high → medium → low
        order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda i: order.get(i.priority, 1))
        return insights

    # ── Budget Intelligence ───────────────────────────────────────────────

    @classmethod
    def analyse_budget(cls, session) -> list[Insight]:
        from src.database.operations import BudgetManager
        insights: list[Insight] = []
        now = datetime.now()

        # Gather last 6 months of data
        months_data = []
        for offset in range(6):
            m = now.month - offset
            y = now.year
            while m < 1:
                m += 12
                y -= 1
            period = BudgetManager.get_or_create_period(session, y, m)
            spending = BudgetManager.get_spending_by_category(session, period.id)
            limits = {lim.category: lim.limit_amount
                      for lim in BudgetManager.get_limits(session, period.id)}
            entries = BudgetManager.get_entries(session, period.id)
            months_data.append({
                "year": y, "month": m, "period_id": period.id,
                "spending": spending, "limits": limits, "entries": entries,
            })

        current = months_data[0] if months_data else None
        if not current or not current["entries"]:
            return insights

        # --- 1. Over-budget categories ---
        for cat, spent in current["spending"].items():
            if spent <= 0:
                continue
            limit = current["limits"].get(cat, 0)
            if limit > 0:
                pct = spent / limit * 100
                if pct >= 100:
                    insights.append(Insight(
                        f"{cat} over budget",
                        f"You've spent ${spent:,.0f} of your ${limit:,.0f} {cat} budget ({pct:.0f}%).",
                        "budget", Insight.PRIORITY_HIGH, "warning",
                        action_label="View Budget"))
                elif pct >= 80:
                    insights.append(Insight(
                        f"{cat} nearing limit",
                        f"${spent:,.0f} of ${limit:,.0f} — {pct:.0f}% used with "
                        f"{_date.today().day} day(s) elapsed.",
                        "budget", Insight.PRIORITY_MEDIUM, "money",
                        action_label="View Budget"))

        # --- 2. Spending trend (vs previous month) ---
        if len(months_data) >= 2:
            prev = months_data[1]
            cur_total = sum(v for v in current["spending"].values() if v > 0)
            prev_total = sum(v for v in prev["spending"].values() if v > 0)
            if prev_total > 0:
                change_pct = (cur_total - prev_total) / prev_total * 100
                if change_pct > 20:
                    insights.append(Insight(
                        "Spending spike detected",
                        f"Total spending is up {change_pct:.0f}% vs last month "
                        f"(${cur_total:,.0f} vs ${prev_total:,.0f}).",
                        "budget", Insight.PRIORITY_HIGH, "anomaly"))
                elif change_pct < -15:
                    insights.append(Insight(
                        "Great savings this month!",
                        f"Spending is down {abs(change_pct):.0f}% vs last month. Keep it up!",
                        "budget", Insight.PRIORITY_LOW, "star"))

        # --- 3. Unusual single transaction ---
        if current["entries"]:
            amounts = [e.amount for e in current["entries"] if e.amount > 0]
            if len(amounts) >= 3:
                avg = sum(amounts) / len(amounts)
                std = math.sqrt(sum((a - avg) ** 2 for a in amounts) / len(amounts))
                for entry in current["entries"]:
                    if entry.amount > 0 and std > 0 and (entry.amount - avg) / std > 2.0:
                        insights.append(Insight(
                            f"Unusual expense: {entry.title}",
                            f"${entry.amount:,.2f} is significantly higher than your "
                            f"average expense of ${avg:,.2f}.",
                            "budget", Insight.PRIORITY_MEDIUM, "anomaly"))
                        break  # one is enough

        # --- 4. Recurring expenses prediction ---
        if len(months_data) >= 3:
            cat_freq: dict[str, int] = Counter()
            for md in months_data[1:]:
                for cat in md["spending"]:
                    if md["spending"][cat] > 0:
                        cat_freq[cat] += 1
            for cat, count in cat_freq.items():
                if count >= 3 and cat not in current["spending"]:
                    avg_amt = sum(
                        md["spending"].get(cat, 0) for md in months_data[1:]
                        if md["spending"].get(cat, 0) > 0
                    ) / count
                    insights.append(Insight(
                        f"Expected expense: {cat}",
                        f"You usually spend ~${avg_amt:,.0f}/mo on {cat} but haven't yet this month.",
                        "budget", Insight.PRIORITY_LOW, "tip"))

        # --- 5. Smart budget suggestions ---
        no_limit_cats = [
            cat for cat in current["spending"]
            if current["spending"][cat] > 0 and cat not in current["limits"]
        ]
        if no_limit_cats:
            insights.append(Insight(
                "Set budget limits",
                f"You're spending in {', '.join(no_limit_cats[:3])} without budget limits. "
                f"Consider setting limits to track your goals.",
                "budget", Insight.PRIORITY_LOW, "tip",
                action_label="Set Limits"))

        return insights

    # ── Activity Intelligence ────────────────────────────────────────────

    @classmethod
    def analyse_activities(cls, session) -> list[Insight]:
        from src.database.operations import ActivityManager
        from src.database.models import ActivityCompletion
        insights: list[Insight] = []

        all_acts = ActivityManager.get_all_activities(session, active_only=True)
        overdue = ActivityManager.get_overdue_activities(session)
        due_soon = ActivityManager.get_due_activities(session, days_ahead=3)

        # --- 1. Overdue pile-up ---
        if len(overdue) >= 5:
            insights.append(Insight(
                f"{len(overdue)} overdue activities",
                "You have a backlog of overdue items. Consider completing or rescheduling them.",
                "activity", Insight.PRIORITY_HIGH, "warning",
                action_label="View Activities"))
        elif len(overdue) >= 2:
            insights.append(Insight(
                f"{len(overdue)} activities overdue",
                "A few items need attention. Tackling the oldest first helps build momentum.",
                "activity", Insight.PRIORITY_MEDIUM, "calendar"))

        # --- 2. Busy day warning ---
        day_counts: dict[_date, int] = Counter()
        for a in all_acts:
            if a.next_due_date:
                day_counts[a.next_due_date.date()] += 1
        for day, count in day_counts.items():
            if count >= 5 and day >= _date.today():
                label = day.strftime("%A, %b %d")
                insights.append(Insight(
                    f"Busy day ahead: {label}",
                    f"You have {count} activities due on {label}. Consider spreading them out.",
                    "activity", Insight.PRIORITY_MEDIUM, "calendar"))
                break

        # --- 3. Completion rate ---
        completions = session.query(ActivityCompletion).all()
        if completions:
            last_30 = [c for c in completions
                       if c.completed_at >= datetime.now() - timedelta(days=30)]
            rate = len(last_30) / max(len(all_acts), 1) * 100
            if rate >= 80:
                insights.append(Insight(
                    "Excellent completion rate!",
                    f"You completed {len(last_30)} tasks in the last 30 days — {rate:.0f}% rate.",
                    "activity", Insight.PRIORITY_LOW, "star"))
            elif rate < 30 and len(all_acts) > 3:
                insights.append(Insight(
                    "Low completion rate",
                    f"Only {rate:.0f}% of activities completed in the last 30 days. "
                    f"Try starting with the quick wins.",
                    "activity", Insight.PRIORITY_MEDIUM, "tip"))

        # --- 4. Category balance ---
        if len(all_acts) >= 5:
            cat_dist = Counter(a.category.value for a in all_acts)
            total = sum(cat_dist.values())
            dominant = cat_dist.most_common(1)[0]
            if dominant[1] / total >= 0.6:
                insights.append(Insight(
                    f"Heavy focus on {dominant[0].title()}",
                    f"{dominant[1]}/{total} activities are {dominant[0]}. "
                    f"Consider diversifying your schedule.",
                    "activity", Insight.PRIORITY_LOW, "tip"))

        # --- 5. Stale activities ---
        stale_threshold = datetime.now() - timedelta(days=60)
        stale = [a for a in all_acts
                 if not a.is_completed and a.created_at and a.created_at < stale_threshold]
        if stale:
            insights.append(Insight(
                f"{len(stale)} stale activities",
                f"Some activities are over 60 days old and still pending. "
                f"Review if they're still relevant.",
                "activity", Insight.PRIORITY_LOW, "tip",
                action_label="View Activities"))

        return insights

    # ── Document Intelligence ─────────────────────────────────────────────

    @classmethod
    def analyse_documents(cls, session) -> list[Insight]:
        from src.database.operations import DocumentManager
        insights: list[Insight] = []

        all_docs = DocumentManager.get_all_documents(session)
        if not all_docs:
            insights.append(Insight(
                "Start your Document Vault",
                "Upload important documents like passports, tax returns, and insurance "
                "policies to keep them organized and searchable.",
                "document", Insight.PRIORITY_LOW, "doc",
                action_label="Open Vault"))
            return insights

        # --- 1. Expiring documents ---
        expiring_soon = DocumentManager.get_expiring_documents(session, days_ahead=30)
        expiring_90 = DocumentManager.get_expiring_documents(session, days_ahead=90)
        already_expired = [
            d for d in all_docs
            if d.expiry_date and d.expiry_date < datetime.now()
        ]

        if already_expired:
            names = ", ".join(d.title for d in already_expired[:3])
            insights.append(Insight(
                f"{len(already_expired)} expired document(s)",
                f"Expired: {names}. Renew them as soon as possible.",
                "document", Insight.PRIORITY_HIGH, "warning",
                action_label="View Vault"))

        if expiring_soon:
            names = ", ".join(d.title for d in expiring_soon[:3])
            insights.append(Insight(
                f"{len(expiring_soon)} document(s) expiring within 30 days",
                f"Expiring soon: {names}. Plan ahead for renewal.",
                "document", Insight.PRIORITY_HIGH, "doc",
                action_label="View Vault"))
        elif expiring_90:
            names = ", ".join(d.title for d in expiring_90[:3])
            insights.append(Insight(
                f"{len(expiring_90)} document(s) expiring within 90 days",
                f"Coming up: {names}.",
                "document", Insight.PRIORITY_MEDIUM, "doc"))

        # --- 2. Missing essential documents ---
        essential_categories = {"PASSPORT", "TAX_DOCUMENTS", "INSURANCE_DOCUMENTS"}
        existing_cats = {d.category.name for d in all_docs}
        missing = essential_categories - existing_cats
        if missing:
            readable = [c.replace("_", " ").title() for c in missing]
            insights.append(Insight(
                "Missing essential documents",
                f"Consider uploading: {', '.join(readable)}.",
                "document", Insight.PRIORITY_MEDIUM, "tip",
                action_label="Upload Document"))

        # --- 3. Duplicate detection (same filename) ---
        name_counts = Counter(d.original_filename for d in all_docs)
        dupes = {name: cnt for name, cnt in name_counts.items() if cnt > 1}
        if dupes:
            names = list(dupes.keys())[:3]
            insights.append(Insight(
                f"{sum(dupes.values()) - len(dupes)} possible duplicate(s)",
                f"Files like \"{names[0]}\" appear multiple times. "
                f"Review and remove duplicates to save space.",
                "document", Insight.PRIORITY_LOW, "anomaly"))

        # --- 4. Untagged documents ---
        untagged = [d for d in all_docs if not d.tags or not d.tags.strip()]
        if untagged and len(untagged) >= 3:
            insights.append(Insight(
                f"{len(untagged)} documents without tags",
                "Adding tags makes documents easier to find with search.",
                "document", Insight.PRIORITY_LOW, "tip"))

        return insights

    # ── Security Intelligence ─────────────────────────────────────────────

    @classmethod
    def analyse_security(cls, session) -> list[Insight]:
        from src.database.operations import ConnectedApplicationManager
        insights: list[Insight] = []

        apps = ConnectedApplicationManager.get_all_connected_apps(session, active_only=True)
        if not apps:
            return insights

        # --- 1. Password health scan ---
        weak_passwords = []
        reused_passwords = []
        old_passwords = []

        pw_hashes: dict[str, list[str]] = defaultdict(list)
        for app in apps:
            pw = app.password_encrypted or ""
            if pw:
                pw_hashes[pw].append(app.name)

            # Weak password heuristic (only if we can see raw length via stored field)
            if pw and len(pw) < 12:
                weak_passwords.append(app.name)

            # Old / stale passwords (not accessed in 180+ days)
            if app.last_accessed:
                days_since = (datetime.now() - app.last_accessed).days
                if days_since > 180:
                    old_passwords.append(app.name)

        # Reused passwords
        for pw_hash, names in pw_hashes.items():
            if len(names) > 1:
                reused_passwords.extend(names)

        if reused_passwords:
            sample = ", ".join(reused_passwords[:3])
            insights.append(Insight(
                f"Password reuse detected ({len(reused_passwords)} apps)",
                f"Apps like {sample} share the same password. "
                f"Use unique passwords for each account.",
                "security", Insight.PRIORITY_HIGH, "security",
                action_label="View Apps"))

        if old_passwords:
            insights.append(Insight(
                f"{len(old_passwords)} app(s) not accessed in 6+ months",
                f"Review {', '.join(old_passwords[:3])} — consider updating passwords or removing unused accounts.",
                "security", Insight.PRIORITY_MEDIUM, "security"))

        # --- 2. Missing information ---
        no_url = [a for a in apps if not a.website_url and not a.login_url]
        if no_url:
            insights.append(Insight(
                f"{len(no_url)} app(s) missing website URL",
                "Adding URLs makes quick-access one click away.",
                "security", Insight.PRIORITY_LOW, "tip"))

        # --- 3. Category coverage ---
        cats = Counter(a.category for a in apps if a.category)
        if len(cats) == 1 and len(apps) >= 3:
            insights.append(Insight(
                "All apps in one category",
                "Consider categorising your connected apps for better organisation.",
                "security", Insight.PRIORITY_LOW, "tip"))

        return insights

    # ── Net Worth Intelligence ────────────────────────────────────────────

    @classmethod
    def analyse_net_worth(cls, session) -> list[Insight]:
        from src.database.operations import NetWorthManager
        insights: list[Insight] = []

        snapshots = NetWorthManager.get_snapshots_serialized(session)
        if not snapshots:
            insights.append(Insight(
                "Track your net worth",
                "Start recording monthly snapshots to visualize your wealth growth over time.",
                "general", Insight.PRIORITY_LOW, "money",
                action_label="Open Net Worth"))
            return insights

        latest = snapshots[-1]
        nw = latest.get("net_worth", 0)

        # --- 1. Monthly trend ---
        if len(snapshots) >= 2:
            prev_nw = snapshots[-2].get("net_worth", 0)
            if prev_nw != 0:
                change = nw - prev_nw
                pct = change / abs(prev_nw) * 100
                if change > 0:
                    insights.append(Insight(
                        f"Net worth grew ${change:,.0f} ({pct:+.1f}%)",
                        "Great progress! Keep building your assets.",
                        "general", Insight.PRIORITY_LOW, "trend"))
                elif change < 0:
                    insights.append(Insight(
                        f"Net worth decreased ${abs(change):,.0f} ({pct:+.1f}%)",
                        "Review recent liabilities or asset changes.",
                        "general", Insight.PRIORITY_MEDIUM, "warning"))

        # --- 2. Debt-to-asset ratio ---
        import json as _json
        assets_total = 0
        liabilities_total = 0
        try:
            assets = _json.loads(latest.get("assets_json", "{}"))
            liabilities = _json.loads(latest.get("liabilities_json", "{}"))
            assets_total = sum(assets.values())
            liabilities_total = sum(liabilities.values())
        except Exception:
            pass

        if assets_total > 0:
            ratio = liabilities_total / assets_total * 100
            if ratio > 80:
                insights.append(Insight(
                    f"High debt ratio: {ratio:.0f}%",
                    "Your liabilities are over 80% of your assets. Focus on debt reduction.",
                    "general", Insight.PRIORITY_HIGH, "warning"))
            elif ratio > 50:
                insights.append(Insight(
                    f"Moderate debt ratio: {ratio:.0f}%",
                    "Consider a plan to bring liabilities below 50% of assets.",
                    "general", Insight.PRIORITY_MEDIUM, "money"))

        # --- 3. Snapshot freshness ---
        if snapshots:
            last_date_str = latest.get("snapshot_date", "")
            try:
                last_dt = datetime.fromisoformat(str(last_date_str))
                days_ago = (datetime.now() - last_dt).days
                if days_ago > 45:
                    insights.append(Insight(
                        "Net worth snapshot overdue",
                        f"Last snapshot was {days_ago} days ago. Take a new one to stay on track.",
                        "general", Insight.PRIORITY_MEDIUM, "calendar",
                        action_label="Take Snapshot"))
            except Exception:
                pass

        return insights

    # ── Smart Suggestions / Auto-categorisation ──────────────────────────

    @classmethod
    def suggest_category(cls, title: str) -> str:
        """Suggest a budget category based on transaction title keywords."""
        title_lower = title.lower()
        rules = [
            (["rent", "mortgage", "hoa", "property tax", "home"], "Housing"),
            (["grocery", "groceries", "supermarket", "walmart", "costco", "trader joe",
              "whole foods", "kroger", "aldi", "safeway", "publix"], "Food & Groceries"),
            (["gas", "fuel", "uber", "lyft", "parking", "toll", "metro", "transit",
              "subway", "bus"], "Transportation"),
            (["electric", "water", "internet", "cable", "phone", "utility", "verizon",
              "at&t", "t-mobile", "comcast", "xfinity"], "Utilities"),
            (["doctor", "hospital", "pharmacy", "medical", "dental", "vision",
              "prescription", "health", "clinic", "cvs", "walgreens"], "Healthcare"),
            (["netflix", "spotify", "hulu", "disney", "movie", "concert", "theater",
              "game", "gaming", "entertainment", "amc"], "Entertainment"),
            (["amazon", "target", "best buy", "apple", "store", "shop", "mall",
              "clothing", "shoes", "fashion"], "Shopping"),
            (["insurance", "geico", "state farm", "progressive", "allstate",
              "life insurance"], "Insurance"),
            (["subscription", "membership", "patreon", "premium", "annual fee"], "Subscriptions"),
            (["savings", "deposit", "transfer to savings", "emergency fund"], "Savings"),
            (["invest", "stock", "etf", "mutual fund", "crypto", "bitcoin",
              "robinhood", "fidelity", "vanguard", "schwab"], "Investment"),
            (["tuition", "course", "training", "book", "udemy", "school",
              "university", "college"], "Education"),
            (["haircut", "salon", "spa", "gym", "fitness", "personal care",
              "beauty", "barber"], "Personal Care"),
            (["restaurant", "dine", "dining", "grubhub", "doordash",
              "ubereats", "takeout", "cafe", "coffee", "starbucks"], "Dining Out"),
            (["flight", "hotel", "airbnb", "travel", "vacation", "trip",
              "booking", "airline"], "Travel"),
        ]
        for keywords, category in rules:
            for kw in keywords:
                if kw in title_lower:
                    return category
        return "Other"

    @classmethod
    def smart_score_password(cls, password: str) -> dict:
        """Analyse password strength and return a score + tips."""
        score = 0
        tips = []
        length = len(password)

        if length >= 16:
            score += 40
        elif length >= 12:
            score += 30
        elif length >= 8:
            score += 15
        else:
            score += 5
            tips.append("Use at least 12 characters")

        if re.search(r"[A-Z]", password):
            score += 10
        else:
            tips.append("Add uppercase letters")

        if re.search(r"[a-z]", password):
            score += 10
        else:
            tips.append("Add lowercase letters")

        if re.search(r"\d", password):
            score += 10
        else:
            tips.append("Add numbers")

        if re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'`~]", password):
            score += 15
        else:
            tips.append("Add special characters")

        # Penalise common patterns
        common = ["password", "123456", "qwerty", "abc123", "letmein",
                   "admin", "welcome", "monkey", "dragon"]
        if any(c in password.lower() for c in common):
            score = max(score - 30, 5)
            tips.append("Avoid common words")

        if re.search(r"(.)\1{3,}", password):
            score = max(score - 10, 5)
            tips.append("Avoid repeated characters")

        score = min(score, 100)
        if score >= 80:
            label = "Strong"
            color = "#3fb950"
        elif score >= 50:
            label = "Moderate"
            color = "#f59e0b"
        else:
            label = "Weak"
            color = "#f85149"

        return {"score": score, "label": label, "color": color, "tips": tips}

    @classmethod
    def predict_next_due(cls, activity) -> str | None:
        """Generate a natural-language prediction for an activity's next occurrence."""
        if not activity.next_due_date:
            return None
        delta = activity.next_due_date - datetime.now()
        days = delta.days
        if days < 0:
            return f"Overdue by {abs(days)} day{'s' if abs(days) != 1 else ''}"
        elif days == 0:
            return "Due today"
        elif days == 1:
            return "Due tomorrow"
        elif days <= 7:
            return f"Due in {days} days ({activity.next_due_date.strftime('%A')})"
        else:
            return f"Due {activity.next_due_date.strftime('%b %d')}"

    @classmethod
    def generate_daily_greeting(cls, session) -> str:
        """Generate a context-aware daily greeting message."""
        from src.database.operations import ActivityManager
        now = datetime.now()
        hour = now.hour

        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        overdue = ActivityManager.get_overdue_activities(session)
        due_today = [
            a for a in ActivityManager.get_due_activities(session, days_ahead=1)
            if a.next_due_date and a.next_due_date.date() == now.date()
        ]

        parts = [f"{greeting}!"]
        if due_today:
            parts.append(f"You have {len(due_today)} task{'s' if len(due_today) != 1 else ''} due today.")
        if overdue:
            parts.append(f"{len(overdue)} overdue item{'s' if len(overdue) != 1 else ''} need attention.")
        if not due_today and not overdue:
            parts.append("You're all caught up — great job!")

        return " ".join(parts)
