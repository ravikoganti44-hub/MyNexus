"""Test the AI importer against the user's actual Bank of America CSV."""
import sys, csv, io
sys.path.insert(0, '.')
from src.ui.components.data_importers import _CSVLayout, BankStatementImportDialog, _parse_amount

# Read actual file
with open(r'c:\Users\owner\Downloads\stmt.csv', 'r', encoding='utf-8-sig') as f:
    content = f.read()

print('=== Raw file structure ===')
lines = content.splitlines()
for i, line in enumerate(lines[:10], 1):
    print(f'  {i}: {line[:100]}')
print(f'  ... ({len(lines)} total lines)')

print()
print('=== After _skip_preamble ===')
cleaned = BankStatementImportDialog._skip_preamble(content)
clean_lines = cleaned.splitlines()
for i, line in enumerate(clean_lines[:5], 1):
    print(f'  {i}: {line[:100]}')

print()
print('=== CSV parsing ===')
reader = csv.DictReader(io.StringIO(cleaned))
headers = reader.fieldnames
print(f'Headers: {headers}')
rows = list(reader)
print(f'Row count: {len(rows)}')

print()
print('=== Layout detection ===')
layout = _CSVLayout(headers, rows)
print(f'detected={layout.detected}, type={layout.layout_type}')
print(f'method={layout.detection_method}')
for role, h in layout.col.items():
    if h:
        prof = layout.profiles.get(h)
        dtype = prof.inferred_type if prof else '?'
        print(f'  {role:>12s} -> {h}  (data type: {dtype})')

print()
print('=== Transaction extraction ===')
dialog = BankStatementImportDialog.__new__(BankStatementImportDialog)
dialog._layout = layout
total_debits = 0
total_credits = 0
n_debit = 0
n_credit = 0
for i, row in enumerate(rows):
    txn = dialog._extract_transaction(row)
    if txn:
        symbol = '📉' if txn['type'] == 'debit' else '📈'
        print(f"  {symbol} {txn['date'].strftime('%m/%d/%Y'):>10}  {txn['type']:>6}  "
              f"${txn['amount']:>10,.2f}  {txn['category']:<20}  {txn['description'][:50]}")
        if txn['type'] == 'debit':
            total_debits += txn['amount']
            n_debit += 1
        else:
            total_credits += txn['amount']
            n_credit += 1

print()
print(f'=== Summary ===')
print(f'  {n_debit} debits:  ${total_debits:,.2f}')
print(f'  {n_credit} credits: ${total_credits:,.2f}')
print(f'  Net:     ${total_credits - total_debits:,.2f}')
print()

# Verify against statement totals
expected_credits = 28028.76
expected_debits = 9632.12
print(f'  Statement says: credits=${expected_credits:,.2f}, debits=${expected_debits:,.2f}')
credit_match = abs(total_credits - expected_credits) < 1
debit_match = abs(total_debits - expected_debits) < 1
print(f'  Credits match: {credit_match} (diff=${abs(total_credits - expected_credits):.2f})')
print(f'  Debits match:  {debit_match} (diff=${abs(total_debits - expected_debits):.2f})')

if credit_match and debit_match:
    print('\n  ✅ ALL TOTALS MATCH THE STATEMENT!')
else:
    print('\n  ⚠️ Totals differ — check parsing')
