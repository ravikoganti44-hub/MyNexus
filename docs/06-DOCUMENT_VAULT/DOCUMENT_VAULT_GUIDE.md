# Document Vault Feature - Complete Implementation Guide

## Overview

The **Document Vault** is a new premium feature in MyNexus that allows you to securely store, organize, and quickly access all your important documents in one centralized location. No more searching through folders or emails for critical documents!

## Key Features

### 1. **Organized Document Storage**
- Store documents by category: Passports, Tax Documents, Property Documents, Certificates, Immigration Documents, Medical Records, Insurance Documents, Financial Documents, Legal Documents, and Other
- Add sub-categories for better organization (e.g., "2024" for tax documents organized by year)
- Automatic file management with secure storage

### 2. **Document Management**
- **Upload Documents**: Upload any file type (PDF, images, Word, Excel, etc.)
- **Preview**: View documents directly within the application
- **Favorite Documents**: Mark important documents for quick access
- **Archive**: Archive old documents without deleting them
- **Search**: Search documents by title, description, tags, or reference number

### 3. **Document Tracking**
- **Expiry Dates**: Track expiration dates for passports, licenses, and other time-sensitive documents
- **Expiry Alerts**: Get notified when documents are expiring soon (within 30 days)
- **Reference Numbers**: Store document reference numbers (passport numbers, certificate numbers, etc.)
- **Last Accessed**: System tracks when each document was last viewed

### 4. **Statistics Dashboard**
- View total document count
- Monitor documents expiring soon
- Check expired documents
- Quick overview of your document collection

## Document Categories

### 📄 **All Documents**
View all documents across all categories

### 🛂 **Passports**
Store passport images and documents

### 📊 **Tax Documents**
Organize tax returns, W2 forms, 1099s, and other tax-related documents (organize by year)

### 🏠 **Property Documents**
Mortgage documents, deeds, property insurance, home improvement records

### 🎓 **Certificates**
Diplomas, certifications, licenses, and achievement certificates

### ✈️ **Immigration Documents**
Visas, immigration forms, citizenship documents, travel documents

### ⚕️ **Medical Records**
Medical reports, prescriptions, vaccination records, health documents

### 🛡️ **Insurance Documents**
Insurance policies, coverage documents, premium records

### 💰 **Financial Documents**
Bank statements, investment records, financial reports, loan documents

### ⚖️ **Legal Documents**
Contracts, agreements, legal opinions, wills

### 📎 **Other**
Any other documents that don't fit into standard categories

## How to Use

### Uploading a Document

1. Click the **📁 Document Vault** button in the sidebar
2. Click **⬆ Upload Document** button
3. Fill in the document details:
   - **File**: Click "Browse..." to select the file
   - **Title**: Give your document a meaningful name
   - **Category**: Select the appropriate category
   - **Sub-Category**: Optional (e.g., year for tax documents)
   - **Reference Number**: Optional (e.g., passport number)
   - **Issue Date**: When the document was issued
   - **Expiry Date**: When the document expires (if applicable)
   - **Description**: Add notes about the document
4. Click **Upload** to save

### Browsing Documents

1. Navigate to **Document Vault**
2. Choose a category from the left sidebar to filter documents
3. Browse the list of documents in your selected category
4. Use the search box to find specific documents

### Previewing Documents

1. Find the document you want to view
2. Click the **👁 Preview** button
3. The document will open in your default viewer (PDF viewer, image viewer, etc.)

### Managing Documents

- **Mark as Favorite**: Click the **☆** button to mark a document as favorite (becomes **★**)
- **Organize by Year**: For tax documents and recurring documents, use the sub-category field to organize by year
- **Archive**: Use the archive function to hide old documents from your main view
- **Update Metadata**: Click on a document to update its information

### Using the Tabs

#### **Browse Documents Tab**
- View all documents
- Filter by category
- Search for specific documents
- Manage individual documents

#### **Favorites Tab**
- Quick access to your most important documents
- Mark/unmark documents as favorites

#### **Statistics Tab**
- View document vault statistics
- Monitor expiring documents
- Check for expired documents

## Database Structure

The Document Vault uses the following database tables:

### `documents` Table
Stores all document metadata:
- `id`: Unique identifier
- `title`: Document name
- `category`: Document category
- `sub_category`: Optional sub-category (e.g., year)
- `file_path`: Location of the stored file
- `original_filename`: Original file name
- `stored_filename`: Unique storage name (with timestamp)
- `file_type`: Type of file (PDF, image, etc.)
- `file_size`: Size in bytes
- `issue_date`: When issued
- `expiry_date`: When expires
- `reference_number`: Document reference (passport number, etc.)
- `tags`: Search tags
- `is_favorite`: Marked as favorite
- `is_archived`: Archived status
- `is_encrypted`: Encryption status
- `created_at`: Upload date
- `updated_at`: Last modified date
- `last_accessed`: Last view date
- `notes`: User notes

## Files Modified/Created

### New Files:
1. **`src/ui/components/document_vault.py`** - Main Document Vault UI component
2. **`src/database/models.py`** - Added Document, DocumentCategory, DocumentType models
3. **`assets/icons/document_vault.svg`** - Document Vault icon

### Modified Files:
1. **`src/database/operations.py`** - Added DocumentManager class with CRUD operations
2. **`src/main.py`** - Added DocumentVaultWidget to pages stack
3. **`src/ui/components/sidebar.py`** - Added Document Vault navigation button
4. **`src/ui/styles/icon_manager.py`** - Registered document_vault icon

### New Directory:
1. **`data/documents/`** - Storage directory for uploaded documents

## API Reference

### DocumentManager Class

Located in `src/database/operations.py`

#### Creating a Document
```python
from src.database.operations import DocumentManager
from src.database.config import get_session

session = get_session()
doc = DocumentManager.create_document(
    session=session,
    title="My Passport",
    category=DocumentCategory.PASSPORT,
    file_path="/path/to/file",
    # ... other fields
)
```

#### Retrieving Documents
```python
# Get all documents
all_docs = DocumentManager.get_all_documents(session)

# Get by category
tax_docs = DocumentManager.get_documents_by_category(session, DocumentCategory.TAX_DOCUMENTS)

# Get by category and year
tax_2024 = DocumentManager.get_documents_by_subcategory(
    session, 
    DocumentCategory.TAX_DOCUMENTS, 
    "2024"
)

# Get favorites
favorites = DocumentManager.get_favorite_documents(session)

# Search documents
results = DocumentManager.search_documents(session, "passport")

# Get expiring soon
expiring = DocumentManager.get_expiring_documents(session, days_ahead=30)

# Get expired
expired = DocumentManager.get_expired_documents(session)
```

#### Updating Documents
```python
# Update document
DocumentManager.update_document(session, doc_id, title="New Title")

# Toggle favorite
DocumentManager.toggle_favorite(session, doc_id)

# Archive/Unarchive
DocumentManager.archive_document(session, doc_id)
DocumentManager.unarchive_document(session, doc_id)

# Update last accessed
DocumentManager.update_last_accessed(session, doc_id)
```

#### Deleting Documents
```python
DocumentManager.delete_document(session, doc_id)
```

## Best Practices

1. **Organize by Year**: For recurring documents like tax returns, use sub-categories to organize by year
2. **Use Reference Numbers**: Store important reference numbers (passport number, certificate number, etc.) for quick identification
3. **Set Expiry Dates**: Always set expiry dates for time-sensitive documents like passports and licenses
4. **Add Descriptions**: Include notes about where to find original documents or important details
5. **Use Favorites**: Mark critical documents as favorites for quick access
6. **Regular Backups**: The documents are stored locally; consider backing up the `data/documents/` directory

## Storage Information

- Documents are stored in: `data/documents/`
- Each file is stored with a timestamp prefix to ensure uniqueness
- Original filenames are preserved in the database for reference
- File size is tracked for storage monitoring

## Security Considerations

- Documents are stored locally on your machine
- Original files are copied to the storage directory
- Consider encrypting sensitive documents before upload
- The `is_encrypted` flag can track which documents should be encrypted
- Future versions can implement automatic encryption

## Troubleshooting

### Document Preview Not Working
- Ensure the file format is supported by your system
- Check that the file wasn't moved or deleted from the storage directory
- Try uploading the document again

### Search Not Finding Documents
- Ensure you've typed the search term correctly
- Try using different keywords (title, description, tags)
- Check that the document hasn't been archived

### Expiry Alerts Not Appearing
- Set the expiry date when uploading the document
- Restart the application to refresh the statistics

## Future Enhancements

Potential features for future versions:
- Document encryption/decryption
- Cloud backup integration
- OCR (Optical Character Recognition) for document text extraction
- Document sharing with permissions
- Advanced filtering and sorting options
- Document templates
- Batch operations
- Integration with cloud storage (Google Drive, OneDrive, Dropbox)

## Support

For issues or questions about the Document Vault feature:
1. Check the documentation above
2. Review the troubleshooting section
3. Contact the development team

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Feature Lead**: AI Assistant  
