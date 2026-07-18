# Document Vault - Technical Implementation Details

## Architecture Overview

The Document Vault feature follows the existing MyNexus architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Vault UI                         │
│           (src/ui/components/document_vault.py)              │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
    ┌────▼─────────────────┐   ┌────────▼──────────────┐
    │   Database Models     │   │  Database Operations │
    │ (src/database/        │   │ (src/database/       │
    │  models.py)           │   │  operations.py)      │
    │ - Document            │   │ - DocumentManager    │
    │ - DocumentCategory    │   │   (CRUD operations)  │
    │ - DocumentType        │   │                      │
    └────┬─────────────────┘   └────────┬──────────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
         ┌──────────────▼──────────────┐
         │   SQLite Database           │
         │ (database.db)               │
         │ - documents table           │
         └─────────────────────────────┘
         
         ┌──────────────────────────────────┐
         │   File Storage                   │
         │ (data/documents/)                │
         │ - Uploaded document files        │
         │ - Named with timestamp prefix    │
         └──────────────────────────────────┘
```

## Component Structure

### 1. Database Models (src/database/models.py)

**DocumentCategory Enum**
```python
PASSPORT = "passport"
TAX_DOCUMENTS = "tax_documents"
PROPERTY_DOCUMENTS = "property_documents"
CERTIFICATES = "certificates"
IMMIGRATION_DOCUMENTS = "immigration_documents"
MEDICAL_RECORDS = "medical_records"
INSURANCE_DOCUMENTS = "insurance_documents"
FINANCIAL_DOCUMENTS = "financial_documents"
LEGAL_DOCUMENTS = "legal_documents"
OTHER = "other"
```

**DocumentType Enum**
```python
PDF = "pdf"
IMAGE = "image"
WORD = "word"
EXCEL = "excel"
TEXT = "text"
OTHER = "other"
```

**Document Model**
Primary table storing document metadata and references.

### 2. Database Operations (src/database/operations.py)

**DocumentManager Class** - Provides all CRUD operations:

**Create Operations:**
- `create_document()` - Create new document entry

**Read Operations:**
- `get_document()` - Get single document by ID
- `get_all_documents()` - Get all non-archived documents
- `get_documents_by_category()` - Filter by category
- `get_documents_by_subcategory()` - Filter by category and sub-category
- `get_favorite_documents()` - Get starred documents
- `get_expiring_documents()` - Get documents expiring within X days
- `get_expired_documents()` - Get expired documents
- `search_documents()` - Full-text search

**Update Operations:**
- `update_document()` - Update metadata
- `toggle_favorite()` - Toggle favorite status
- `archive_document()` - Archive document
- `unarchive_document()` - Restore archived document
- `update_last_accessed()` - Update access timestamp

**Delete Operations:**
- `delete_document()` - Permanently delete document

### 3. UI Component (src/ui/components/document_vault.py)

**DocumentVaultWidget** - Main UI container with tabbed interface

**Tabs:**
1. **Browse Documents Tab**
   - Category sidebar for filtering
   - Documents table with display options
   - Search and filter functionality
   - Preview and favorite buttons

2. **Favorites Tab**
   - Table of favorite documents
   - Quick access to important files
   - Remove from favorites option

3. **Statistics Tab**
   - Document count statistics
   - Expiring documents list
   - Expired documents count
   - Visual indicators for alerts

**DocumentUploadDialog** - Modal dialog for uploading new documents
- File selection with browser
- Document metadata input
- Category selection
- Date pickers for issue/expiry dates
- Notes/description field

## Data Flow

### Upload Flow
```
User Clicks Upload
    ↓
DocumentUploadDialog Opens
    ↓
User Selects File + Metadata
    ↓
Dialog Validates Input
    ↓
File Copied to data/documents/ (with timestamp)
    ↓
DocumentManager.create_document() called
    ↓
Document Record Inserted into Database
    ↓
UI Refreshed with New Document
```

### Preview Flow
```
User Clicks Preview Button
    ↓
DocumentManager.update_last_accessed() called
    ↓
File Path Retrieved from Database
    ↓
os.startfile() Opens Default Viewer
    ↓
Document Opens in System Viewer
```

### Search/Filter Flow
```
User Types Search Term
    ↓
DocumentManager.search_documents() called
    ↓
Database Query (Title/Description/Tags)
    ↓
Results Displayed in Table
    ↓
User Can Preview or Manage Results
```

## File Storage Strategy

### Naming Convention
```
TIMESTAMP_ORIGINALNAME.EXT
Example: 20260330_143022_MyPassport.pdf
```

### Directory Structure
```
data/
├── documents/
│   ├── 20260330_143022_passport.pdf
│   ├── 20260330_143045_tax_2024.pdf
│   ├── 20260330_143102_mortgage_deed.jpg
│   └── ... more files
```

### Why Timestamp Prefix?
1. **Uniqueness**: Avoids filename collisions
2. **Chronological Sorting**: Files naturally sort by upload time
3. **Traceability**: Easy to identify when files were added
4. **Recovery**: Timestamp helps correlate with database records

## Key Implementation Details

### 1. Date Handling
- Uses `datetime.datetime` for all date operations
- Timezone-aware operations where needed
- Expiry calculation uses `timedelta` for reliable date math

### 2. File Type Detection
- Determined by file extension
- Supported types: PDF, Image, Word, Excel, Text, Other
- Used for UI display and future filtering

### 3. Prevention of Data Loss
- Original filename preserved in database
- Stored filename timestamp ensures no overwrites
- Database maintains complete audit trail

### 4. Search Implementation
- Uses SQLAlchemy's `ilike()` for case-insensitive search
- Searches: title, description, tags, reference_number
- Excludes archived documents by default

### 5. Statistics Calculation
- All counts use filtered queries
- Expiry dates calculated using `timedelta(days=30)`
- Performance optimized with database indexes on frequently searched fields

## Integration Points

### With Main Application
1. **Sidebar Navigation** - New button in navigation
2. **Status Bar** - Shows current page name
3. **Database** - Uses existing database session management
4. **Styling** - Inherits application stylesheet

### Database Integration
1. **Session Management** - Uses `get_session()` from config
2. **Transaction Handling** - Automatic commit on operations
3. **Model Relationships** - Independent, no foreign key dependencies

## Performance Considerations

### Database Optimization
- Indexed fields: `title`, `category`, `created_at`
- Queries filtered by `is_archived` status for faster retrieval
- Separate expiry date query for alert calculations

### UI Optimization
- Table data loaded incrementally
- Search debouncing (text changed signal)
- File operations in background where possible

### Memory Management
- Document list loaded on demand
- Statistics calculated on tab switch
- File preview uses system viewers (no in-memory loading)

## Error Handling

All operations include try-except blocks for:
1. File I/O errors (file not found, permission denied)
2. Database errors (connection issues, constraint violations)
3. User input validation (missing required fields)
4. System errors (file already exists, insufficient space)

## Security Features (Current)

1. **Local Storage** - Documents stored on user's machine
2. **Database Record** - Metadata tracked in database
3. **Encryption Ready** - `is_encrypted` flag for future implementation
4. **Access Logging** - `last_accessed` timestamp tracks viewing

## Security Features (Planned)

1. **File Encryption** - Encrypt sensitive documents at rest
2. **Password protection** - Encrypt documents with user password
3. **Audit Trail** - Full logging of document access
4. **Cloud Backup** - Optional encrypted cloud storage

## Configuration

### Default Directories
- Storage: `data/documents/`
- Created automatically if missing
- Configurable future enhancement

### Document Retention
- Soft delete via archive status
- Hard delete supported for cleanup
- Expiry tracking for compliance

## Testing Scenarios

1. **Upload a document** - Verify file copying and database entry
2. **Preview document** - Verify file opens in default viewer
3. **Search documents** - Test various search terms
4. **Filter by category** - Verify proper sorting
5. **Mark as favorite** - Toggle favorite status
6. **Archive/unarchive** - Test status changes
7. **Check expiry alerts** - Set future expiry dates
8. **Statistics display** - Verify counts are accurate

## Dependencies

### Required Packages
- PyQt6 - UI framework (already in requirements.txt)
- SQLAlchemy - ORM (already in requirements.txt)
- Python stdlib:
  - `os` - File operations
  - `shutil` - Copy operations
  - `pathlib.Path` - Path handling
  - `datetime` - Date/time handling
  - `json` - Metadata storage (future)

### No External Dependencies Added

## Future Enhancement Roadmap

### Phase 2
- Document encryption/decryption
- Advanced search with date range filters
- Bulk operations (upload multiple, delete multiple)
- Export functionality (zip, PDF, etc.)

### Phase 3
- Cloud integration (Google Drive, OneDrive, Dropbox)
- Document sharing with permissions
- Collaborative features
- Mobile app sync

### Phase 4
- OCR (Optical Character Recognition)
- Document templates
- E-signature support
- Blockchain validation

## Maintenance Notes

### Backup Strategy
Users should periodically backup:
- `data/documents/` directory
- `database.db` file (contains metadata)

### Cleanup
- Archived documents don't affect storage until deleted
- Monitor `data/documents/` size for space management
- Consider batch deletion for old documents

### Migration Path
If users need to move their vault:
1. Export database
2. Copy `data/documents/` folder
3. Import database in new location
4. Verify file paths are accessible

---

**Last Updated**: March 2026  
**Version**: 1.0  
**Status**: Production Ready
