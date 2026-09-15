"""
Script to import invoice data from JSON file into database
Run this after updating your Excel files to sync data to the cloud
"""
import json
import sys
from datetime import datetime
from sqlalchemy.orm import Session

from database import SessionLocal, Invoice, LineItem, init_db


def import_from_json(json_file_path: str):
    """Import data from invoice_data_complete.json into database"""

    # Initialize database
    init_db()

    # Load JSON data
    print(f"Loading data from {json_file_path}...")
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    db = SessionLocal()

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(LineItem).delete()
        db.query(Invoice).delete()
        db.commit()

        # Import invoices
        print(f"Importing {len(data['invoices'])} invoices...")
        for inv_data in data['invoices']:
            # Parse date
            invoice_date = None
            if inv_data['invoice_date'] and inv_data['invoice_date'] != 'N/A':
                try:
                    invoice_date = datetime.strptime(inv_data['invoice_date'], '%Y-%m-%d').date()
                except:
                    pass

            invoice = Invoice(
                invoice_no=inv_data['invoice_no'],
                invoice_date=invoice_date,
                customer=inv_data['customer'],
                ship_via=inv_data.get('ship_via', 'No shipping'),
                total_amount=inv_data['total_amount'],
                line_item_count=inv_data['line_item_count'],
                filename=inv_data.get('filename', '')
            )
            db.add(invoice)

        db.commit()
        print(f"✓ Imported {len(data['invoices'])} invoices")

        # Import line items
        print(f"Importing {len(data['line_items'])} line items...")
        for item_data in data['line_items']:
            line_item = LineItem(
                invoice_no=item_data['invoice_no'],
                p_n=item_data['p_n'],
                description=item_data.get('description', ''),
                qty=item_data['qty'],
                price_unit=item_data['price_unit'],
                amount=item_data['amount']
            )
            db.add(line_item)

        db.commit()
        print(f"✓ Imported {len(data['line_items'])} line items")

        print("\n✅ Data import completed successfully!")

    except Exception as e:
        print(f"❌ Error importing data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Default to the invoice_data_complete.json in parent directory
    json_path = "../invoice_data_complete.json"

    if len(sys.argv) > 1:
        json_path = sys.argv[1]

    import_from_json(json_path)
