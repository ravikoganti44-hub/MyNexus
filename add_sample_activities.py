"""
Add comprehensive sample financial activities for demonstration
Includes: Bills, payments, insurance, taxes, subscriptions, maintenance
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from src.database.config import get_session
from src.database.operations import ActivityManager
from src.database.models import RecurrenceType, CategoryType, Activity

def add_sample_activities():
    """Add comprehensive sample financial activities"""
    session = get_session()
    
    try:
        now = datetime.now()
        
        # Comprehensive sample activities organized by type
        sample_activities = [
            # ========== MONTHLY PAYMENTS ==========
            {
                'title': 'Mortgage Payment',
                'description': 'Monthly mortgage payment to Better.com ($2,450)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=1) + relativedelta(months=1),
                'reminder_days_before': 3,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Credit Card Payment - Chase',
                'description': 'Monthly credit card payment for Chase Sapphire ($2,000 average)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now + timedelta(days=5),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Credit Card Payment - AmEx',
                'description': 'Pay American Express Gold Card statement ($1,500 average)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now + timedelta(days=12),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Electric Bill',
                'description': 'Monthly electric bill payment to Duke Energy (~$150)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=15) + relativedelta(months=0),
                'reminder_days_before': 3,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Internet/Cable Bill',
                'description': 'Monthly Xfinity internet and cable payment ($120)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=20) + relativedelta(months=0),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Gas Bill',
                'description': 'Monthly natural gas heating bill (~$95)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=10) + relativedelta(months=0),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== AUTO INSURANCE PAYMENTS ==========
            {
                'title': 'Auto Insurance - Geico',
                'description': 'Monthly automobile insurance payment ($85)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=8) + relativedelta(months=0),
                'reminder_days_before': 3,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== QUARTERLY & SEMI-ANNUAL PAYMENTS ==========
            {
                'title': 'Water & Sewer Bill',
                'description': 'Quarterly water and sewer payment (~$300)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.QUARTERLY,
                'start_date': now,
                'next_due_date': now + timedelta(days=30),
                'reminder_days_before': 5,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Homeowners Insurance',
                'description': 'Semi-annual homeowners insurance ($1,200/year, $600 each payment)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.BIWEEKLY,
                'recurrence_interval': 26,  # 26 weeks = ~6 months
                'start_date': now,
                'next_due_date': now.replace(month=6, day=1),
                'reminder_days_before': 7,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== ANNUAL PAYMENTS ==========
            {
                'title': 'Property Tax Payment',
                'description': 'Annual property tax payment to County Assessor (~$3,600)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=4, day=15),
                'reminder_days_before': 14,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Federal Income Tax Filing',
                'description': 'Federal tax return filing deadline - IRS',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=4, day=15),
                'reminder_days_before': 30,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'State Income Tax Filing',
                'description': 'State tax return filing deadline',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=4, day=15),
                'reminder_days_before': 30,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Car Registration Renewal',
                'description': 'Annual vehicle registration renewal (~$200)',
                'category': CategoryType.MAINTENANCE,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=7, day=1),
                'reminder_days_before': 21,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Car Inspection',
                'description': 'Annual vehicle safety inspection',
                'category': CategoryType.MAINTENANCE,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=6, day=1),
                'reminder_days_before': 14,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== SUBSCRIPTIONS ==========
            {
                'title': 'Netflix Subscription',
                'description': 'Monthly streaming service subscription ($15.99)',
                'category': CategoryType.SUBSCRIPTION,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now + timedelta(days=25),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Adobe Creative Cloud',
                'description': 'Monthly software subscription for creative tools ($54.99)',
                'category': CategoryType.SUBSCRIPTION,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=1) + relativedelta(months=1),
                'reminder_days_before': 2,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Gym Membership',
                'description': 'Monthly fitness center membership ($50)',
                'category': CategoryType.SUBSCRIPTION,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=1) + relativedelta(months=0),
                'reminder_days_before': 1,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Microsoft 365 Annual',
                'description': 'Annual Microsoft Office and cloud storage subscription ($100)',
                'category': CategoryType.SUBSCRIPTION,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=9, day=1),
                'reminder_days_before': 7,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== MAINTENANCE & CHECKUPS ==========
            {
                'title': 'Oil Change - Car Maintenance',
                'description': 'Car oil change and filter service (~$50, every 5,000 miles)',
                'category': CategoryType.MAINTENANCE,
                'recurrence_type': RecurrenceType.CUSTOM,
                'recurrence_interval': 90,  # Every 3 months typically
                'start_date': now,
                'next_due_date': now + timedelta(days=60),
                'reminder_days_before': 7,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'HVAC Maintenance',
                'description': 'Annual HVAC system inspection and maintenance',
                'category': CategoryType.MAINTENANCE,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=3, day=15),
                'reminder_days_before': 14,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Dental Checkup',
                'description': 'Regular dental cleaning and checkup (every 6 months)',
                'category': CategoryType.HEALTH,
                'recurrence_type': RecurrenceType.BIWEEKLY,
                'recurrence_interval': 26,  # 26 weeks = 6 months
                'start_date': now,
                'next_due_date': now + timedelta(days=45),
                'reminder_days_before': 7,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Eye Doctor Visit',
                'description': 'Annual eye exam and vision check',
                'category': CategoryType.HEALTH,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=8, day=15),
                'reminder_days_before': 7,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': 'Annual Physical Exam',
                'description': 'Annual medical checkup with primary care physician',
                'category': CategoryType.HEALTH,
                'recurrence_type': RecurrenceType.YEARLY,
                'start_date': now,
                'next_due_date': now.replace(month=10, day=1),
                'reminder_days_before': 14,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            
            # ========== INVESTMENT CONTRIBUTIONS ==========
            {
                'title': 'Retirement IRA Contribution',
                'description': 'Monthly automatic contribution to Vanguard IRA ($583/month = $7,000/year)',
                'category': CategoryType.PAYMENT,
                'recurrence_type': RecurrenceType.MONTHLY,
                'start_date': now,
                'next_due_date': now.replace(day=1) + relativedelta(months=0),
                'reminder_days_before': 0,
                'reminder_hours_before': 0,
                'send_notification': True
            },
            {
                'title': '401(k) Review & Rebalance',
                'description': 'Quarterly portfolio review and rebalancing',
                'category': CategoryType.TASK,
                'recurrence_type': RecurrenceType.QUARTERLY,
                'start_date': now,
                'next_due_date': now + timedelta(days=30),
                'reminder_days_before': 1,
                'reminder_hours_before': 0,
                'send_notification': True
            },
        ]
        
        # Add each activity
        added_count = 0
        skipped_count = 0
        
        print("=" * 70)
        print("📋 Adding Comprehensive Financial Activities")
        print("=" * 70)
        
        for activity_data in sample_activities:
            # Check if activity already exists
            existing = session.query(Activity).filter(
                Activity.title == activity_data['title']
            ).first()
            
            if not existing:
                activity = ActivityManager.create_activity(session, **activity_data)
                print(f"✅ {activity_data['title']:<45} | {activity_data['category'].value.upper()}")
                added_count += 1
            else:
                skipped_count += 1
        
        print("\n" + "=" * 70)
        print(f"✅ Summary: {added_count} activities added, {skipped_count} existing")
        print("=" * 70)
        print("\nActivity Categories Added:")
        print("  💳 Monthly Bill Payments (6 activities)")
        print("  🏠 Insurance Payments (2 activities)")
        print("  💰 Quarterly & Semi-Annual (2 activities)")
        print("  📅 Annual Payments & Taxes (4 activities)")
        print("  🚗 Vehicle Maintenance (3 activities)")
        print("  📺 Subscriptions (4 activities)")
        print("  🔧 Home & Auto Maintenance (3 activities)")
        print("  ❤️  Health Checkups (3 activities)")
        print("  📈 Investment Contributions (2 activities)")
        print(f"\n💾 Total: {added_count} activities loaded!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    add_sample_activities()
