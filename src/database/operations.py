"""
Database operations for activities, integrations, connected applications, and documents
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .models import (
    Activity, ActivityCompletion, Integration, Notification,
    ConnectedApplication, Document, DocumentCategory, RecurrenceType,
    BudgetPeriod, BudgetLimit, BudgetEntry, NetWorthSnapshot,
)


class ActivityManager:
    """Manager for activity database operations"""
    
    @staticmethod
    def create_activity(session: Session, **kwargs) -> Activity:
        """Create a new activity"""
        activity = Activity(**kwargs)
        session.add(activity)
        session.commit()
        session.expire_all()  # Refresh session cache
        return activity
    
    @staticmethod
    def get_activity(session: Session, activity_id: int) -> Activity:
        """Get activity by ID"""
        return session.query(Activity).filter(Activity.id == activity_id).first()
    
    @staticmethod
    def get_all_activities(session: Session, active_only: bool = True):
        """Get all activities"""
        query = session.query(Activity)
        if active_only:
            query = query.filter(Activity.is_active == True)
        return query.all()
    
    @staticmethod
    def update_activity(session: Session, activity_id: int, **kwargs) -> Activity:
        """Update an activity"""
        activity = session.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            for key, value in kwargs.items():
                if hasattr(activity, key):
                    setattr(activity, key, value)
            activity.updated_at = datetime.now()
            session.commit()
            session.expire_all()  # Refresh session cache
        return activity
    
    @staticmethod
    def delete_activity(session: Session, activity_id: int) -> bool:
        """Delete an activity"""
        activity = session.query(Activity).filter(Activity.id == activity_id).first()
        if activity:
            session.delete(activity)
            session.commit()
            session.expire_all()  # Refresh session cache
            return True
        return False
    
    @staticmethod
    def get_due_activities(session: Session, days_ahead: int = 7):
        """Get activities due in the next N days"""
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        
        return session.query(Activity).filter(
            Activity.is_active == True,
            Activity.next_due_date >= now,
            Activity.next_due_date <= future_date
        ).order_by(Activity.next_due_date).all()
    
    @staticmethod
    def get_overdue_activities(session: Session):
        """Get overdue activities"""
        now = datetime.now()
        return session.query(Activity).filter(
            Activity.is_active == True,
            Activity.next_due_date < now,
            Activity.is_completed == False
        ).order_by(Activity.next_due_date).all()
    
    @staticmethod
    def complete_activity(session: Session, activity_id: int, notes: str = "") -> ActivityCompletion:
        """Mark an activity as completed"""
        activity = session.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return None
        
        # Create completion record
        completion = ActivityCompletion(activity_id=activity_id, notes=notes)
        session.add(completion)
        
        # Calculate next due date if recurring
        next_due = activity.calculate_next_due_date()
        if next_due:
            activity.next_due_date = next_due
            activity.is_completed = False
        else:
            activity.is_completed = True
        
        activity.updated_at = datetime.now()
        session.commit()
        session.expire_all()  # Refresh session cache
        return completion
    
    @staticmethod
    def get_completion_history(session: Session, activity_id: int, limit: int = 10):
        """Get completion history for an activity"""
        return session.query(ActivityCompletion).filter(
            ActivityCompletion.activity_id == activity_id
        ).order_by(ActivityCompletion.completed_at.desc()).limit(limit).all()


class IntegrationManager:
    """Manager for integration database operations"""
    
    @staticmethod
    def create_integration(session: Session, **kwargs) -> Integration:
        """Create a new integration"""
        integration = Integration(**kwargs)
        session.add(integration)
        session.commit()
        session.expire_all()  # Refresh session cache
        return integration
    
    @staticmethod
    def get_integration(session: Session, integration_id: int) -> Integration:
        """Get integration by ID"""
        return session.query(Integration).filter(Integration.id == integration_id).first()
    
    @staticmethod
    def get_integration_by_name(session: Session, name: str) -> Integration:
        """Get integration by name"""
        return session.query(Integration).filter(Integration.name == name).first()
    
    @staticmethod
    def get_all_integrations(session: Session, active_only: bool = True):
        """Get all integrations"""
        query = session.query(Integration)
        if active_only:
            query = query.filter(Integration.is_active == True)
        return query.all()
    
    @staticmethod
    def update_integration(session: Session, integration_id: int, **kwargs) -> Integration:
        """Update an integration"""
        integration = session.query(Integration).filter(Integration.id == integration_id).first()
        if integration:
            for key, value in kwargs.items():
                if hasattr(integration, key):
                    setattr(integration, key, value)
            session.commit()
        return integration
    
    @staticmethod
    def delete_integration(session: Session, integration_id: int) -> bool:
        """Delete an integration"""
        integration = session.query(Integration).filter(Integration.id == integration_id).first()
        if integration:
            session.delete(integration)
            session.commit()
            return True
        return False


class NotificationManager:
    """Manager for notification database operations"""
    
    @staticmethod
    def create_notification(session: Session, **kwargs) -> Notification:
        """Create a new notification"""
        notification = Notification(**kwargs)
        session.add(notification)
        session.commit()
        return notification
    
    @staticmethod
    def get_unread_notifications(session: Session, limit: int = 50):
        """Get unread notifications"""
        return session.query(Notification).filter(
            Notification.is_read == False
        ).order_by(Notification.sent_at.desc()).limit(limit).all()
    
    @staticmethod
    def mark_as_read(session: Session, notification_id: int):
        """Mark notification as read"""
        notification = session.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            session.commit()


class ConnectedApplicationManager:
    """Manager for connected applications database operations"""
    
    @staticmethod
    def create_connected_app(session: Session, **kwargs) -> ConnectedApplication:
        """Create a new connected application"""
        app = ConnectedApplication(**kwargs)
        session.add(app)
        session.commit()
        session.expire_all()  # Refresh session cache
        return app
    
    @staticmethod
    def get_connected_app(session: Session, app_id: int) -> ConnectedApplication:
        """Get connected application by ID"""
        return session.query(ConnectedApplication).filter(ConnectedApplication.id == app_id).first()
    
    @staticmethod
    def get_connected_app_by_name(session: Session, name: str) -> ConnectedApplication:
        """Get connected application by name"""
        return session.query(ConnectedApplication).filter(ConnectedApplication.name == name).first()
    
    @staticmethod
    def get_all_connected_apps(session: Session, active_only: bool = True):
        """Get all connected applications"""
        query = session.query(ConnectedApplication)
        if active_only:
            query = query.filter(ConnectedApplication.is_active == True)
        return query.order_by(ConnectedApplication.category, ConnectedApplication.name).all()
    
    @staticmethod
    def get_apps_by_category(session: Session, category: str, active_only: bool = True):
        """Get connected applications by category"""
        query = session.query(ConnectedApplication).filter(ConnectedApplication.category == category)
        if active_only:
            query = query.filter(ConnectedApplication.is_active == True)
        return query.order_by(ConnectedApplication.name).all()
    
    @staticmethod
    def update_connected_app(session: Session, app_id: int, **kwargs) -> ConnectedApplication:
        """Update a connected application"""
        app = session.query(ConnectedApplication).filter(ConnectedApplication.id == app_id).first()
        if app:
            for key, value in kwargs.items():
                if hasattr(app, key) and key not in ['id', 'created_at']:
                    setattr(app, key, value)
            app.updated_at = datetime.now()
            session.commit()
            session.expire_all()  # Refresh session cache
        return app
    
    @staticmethod
    def delete_connected_app(session: Session, app_id: int) -> bool:
        """Delete a connected application"""
        app = session.query(ConnectedApplication).filter(ConnectedApplication.id == app_id).first()
        if app:
            session.delete(app)
            session.commit()
            session.expire_all()  # Refresh session cache
            return True
        return False
    
    @staticmethod
    def update_last_accessed(session: Session, app_id: int):
        """Update last accessed timestamp"""
        app = session.query(ConnectedApplication).filter(ConnectedApplication.id == app_id).first()
        if app:
            app.last_accessed = datetime.now()
            session.commit()
            session.expire_all()  # Refresh session cache
    
    @staticmethod
    def search_connected_apps(session: Session, search_term: str):
        """Search connected applications by name or account"""
        return session.query(ConnectedApplication).filter(
            (ConnectedApplication.name.ilike(f'%{search_term}%')) |
            (ConnectedApplication.app_name.ilike(f'%{search_term}%')) |
            (ConnectedApplication.account_number.ilike(f'%{search_term}%'))
        ).all()


class DocumentManager:
    """Manager for document vault database operations"""
    
    @staticmethod
    def create_document(session: Session, **kwargs) -> Document:
        """Create a new document"""
        document = Document(**kwargs)
        session.add(document)
        session.commit()
        session.expire_all()
        return document
    
    @staticmethod
    def get_document(session: Session, document_id: int) -> Document:
        """Get document by ID"""
        return session.query(Document).filter(Document.id == document_id).first()
    
    @staticmethod
    def get_all_documents(session: Session, archived_only: bool = False):
        """Get all documents"""
        query = session.query(Document)
        if not archived_only:
            query = query.filter(Document.is_archived == False)
        else:
            query = query.filter(Document.is_archived == True)
        return query.order_by(Document.created_at.desc()).all()
    
    @staticmethod
    def get_documents_by_category(session: Session, category: DocumentCategory, archived_only: bool = False):
        """Get documents by category"""
        query = session.query(Document).filter(Document.category == category)
        if not archived_only:
            query = query.filter(Document.is_archived == False)
        return query.order_by(Document.created_at.desc()).all()
    
    @staticmethod
    def get_documents_by_subcategory(session: Session, category: DocumentCategory, sub_category: str, archived_only: bool = False):
        """Get documents by category and subcategory"""
        query = session.query(Document).filter(
            Document.category == category,
            Document.sub_category == sub_category
        )
        if not archived_only:
            query = query.filter(Document.is_archived == False)
        return query.order_by(Document.created_at.desc()).all()
    
    @staticmethod
    def get_favorite_documents(session: Session):
        """Get favorite documents"""
        return session.query(Document).filter(
            Document.is_favorite == True,
            Document.is_archived == False
        ).order_by(Document.created_at.desc()).all()
    
    @staticmethod
    def update_document(session: Session, document_id: int, **kwargs) -> Document:
        """Update a document"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            for key, value in kwargs.items():
                if hasattr(document, key) and key not in ['id', 'created_at', 'stored_filename']:
                    setattr(document, key, value)
            document.updated_at = datetime.now()
            session.commit()
            session.expire_all()
        return document
    
    @staticmethod
    def delete_document(session: Session, document_id: int) -> bool:
        """Delete a document"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            session.delete(document)
            session.commit()
            session.expire_all()
            return True
        return False
    
    @staticmethod
    def archive_document(session: Session, document_id: int) -> Document:
        """Archive a document"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            document.is_archived = True
            document.updated_at = datetime.now()
            session.commit()
            session.expire_all()
        return document
    
    @staticmethod
    def unarchive_document(session: Session, document_id: int) -> Document:
        """Unarchive a document"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            document.is_archived = False
            document.updated_at = datetime.now()
            session.commit()
            session.expire_all()
        return document
    
    @staticmethod
    def toggle_favorite(session: Session, document_id: int) -> Document:
        """Toggle document favorite status"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            document.is_favorite = not document.is_favorite
            document.updated_at = datetime.now()
            session.commit()
            session.expire_all()
        return document
    
    @staticmethod
    def search_documents(session: Session, search_term: str):
        """Search documents by title, description, or tags"""
        return session.query(Document).filter(
            Document.is_archived == False,
            (Document.title.ilike(f'%{search_term}%')) |
            (Document.description.ilike(f'%{search_term}%')) |
            (Document.tags.ilike(f'%{search_term}%')) |
            (Document.reference_number.ilike(f'%{search_term}%'))
        ).order_by(Document.created_at.desc()).all()
    
    @staticmethod
    def update_last_accessed(session: Session, document_id: int):
        """Update last accessed timestamp"""
        document = session.query(Document).filter(Document.id == document_id).first()
        if document:
            document.last_accessed = datetime.now()
            session.commit()
            session.expire_all()
    
    @staticmethod
    def get_expiring_documents(session: Session, days_ahead: int = 30):
        """Get documents expiring soon"""
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        
        return session.query(Document).filter(
            Document.is_archived == False,
            Document.expiry_date.isnot(None),
            Document.expiry_date >= now,
            Document.expiry_date <= future_date
        ).order_by(Document.expiry_date).all()


# ── Budget Manager ─────────────────────────────────────────────────────────────

class BudgetManager:
    """Manager for budget periods, limits, and entries"""

    @staticmethod
    def get_or_create_period(session: Session, year: int, month: int) -> BudgetPeriod:
        period = session.query(BudgetPeriod).filter_by(year=year, month=month).first()
        if not period:
            period = BudgetPeriod(year=year, month=month)
            session.add(period)
            session.commit()
        return period

    @staticmethod
    def get_limits(session: Session, period_id: int):
        return session.query(BudgetLimit).filter_by(period_id=period_id).all()

    @staticmethod
    def set_limit(session: Session, period_id: int, category: str, amount: float) -> BudgetLimit:
        limit = session.query(BudgetLimit).filter_by(period_id=period_id, category=category).first()
        if limit:
            limit.limit_amount = amount
        else:
            limit = BudgetLimit(period_id=period_id, category=category, limit_amount=amount)
            session.add(limit)
        session.commit()
        return limit

    @staticmethod
    def get_entries(session: Session, period_id: int):
        return (session.query(BudgetEntry)
                .filter_by(period_id=period_id)
                .order_by(BudgetEntry.entry_date.desc())
                .all())

    @staticmethod
    def add_entry(session: Session, period_id: int, title: str, amount: float,
                  category: str, entry_date=None, notes=None) -> BudgetEntry:
        entry = BudgetEntry(
            period_id=period_id,
            title=title,
            amount=amount,
            category=category,
            entry_date=entry_date or datetime.now(),
            notes=notes,
        )
        session.add(entry)
        session.commit()
        return entry

    @staticmethod
    def delete_entry(session: Session, entry_id: int) -> bool:
        entry = session.query(BudgetEntry).filter_by(id=entry_id).first()
        if entry:
            session.delete(entry)
            session.commit()
            return True
        return False

    @staticmethod
    def get_spending_by_category(session: Session, period_id: int) -> dict:
        """Returns {category: total_spent}"""
        entries = session.query(BudgetEntry).filter_by(period_id=period_id).all()
        spending: dict = {}
        for entry in entries:
            spending[entry.category] = spending.get(entry.category, 0.0) + entry.amount
        return spending


# ── Net Worth Manager ──────────────────────────────────────────────────────────

class NetWorthManager:
    """Manager for net worth snapshots"""

    @staticmethod
    def get_all_snapshots(session: Session):
        return (session.query(NetWorthSnapshot)
                .order_by(NetWorthSnapshot.snapshot_date.desc(),
                           NetWorthSnapshot.id.desc())
                .all())

    @staticmethod
    def get_latest(session: Session):
        return (session.query(NetWorthSnapshot)
                .order_by(NetWorthSnapshot.snapshot_date.desc())
                .first())

    @staticmethod
    def create_snapshot(session: Session, assets: dict, liabilities: dict,
                        notes=None, snapshot_date=None) -> NetWorthSnapshot:
        import json
        snap = NetWorthSnapshot(
            snapshot_date=snapshot_date or datetime.now(),
            assets_json=json.dumps(assets),
            liabilities_json=json.dumps(liabilities),
            net_worth=sum(assets.values()) - sum(liabilities.values()),
            notes=notes,
        )
        session.add(snap)
        session.commit()
        return snap

    @staticmethod
    def update_snapshot(session: Session, snapshot_id: int, assets: dict,
                        liabilities: dict, notes=None, snapshot_date=None) -> NetWorthSnapshot:
        import json
        snap = session.query(NetWorthSnapshot).filter_by(id=snapshot_id).first()
        if snap:
            snap.assets_json = json.dumps(assets)
            snap.liabilities_json = json.dumps(liabilities)
            snap.net_worth = sum(assets.values()) - sum(liabilities.values())
            if notes is not None:
                snap.notes = notes
            if snapshot_date is not None:
                snap.snapshot_date = snapshot_date
            snap.updated_at = datetime.now()
            session.commit()
        return snap

    @staticmethod
    def delete_snapshot(session: Session, snapshot_id: int) -> bool:
        snap = session.query(NetWorthSnapshot).filter_by(id=snapshot_id).first()
        if snap:
            session.delete(snap)
            session.commit()
            return True
        return False

    @staticmethod
    def get_snapshots_serialized(session: Session) -> list[dict]:
        """Return all snapshots as plain dicts (safe to use after session close)."""
        import json as _json
        snaps = (session.query(NetWorthSnapshot)
                 .order_by(NetWorthSnapshot.snapshot_date.asc(),
                            NetWorthSnapshot.id.asc())
                 .all())
        result = []
        for s in snaps:
            assets = _json.loads(s.assets_json or "{}")
            liabs  = _json.loads(s.liabilities_json or "{}")
            result.append({
                "id":          s.id,
                "date":        s.snapshot_date,
                "assets":      assets,
                "liabilities": liabs,
                "total_assets": sum(assets.values()),
                "total_liab":   sum(liabs.values()),
                "net_worth":   s.net_worth,
                "notes":       s.notes or "",
            })
        return result

    @staticmethod
    def compute_insights(snapshots: list[dict]) -> dict:
        """
        Pure-Python analytics from a list of serialized snapshot dicts
        (oldest-first).  Returns dict of insight values for the UI.
        """
        if not snapshots:
            return {}

        latest  = snapshots[-1]
        nw_vals = [s["net_worth"] for s in snapshots]
        assets_vals = [s["total_assets"] for s in snapshots]

        # Month-over-month change (compare last two snapshots)
        mom_change     = nw_vals[-1] - nw_vals[-2] if len(nw_vals) >= 2 else 0.0
        mom_pct        = (mom_change / abs(nw_vals[-2]) * 100) if len(nw_vals) >= 2 and nw_vals[-2] != 0 else 0.0

        # Year-over-year: find a snapshot ~12 months back
        from datetime import timedelta
        one_year_ago = latest["date"] - timedelta(days=365)
        yoy_snap = next(
            (s for s in reversed(snapshots[:-1]) if s["date"] <= one_year_ago),
            snapshots[0]
        )
        yoy_change = latest["net_worth"] - yoy_snap["net_worth"]
        yoy_pct    = (yoy_change / abs(yoy_snap["net_worth"]) * 100) if yoy_snap["net_worth"] != 0 else 0.0

        # Debt-to-asset ratio
        d2a = (latest["total_liab"] / latest["total_assets"] * 100) if latest["total_assets"] > 0 else 0.0

        # Savings rate approximation (asset growth / previous total assets)
        asset_growth = assets_vals[-1] - assets_vals[-2] if len(assets_vals) >= 2 else 0.0

        # Best / worst periods
        changes = [nw_vals[i] - nw_vals[i-1] for i in range(1, len(nw_vals))]
        best_gain  = max(changes) if changes else 0.0
        worst_loss = min(changes) if changes else 0.0

        # FIRE number (25× annual expenses = annual liabilities × 25)
        fire_number = latest["total_liab"] * 25

        # Projected months to FIRE at current growth rate
        if len(nw_vals) >= 2:
            avg_monthly_growth = (nw_vals[-1] - nw_vals[0]) / max(len(nw_vals) - 1, 1)
        else:
            avg_monthly_growth = 0.0
        remaining = fire_number - latest["net_worth"]
        months_to_fire = (remaining / avg_monthly_growth) if avg_monthly_growth > 0 else None

        return {
            "latest":            latest,
            "snapshots":         snapshots,
            "mom_change":        mom_change,
            "mom_pct":           mom_pct,
            "yoy_change":        yoy_change,
            "yoy_pct":           yoy_pct,
            "d2a_ratio":         d2a,
            "asset_growth":      asset_growth,
            "best_gain":         best_gain,
            "worst_loss":        worst_loss,
            "fire_number":       fire_number,
            "months_to_fire":    months_to_fire,
            "avg_monthly_growth": avg_monthly_growth,
            "snapshot_count":    len(snapshots),
        }

    @staticmethod
    def get_expired_documents(session: Session):
        """Get expired documents"""
        now = datetime.now()
        return session.query(Document).filter(
            Document.is_archived == False,
            Document.expiry_date.isnot(None),
            Document.expiry_date < now
        ).order_by(Document.expiry_date).all()
