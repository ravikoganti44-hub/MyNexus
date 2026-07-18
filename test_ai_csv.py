"""Test the AI-powered CSV layout detector."""
import sys
sys.path.insert(0, '.')
from src.ui.components.data_importers import _CSVLayout, _ColumnProfile

def test_summary_amt():
    """Test 1: The EXACT failing case - 'Description, , Summary Amt.'"""
    print('=== Test 1: Summary Amt. (user failing CSV) ===')
    headers = ['Description', '', 'Summary Amt.']
    rows = [
        {'Description': 'Amazon Purchase', '': '', 'Summary Amt.': '-42.99'},
        {'Description': 'Salary Deposit', '': '', 'Summary Amt.': '3200.00'},
        {'Description': 'Grocery Store', '': '', 'Summary Amt.': '-85.50'},
        {'Description': 'Netflix', '': '', 'Summary Amt.': '-15.99'},
        {'Description': 'Freelance Payment', '': '', 'Summary Amt.': '500.00'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    print(f'  method={layout.detection_method}')
    print(f'  cols={layout.col}')
    assert layout.detected, 'FAIL!'
    print('  PASS\n')

def test_garbage_headers():
    """Test 2: Totally unrecognizable headers, but real data."""
    print('=== Test 2: Unrecognizable headers, data-only detection ===')
    headers = ['Col_A', 'Col_B', 'Col_C', 'Col_D']
    rows = [
        {'Col_A': '01/15/2024', 'Col_B': 'Starbucks Coffee', 'Col_C': '-5.75', 'Col_D': '1234.25'},
        {'Col_A': '01/16/2024', 'Col_B': 'Payroll Direct Dep', 'Col_C': '2500.00', 'Col_D': '3734.25'},
        {'Col_A': '01/17/2024', 'Col_B': 'Electric Bill', 'Col_C': '-120.00', 'Col_D': '3614.25'},
        {'Col_A': '01/18/2024', 'Col_B': 'Amazon.com', 'Col_C': '-45.99', 'Col_D': '3568.26'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    print(f'  cols={layout.col}')
    assert layout.detected, 'FAIL!'
    assert layout.col['date'] == 'Col_A', f"Expected date=Col_A, got {layout.col['date']}"
    assert layout.col['description'] == 'Col_B', f"Expected desc=Col_B, got {layout.col['description']}"
    print('  PASS\n')

def test_standard_debit_credit():
    """Test 3: Standard bank format."""
    print('=== Test 3: Standard Debit/Credit columns ===')
    headers = ['Date', 'Description', 'Debit', 'Credit', 'Balance']
    rows = [
        {'Date': '2024-01-15', 'Description': 'Coffee', 'Debit': '5.75', 'Credit': '', 'Balance': '1000'},
        {'Date': '2024-01-16', 'Description': 'Salary', 'Debit': '', 'Credit': '3000', 'Balance': '4000'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    assert layout.layout_type == 'split', f'Expected split, got {layout.layout_type}'
    print('  PASS\n')

def test_amount_type():
    """Test 4: Amount + DR/CR type column."""
    print('=== Test 4: Amount + DR/CR type column ===')
    headers = ['Transaction Date', 'Particulars', 'Amount', 'Dr/Cr', 'Balance']
    rows = [
        {'Transaction Date': '15/01/2024', 'Particulars': 'ATM Withdrawal', 'Amount': '500.00', 'Dr/Cr': 'DR', 'Balance': '9500'},
        {'Transaction Date': '16/01/2024', 'Particulars': 'NEFT Credit', 'Amount': '25000', 'Dr/Cr': 'CR', 'Balance': '34500'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    assert layout.layout_type == 'amount+type', f'Expected amount+type, got {layout.layout_type}'
    print('  PASS\n')

def test_european_format():
    """Test 5: European format."""
    print('=== Test 5: European format ===')
    headers = ['Datum', 'Beschreibung', 'Betrag', 'Saldo']
    rows = [
        {'Datum': '15.01.2024', 'Beschreibung': 'REWE Supermarkt', 'Betrag': '-42,99', 'Saldo': '1.234,56'},
        {'Datum': '16.01.2024', 'Beschreibung': 'Gehalt', 'Betrag': '3.200,00', 'Saldo': '4.434,56'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    print(f'  cols={layout.col}')
    assert layout.detected, 'FAIL!'
    print('  PASS\n')

def test_indian_bank():
    """Test 6: Indian bank statement."""
    print('=== Test 6: Indian bank statement ===')
    headers = ['Txn Date', 'Narration', 'Withdrawal Amt.', 'Deposit Amt.', 'Closing Balance']
    rows = [
        {'Txn Date': '15/01/2024', 'Narration': 'UPI/Pay', 'Withdrawal Amt.': 'Rs.500.00', 'Deposit Amt.': '', 'Closing Balance': 'Rs.9,500.00'},
        {'Txn Date': '16/01/2024', 'Narration': 'NEFT/Salary', 'Withdrawal Amt.': '', 'Deposit Amt.': 'Rs.25,000.00', 'Closing Balance': 'Rs.34,500.00'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    print(f'  cols={layout.col}')
    assert layout.detected, 'FAIL!'
    print('  PASS\n')

def test_single_column_csv():
    """Test 7: Minimal single amount column with no headers matching."""
    print('=== Test 7: Minimal columns, no recognizable headers ===')
    headers = ['X', 'Y']
    rows = [
        {'X': 'Rent Payment', 'Y': '-1500.00'},
        {'X': 'Freelance', 'Y': '2000.00'},
        {'X': 'Groceries', 'Y': '-89.50'},
    ]
    layout = _CSVLayout(headers, rows)
    print(f'  detected={layout.detected}, type={layout.layout_type}')
    print(f'  cols={layout.col}')
    assert layout.detected, 'FAIL!'
    assert layout.col['description'] == 'X'
    assert layout.col['amount'] == 'Y'
    print('  PASS\n')

if __name__ == '__main__':
    test_summary_amt()
    test_garbage_headers()
    test_standard_debit_credit()
    test_amount_type()
    test_european_format()
    test_indian_bank()
    test_single_column_csv()
    print('All 7 tests passed!')
