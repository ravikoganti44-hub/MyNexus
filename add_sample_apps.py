"""
Add comprehensive sample connected applications for demonstration
Includes: Banks, Mortgage companies, Insurance providers, Utilities, Credit Cards
"""

from src.database.config import get_session
from src.database.operations import ConnectedApplicationManager

def add_sample_apps():
    """Add comprehensive sample connected applications"""
    session = get_session()
    
    try:
        # Comprehensive sample apps organized by category
        sample_apps = [
            # ========== BANKING ========== 
            {
                'name': 'Chase Checking Account',
                'app_type': 'banking',
                'app_name': 'Chase Bank',
                'category': 'banking',
                'website_url': 'https://www.chase.com',
                'login_url': 'https://secure06a.chase.com/id/client/login',
                'username': 'user@example.com',
                'account_number': '****1234',
                'account_holder': 'John Doe',
                'icon_emoji': '🏦',
                'notes': 'Primary checking account'
            },
            {
                'name': 'Bank of America Savings',
                'app_type': 'banking',
                'app_name': 'Bank of America',
                'category': 'banking',
                'website_url': 'https://www.bankofamerica.com',
                'login_url': 'https://www.bankofamerica.com/login',
                'username': 'user@example.com',
                'account_number': '****5678',
                'account_holder': 'John Doe',
                'icon_emoji': '🏦',
                'notes': 'Savings account with high yield'
            },
            {
                'name': 'Well Fargo Business',
                'app_type': 'banking',
                'app_name': 'Wells Fargo',
                'category': 'banking',
                'website_url': 'https://www.wellsfargo.com',
                'login_url': 'https://online.wellsfargo.com',
                'username': 'business@example.com',
                'account_number': '****9012',
                'account_holder': 'John Doe',
                'icon_emoji': '🏦',
                'notes': 'Business checking account'
            },
            
            # ========== CREDIT CARDS ==========
            {
                'name': 'Chase Sapphire Preferred',
                'app_type': 'credit_card',
                'app_name': 'Chase Credit Cards',
                'category': 'credit_card',
                'website_url': 'https://www.chase.com/personal/credit-cards',
                'login_url': 'https://creditcards.chase.com/login',
                'username': 'user@example.com',
                'account_number': '****1111',
                'account_holder': 'John Doe',
                'icon_emoji': '💳',
                'notes': 'Premium travel rewards card'
            },
            {
                'name': 'American Express Gold',
                'app_type': 'credit_card',
                'app_name': 'American Express',
                'category': 'credit_card',
                'website_url': 'https://www.americanexpress.com',
                'login_url': 'https://myca.americanexpress.com',
                'username': 'user@example.com',
                'account_number': '****2222',
                'account_holder': 'John Doe',
                'icon_emoji': '💳',
                'notes': 'Gold card for dining and travel'
            },
            {
                'name': 'Discover Card',
                'app_type': 'credit_card',
                'app_name': 'Discover',
                'category': 'credit_card',
                'website_url': 'https://www.discover.com',
                'login_url': 'https://www.discover.com/login',
                'username': 'user@example.com',
                'account_number': '****3333',
                'account_holder': 'John Doe',
                'icon_emoji': '💳',
                'notes': 'Cashback rewards card'
            },
            
            # ========== MORTGAGE ==========
            {
                'name': 'Primary Mortgage - Better.com',
                'app_type': 'mortgage',
                'app_name': 'Better.com',
                'category': 'mortgage',
                'website_url': 'https://www.better.com',
                'login_url': 'https://app.better.com/login',
                'username': 'user@example.com',
                'account_number': 'MG-123456789',
                'account_holder': 'John Doe',
                'icon_emoji': '🏠',
                'notes': '30-year fixed mortgage, 3.5% APR, ~$2,500/month'
            },
            {
                'name': 'Loan Servicer - Fannie Mae',
                'app_type': 'mortgage',
                'app_name': 'Fannie Mae Portal',
                'category': 'mortgage',
                'website_url': 'https://www.fanniemae.com',
                'login_url': 'https://myaloan.fanniemae.com/portal',
                'username': 'user@example.com',
                'account_number': 'FM-987654321',
                'account_holder': 'John Doe',
                'icon_emoji': '🏠',
                'notes': 'Mortgage loan servicer for payment management'
            },
            
            # ========== INSURANCE ==========
            {
                'name': 'Homeowners Insurance - State Farm',
                'app_type': 'insurance',
                'app_name': 'State Farm',
                'category': 'insurance',
                'website_url': 'https://www.statefarm.com',
                'login_url': 'https://www.statefarm.com/login',
                'username': 'user@example.com',
                'account_number': 'HO-98765432',
                'account_holder': 'John Doe',
                'icon_emoji': '🏠',
                'notes': 'Homeowners insurance - $1,200/year'
            },
            {
                'name': 'Auto Insurance - Geico',
                'app_type': 'insurance',
                'app_name': 'Geico',
                'category': 'insurance',
                'website_url': 'https://www.geico.com',
                'login_url': 'https://www.geico.com/login',
                'username': 'user@example.com',
                'account_number': 'AUTO-456789',
                'account_holder': 'John Doe',
                'icon_emoji': '🚗',
                'notes': 'Auto insurance for 2 vehicles - $85/month'
            },
            {
                'name': 'Life Insurance - Term Life',
                'app_type': 'insurance',
                'app_name': 'Haven Life',
                'category': 'insurance',
                'website_url': 'https://www.havenlife.com',
                'login_url': 'https://www.havenlife.com/login',
                'username': 'user@example.com',
                'account_number': 'LIFE-321654',
                'account_holder': 'John Doe',
                'icon_emoji': '🛡️',
                'notes': '$500,000 20-year term life insurance'
            },
            {
                'name': 'Umbrella Insurance - Progressive',
                'app_type': 'insurance',
                'app_name': 'Progressive',
                'category': 'insurance',
                'website_url': 'https://www.progressive.com',
                'login_url': 'https://www.progressive.com/login',
                'username': 'user@example.com',
                'account_number': 'UMB-789012',
                'account_holder': 'John Doe',
                'icon_emoji': '☂️',
                'notes': '$1M umbrella liability coverage'
            },
            
            # ========== UTILITIES ==========
            {
                'name': 'Electric - Duke Energy',
                'app_type': 'utilities',
                'app_name': 'Duke Energy',
                'category': 'utilities',
                'website_url': 'https://www.dukeenergy.com',
                'login_url': 'https://www.dukeenergy.com/login',
                'username': 'user@example.com',
                'account_number': 'ELEC-123456',
                'icon_emoji': '⚡',
                'notes': 'Electric bill - Average $150/month'
            },
            {
                'name': 'Water & Sewer - City Services',
                'app_type': 'utilities',
                'app_name': 'Municipal Water Department',
                'category': 'utilities',
                'website_url': 'https://www.citywaterservices.gov',
                'login_url': 'https://www.citywaterservices.gov/pay',
                'username': 'user@example.com',
                'account_number': 'WATER-654321',
                'icon_emoji': '💧',
                'notes': 'Water and sewer - Quarterly billing ~$300'
            },
            {
                'name': 'Gas Utility - Natural Gas Co',
                'app_type': 'utilities',
                'app_name': 'National Gas Services',
                'category': 'utilities',
                'website_url': 'https://www.nationalgasservices.com',
                'login_url': 'https://www.nationalgasservices.com/login',
                'username': 'user@example.com',
                'account_number': 'GAS-987654',
                'icon_emoji': '🔥',
                'notes': 'Natural gas heating - $80-120/month seasonal'
            },
            {
                'name': 'Internet/Cable - Comcast',
                'app_type': 'utilities',
                'app_name': 'Comcast Xfinity',
                'category': 'utilities',
                'website_url': 'https://www.xfinity.com',
                'login_url': 'https://www.xfinity.com/login',
                'username': 'user@example.com',
                'account_number': 'XFINITY-111111',
                'icon_emoji': '📡',
                'notes': 'Internet 500Mbps + TV bundle - $120/month'
            },
            
            # ========== TAX & GOVERNMENT ==========
            {
                'name': 'IRS - Tax Filing',
                'app_type': 'government',
                'app_name': 'IRS.gov',
                'category': 'government',
                'website_url': 'https://www.irs.gov',
                'login_url': 'https://www.irs.gov/account',
                'username': 'user@example.com',
                'account_number': 'SSN-****1234',
                'icon_emoji': '💼',
                'notes': 'Federal tax account - Annual filing deadline April 15'
            },
            {
                'name': 'State Tax Authority',
                'app_type': 'government',
                'app_name': 'State Department of Revenue',
                'category': 'government',
                'website_url': 'https://www.state.gov/tax',
                'login_url': 'https://www.state.gov/tax/login',
                'username': 'user@example.com',
                'account_number': 'STATE-TAX-001',
                'icon_emoji': '📊',
                'notes': 'State income tax - File by April 15'
            },
            {
                'name': 'Property Tax - County Assessor',
                'app_type': 'government',
                'app_name': 'County Tax Assessor',
                'category': 'government',
                'website_url': 'https://assessor.county.gov',
                'login_url': 'https://assessor.county.gov/pay',
                'username': 'user@example.com',
                'account_number': 'PROP-TAX-001',
                'icon_emoji': '🏘️',
                'notes': 'Annual property tax - Paid semi-annually'
            },
            
            # ========== INVESTMENT & WEALTH ==========
            {
                'name': 'Fidelity Brokerage',
                'app_type': 'investment',
                'app_name': 'Fidelity Investments',
                'category': 'investment',
                'website_url': 'https://www.fidelity.com',
                'login_url': 'https://login.fidelity.com',
                'username': 'user@example.com',
                'account_number': 'FID-123456789',
                'account_holder': 'John Doe',
                'icon_emoji': '📈',
                'notes': 'Brokerage account with stocks and ETFs'
            },
            {
                'name': 'Vanguard Retirement IRA',
                'app_type': 'investment',
                'app_name': 'Vanguard',
                'category': 'investment',
                'website_url': 'https://www.vanguard.com',
                'login_url': 'https://www.vanguard.com/login',
                'username': 'user@example.com',
                'account_number': 'VGD-IRA-001',
                'account_holder': 'John Doe',
                'icon_emoji': '🎯',
                'notes': 'Traditional IRA - Max annual contribution $7,000'
            },
            
            # ========== PAYMENT PROCESSORS ==========
            {
                'name': 'PayPal Business',
                'app_type': 'payment',
                'app_name': 'PayPal',
                'category': 'payment',
                'website_url': 'https://www.paypal.com',
                'login_url': 'https://www.paypal.com/login',
                'username': 'user@example.com',
                'account_number': 'PP-USER123',
                'icon_emoji': '💰',
                'notes': 'Business payment processing and transfers'
            },
            {
                'name': 'Stripe Payment Gateway',
                'app_type': 'payment',
                'app_name': 'Stripe',
                'category': 'payment',
                'website_url': 'https://stripe.com',
                'login_url': 'https://dashboard.stripe.com/login',
                'username': 'business@example.com',
                'account_number': 'acct_stripe123',
                'icon_emoji': '💳',
                'notes': 'Online payment processing for e-commerce'
            },
        ]
        
        # Add each app
        added_count = 0
        skipped_count = 0
        
        print("=" * 60)
        print("🔧 Adding Financial Application Templates")
        print("=" * 60)
        
        for app_data in sample_apps:
            existing = ConnectedApplicationManager.get_connected_app_by_name(session, app_data['name'])
            if not existing:
                app = ConnectedApplicationManager.create_connected_app(session, **app_data)
                print(f"✅ {app_data['name']:<45} | {app_data['app_name']}")
                added_count += 1
            else:
                skipped_count += 1
        
        print("\n" + "=" * 60)
        print(f"✅ Summary: {added_count} apps added, {skipped_count} existing")
        print("=" * 60)
        print("\nAvailable Categories:")
        print("  🏦 Banking (3 apps)")
        print("  💳 Credit Cards (3 apps)")
        print("  🏠 Mortgage (2 apps)")
        print("  🛡️  Insurance (4 apps)")
        print("  ⚡ Utilities (4 apps)")
        print("  💼 Government/Tax (3 apps)")
        print("  📈 Investment (2 apps)")
        print("  💰 Payment Processing (2 apps)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == '__main__':
    add_sample_apps()
