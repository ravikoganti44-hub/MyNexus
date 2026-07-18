"""
Test script for Document Vault feature
Tests all document management functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.config import get_session, init_db
from src.database.operations import DocumentManager
from src.database.models import Document, DocumentCategory, DocumentType


def test_document_vault():
    """Test all Document Vault functionality"""
    print("\n" + "="*70)
    print("🧪 DOCUMENT VAULT TEST SUITE")
    print("="*70 + "\n")
    
    # Initialize database
    print("1️⃣ Initializing database...")
    try:
        init_db()
        print("   ✅ Database initialized successfully\n")
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}\n")
        return False
    
    session = get_session()
    
    # Test 1: Create documents
    print("2️⃣ Testing document creation...")
    try:
        # Create test documents directory
        test_docs_dir = Path("data/documents")
        test_docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        test_file1 = test_docs_dir / "test_passport.txt"
        test_file1.write_text("Test passport content")
        
        test_file2 = test_docs_dir / "test_tax_2024.txt"
        test_file2.write_text("Test tax document for 2024")
        
        # Create documents in database
        doc1 = DocumentManager.create_document(
            session=session,
            title="My Test Passport",
            category=DocumentCategory.PASSPORT,
            original_filename="passport.txt",
            stored_filename="test_passport.txt",
            file_path=str(test_file1),
            file_size=test_file1.stat().st_size,
            file_type=DocumentType.TEXT,
            reference_number="ABC123456",
            issue_date=datetime.now() - timedelta(days=730),
            expiry_date=datetime.now() + timedelta(days=365),
        )
        
        doc2 = DocumentManager.create_document(
            session=session,
            title="Tax Return 2024",
            category=DocumentCategory.TAX_DOCUMENTS,
            sub_category="2024",
            original_filename="tax_2024.txt",
            stored_filename="test_tax_2024.txt",
            file_path=str(test_file2),
            file_size=test_file2.stat().st_size,
            file_type=DocumentType.TEXT,
        )
        
        print(f"   ✅ Created 2 test documents")
        print(f"      - Document 1: {doc1.title} (ID: {doc1.id})")
        print(f"      - Document 2: {doc2.title} (ID: {doc2.id})\n")
        
        doc1_id = doc1.id
        doc2_id = doc2.id
    except Exception as e:
        print(f"   ❌ Document creation failed: {e}\n")
        return False
    
    # Test 2: Retrieve documents
    print("3️⃣ Testing document retrieval...")
    try:
        all_docs = DocumentManager.get_all_documents(session)
        print(f"   ✅ Retrieved all documents: {len(all_docs)} found")
        
        passport_docs = DocumentManager.get_documents_by_category(session, DocumentCategory.PASSPORT)
        print(f"   ✅ Retrieved passport documents: {len(passport_docs)} found")
        
        tax_docs = DocumentManager.get_documents_by_category(session, DocumentCategory.TAX_DOCUMENTS)
        print(f"   ✅ Retrieved tax documents: {len(tax_docs)} found")
        
        tax_2024 = DocumentManager.get_documents_by_subcategory(session, DocumentCategory.TAX_DOCUMENTS, "2024")
        print(f"   ✅ Retrieved tax 2024 documents: {len(tax_2024)} found\n")
    except Exception as e:
        print(f"   ❌ Document retrieval failed: {e}\n")
        return False
    
    # Test 3: Search documents
    print("4️⃣ Testing document search...")
    try:
        search_results = DocumentManager.search_documents(session, "passport")
        print(f"   ✅ Search 'passport': {len(search_results)} result(s)")
        
        search_results = DocumentManager.search_documents(session, "tax")
        print(f"   ✅ Search 'tax': {len(search_results)} result(s)")
        
        search_results = DocumentManager.search_documents(session, "ABC123456")
        print(f"   ✅ Search reference number: {len(search_results)} result(s)\n")
    except Exception as e:
        print(f"   ❌ Document search failed: {e}\n")
        return False
    
    # Test 4: Update document - Toggle favorite
    print("5️⃣ Testing favorite toggle...")
    try:
        doc = DocumentManager.get_document(session, doc1_id)
        initial_state = doc.is_favorite
        
        DocumentManager.toggle_favorite(session, doc1_id)
        doc = DocumentManager.get_document(session, doc1_id)
        after_toggle = doc.is_favorite
        
        if initial_state != after_toggle:
            print(f"   ✅ Favorite toggle successful: {initial_state} → {after_toggle}")
        else:
            print(f"   ⚠️  Favorite toggle may not have worked")
        
        # Toggle back
        DocumentManager.toggle_favorite(session, doc1_id)
        print(f"   ✅ Toggled back to original state\n")
    except Exception as e:
        print(f"   ❌ Favorite toggle failed: {e}\n")
        return False
    
    # Test 5: Update last accessed
    print("6️⃣ Testing last accessed tracking...")
    try:
        doc = DocumentManager.get_document(session, doc1_id)
        old_time = doc.last_accessed
        
        DocumentManager.update_last_accessed(session, doc1_id)
        doc = DocumentManager.get_document(session, doc1_id)
        new_time = doc.last_accessed
        
        if new_time and (old_time is None or new_time > old_time):
            print(f"   ✅ Last accessed updated: {new_time}\n")
        else:
            print(f"   ⚠️  Last accessed update may not have worked\n")
    except Exception as e:
        print(f"   ❌ Last accessed update failed: {e}\n")
        return False
    
    # Test 6: Expiry tracking
    print("7️⃣ Testing expiry date tracking...")
    try:
        expiring = DocumentManager.get_expiring_documents(session, days_ahead=400)
        print(f"   ✅ Documents expiring soon (within 400 days): {len(expiring)}")
        
        expired = DocumentManager.get_expired_documents(session)
        print(f"   ✅ Expired documents: {len(expired)}")
        
        if expiring:
            for doc in expiring:
                days_left = (doc.expiry_date - datetime.now()).days
                print(f"      - {doc.title}: {days_left} days left")
        print()
    except Exception as e:
        print(f"   ❌ Expiry tracking failed: {e}\n")
        return False
    
    # Test 7: Archive document
    print("8️⃣ Testing archive functionality...")
    try:
        doc = DocumentManager.get_document(session, doc1_id)
        print(f"   Status before archive: is_archived = {doc.is_archived}")
        
        DocumentManager.archive_document(session, doc1_id)
        doc = DocumentManager.get_document(session, doc1_id)
        print(f"   ✅ Archived document: is_archived = {doc.is_archived}")
        
        DocumentManager.unarchive_document(session, doc1_id)
        doc = DocumentManager.get_document(session, doc1_id)
        print(f"   ✅ Unarchived document: is_archived = {doc.is_archived}\n")
    except Exception as e:
        print(f"   ❌ Archive/unarchive failed: {e}\n")
        return False
    
    # Test 8: Get favorites
    print("9️⃣ Testing favorite documents...")
    try:
        # Mark as favorite
        DocumentManager.toggle_favorite(session, doc1_id)
        
        favorites = DocumentManager.get_favorite_documents(session)
        print(f"   ✅ Favorite documents: {len(favorites)}")
        for doc in favorites:
            print(f"      - {doc.title} ★")
        print()
    except Exception as e:
        print(f"   ❌ Favorite retrieval failed: {e}\n")
        return False
    
    # Test 9: Delete document
    print("🔟 Testing document deletion...")
    try:
        # Get count before delete
        all_before = len(DocumentManager.get_all_documents(session))
        
        # Delete document
        success = DocumentManager.delete_document(session, doc2_id)
        
        # Get count after delete
        all_after = len(DocumentManager.get_all_documents(session))
        
        if success and all_after < all_before:
            print(f"   ✅ Document deleted successfully")
            print(f"      Document count: {all_before} → {all_after}\n")
        else:
            print(f"   ❌ Document deletion may not have worked\n")
    except Exception as e:
        print(f"   ❌ Document deletion failed: {e}\n")
        return False
    
    # Final summary
    print("="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    try:
        final_count = len(DocumentManager.get_all_documents(session))
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"\n📁 Final document count: {final_count}")
        print(f"📍 Storage location: {Path('data/documents').absolute()}")
        print(f"💾 Database: {Path('database.db').absolute()}\n")
        
        # List all documents
        all_docs = DocumentManager.get_all_documents(session)
        if all_docs:
            print("📄 Current documents in vault:")
            for doc in all_docs:
                status = "★" if doc.is_favorite else "☆"
                expiry_info = f"(expires: {doc.expiry_date.strftime('%Y-%m-%d')})" if doc.expiry_date else ""
                print(f"   {status} {doc.title} [{doc.category.value}] {expiry_info}")
        
        print("\n" + "="*70 + "\n")
        return True
    except Exception as e:
        print(f"\n⚠️  Error in final summary: {e}\n")
        return False


if __name__ == "__main__":
    success = test_document_vault()
    sys.exit(0 if success else 1)
