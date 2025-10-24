
# 1. integrations/google_sheets.py - Google Sheets Integration
google_sheets_code = '''"""
Google Sheets Integration for Product Price Tracker
Sync price data with Google Sheets
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsSync:
    """Sync product price data with Google Sheets"""
    
    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize Google Sheets client
        
        Args:
            credentials_file: Path to Google service account JSON credentials
        """
        self.credentials_file = credentials_file
        self.client = None
        self.connect()
    
    def connect(self):
        """Connect to Google Sheets API"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, 
                scope
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Connected to Google Sheets successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            self.client = None
    
    def create_spreadsheet(self, title: str) -> str:
        """
        Create a new Google Spreadsheet
        
        Args:
            title: Spreadsheet title
            
        Returns:
            Spreadsheet URL
        """
        try:
            spreadsheet = self.client.create(title)
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}"
            logger.info(f"Created spreadsheet: {title}")
            return url
            
        except Exception as e:
            logger.error(f"Error creating spreadsheet: {e}")
            return None
    
    def export_products(self, spreadsheet_name: str, products: List[Dict]) -> bool:
        """
        Export product data to Google Sheets
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            products: List of product dictionaries
            
        Returns:
            Success status
        """
        try:
            # Open or create spreadsheet
            try:
                spreadsheet = self.client.open(spreadsheet_name)
            except gspread.SpreadsheetNotFound:
                logger.info(f"Spreadsheet '{spreadsheet_name}' not found, creating new one")
                self.create_spreadsheet(spreadsheet_name)
                spreadsheet = self.client.open(spreadsheet_name)
            
            # Get first worksheet
            worksheet = spreadsheet.sheet1
            
            # Clear existing data
            worksheet.clear()
            
            # Prepare headers
            headers = [
                'Product Name', 
                'Site', 
                'Current Price', 
                'Alert Price',
                'Last Updated', 
                'Status',
                'Category'
            ]
            
            # Write headers
            worksheet.append_row(headers)
            
            # Format header row
            worksheet.format('A1:G1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.8},
                'horizontalAlignment': 'CENTER'
            })
            
            # Write product data
            for product in products:
                status = 'ALERT' if (
                    product.get('alert_price') and 
                    product.get('current_price') and 
                    product['current_price'] <= product['alert_price']
                ) else 'OK'
                
                row = [
                    product.get('name', 'N/A'),
                    product.get('site', 'N/A'),
                    f"${product.get('current_price', 0):.2f}" if product.get('current_price') else 'N/A',
                    f"${product.get('alert_price', 0):.2f}" if product.get('alert_price') else 'N/A',
                    product.get('last_updated', 'N/A'),
                    status,
                    product.get('category', 'Other')
                ]
                
                worksheet.append_row(row)
            
            # Auto-resize columns
            worksheet.columns_auto_resize(0, len(headers))
            
            # Color code status column
            self._color_code_status(worksheet, len(products))
            
            logger.info(f"Exported {len(products)} products to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to Google Sheets: {e}")
            return False
    
    def export_price_history(self, spreadsheet_name: str, 
                            history_data: pd.DataFrame) -> bool:
        """
        Export price history to a separate sheet
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            history_data: DataFrame with price history
            
        Returns:
            Success status
        """
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            
            # Create or get price history worksheet
            try:
                worksheet = spreadsheet.worksheet('Price History')
            except gspread.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(
                    title='Price History', 
                    rows=1000, 
                    cols=10
                )
            
            # Clear existing data
            worksheet.clear()
            
            # Convert DataFrame to list of lists
            data = [history_data.columns.tolist()] + history_data.values.tolist()
            
            # Update worksheet
            worksheet.update('A1', data)
            
            # Format header
            worksheet.format('A1:Z1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.3, 'green': 0.6, 'blue': 0.4}
            })
            
            logger.info(f"Exported {len(history_data)} price records to Google Sheets")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting price history: {e}")
            return False
    
    def _color_code_status(self, worksheet, num_rows: int):
        """Color code the status column based on values"""
        try:
            # Get status column (F column, index 6)
            status_values = worksheet.col_values(6)[1:]  # Skip header
            
            for i, status in enumerate(status_values, start=2):  # Start from row 2
                cell_range = f'F{i}'
                
                if status == 'ALERT':
                    # Red background for alerts
                    worksheet.format(cell_range, {
                        'backgroundColor': {'red': 1.0, 'green': 0.4, 'blue': 0.4},
                        'textFormat': {'bold': True}
                    })
                else:
                    # Green background for OK
                    worksheet.format(cell_range, {
                        'backgroundColor': {'red': 0.7, 'green': 1.0, 'blue': 0.7}
                    })
                    
        except Exception as e:
            logger.warning(f"Could not color code status column: {e}")
    
    def read_products(self, spreadsheet_name: str) -> List[Dict]:
        """
        Read products from Google Sheets
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            
        Returns:
            List of product dictionaries
        """
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            worksheet = spreadsheet.sheet1
            
            # Get all records
            records = worksheet.get_all_records()
            
            logger.info(f"Read {len(records)} products from Google Sheets")
            return records
            
        except Exception as e:
            logger.error(f"Error reading from Google Sheets: {e}")
            return []
    
    def update_product_price(self, spreadsheet_name: str, 
                            product_name: str, new_price: float) -> bool:
        """
        Update a specific product's price
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            product_name: Product to update
            new_price: New price value
            
        Returns:
            Success status
        """
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            worksheet = spreadsheet.sheet1
            
            # Find the product row
            cell = worksheet.find(product_name)
            
            if cell:
                # Update price in column C (3rd column)
                worksheet.update_cell(cell.row, 3, f"${new_price:.2f}")
                logger.info(f"Updated price for {product_name} to ${new_price:.2f}")
                return True
            else:
                logger.warning(f"Product {product_name} not found in sheet")
                return False
                
        except Exception as e:
            logger.error(f"Error updating product price: {e}")
            return False
    
    def share_spreadsheet(self, spreadsheet_name: str, 
                         email: str, role: str = 'reader') -> bool:
        """
        Share spreadsheet with an email address
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            email: Email to share with
            role: Permission level ('reader', 'writer', 'owner')
            
        Returns:
            Success status
        """
        try:
            spreadsheet = self.client.open(spreadsheet_name)
            spreadsheet.share(email, perm_type='user', role=role)
            
            logger.info(f"Shared spreadsheet with {email} as {role}")
            return True
            
        except Exception as e:
            logger.error(f"Error sharing spreadsheet: {e}")
            return False
    
    def create_chart(self, spreadsheet_name: str, 
                    worksheet_name: str = 'Sheet1') -> bool:
        """
        Create a price trend chart (advanced feature)
        
        Args:
            spreadsheet_name: Name of the spreadsheet
            worksheet_name: Worksheet to add chart to
            
        Returns:
            Success status
        """
        try:
            # Note: Chart creation via API is complex
            # This is a placeholder for advanced implementation
            logger.info("Chart creation requires Google Sheets API v4")
            logger.info("Charts can be created manually or via advanced API")
            return False
            
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize (requires credentials.json file)
    try:
        sheets = GoogleSheetsSync("credentials.json")
        
        # Example: Export sample products
        sample_products = [
            {
                'name': 'iPhone 15 Pro',
                'site': 'Amazon',
                'current_price': 999.99,
                'alert_price': 950.00,
                'last_updated': '2025-10-20 10:00:00',
                'category': 'Electronics'
            },
            {
                'name': 'Sony Headphones',
                'site': 'Flipkart',
                'current_price': 299.99,
                'alert_price': 250.00,
                'last_updated': '2025-10-20 10:05:00',
                'category': 'Electronics'
            }
        ]
        
        sheets.export_products("Price Tracker Data", sample_products)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have credentials.json file from Google Cloud Console")
'''

print("✅ integrations/google_sheets.py code created!")
