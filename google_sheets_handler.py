"""
Google Sheets Integration Handler
==================================
Handles registration data submission to Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os


class GoogleSheetsHandler:
    """Manages Google Sheets API interactions for registration data"""
    
    def __init__(self, credentials_file="credentials.json", sheet_name="Registrations"):
        """
        Initialize Google Sheets handler
        
        Args:
            credentials_file: Path to Google service account credentials JSON
            sheet_name: Name of the Google Sheet to use
        """
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        self.client = None
        self.sheet = None
        self.worksheet = None
        self.is_authenticated = False
        
    def authenticate(self):
        """Authenticate with Google Sheets API using service account credentials"""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                "Please create a Google Service Account and download credentials.json\n"
                "Instructions: https://docs.gspread.org/en/latest/oauth2.html"
            )
        
        try:
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scope
            )
            
            self.client = gspread.authorize(creds)
            self.is_authenticated = True
            return True
        except Exception as e:
            raise Exception(f"Authentication failed: {str(e)}")
    
    def open_sheet(self, spreadsheet_url_or_name):
        """
        Open a Google Sheet
        
        Args:
            spreadsheet_url_or_name: Sheet URL or spreadsheet name
        """
        if not self.is_authenticated:
            self.authenticate()
            
        try:
            if spreadsheet_url_or_name.startswith('http'):
                self.sheet = self.client.open_by_url(spreadsheet_url_or_name)
            else:
                self.sheet = self.client.open(spreadsheet_url_or_name)
            
            # Get or create worksheet
            try:
                self.worksheet = self.sheet.worksheet(self.sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(title=self.sheet_name, rows=100, cols=10)
                self._initialize_headers()
            
            return True
        except Exception as e:
            raise Exception(f"Failed to open sheet: {str(e)}")
    
    def _initialize_headers(self):
        """Initialize worksheet headers"""
        headers = ['Timestamp', 'Name', 'College', 'Batch', 'Phone']
        self.worksheet.insert_row(headers, index=1)
    
    def add_registration(self, name, college, batch, phone):
        """
        Add a new registration record
        
        Args:
            name: Student name
            college: College name
            batch: Academic year/batch
            phone: Phone number
            
        Returns:
            dict: Response with success status and message
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            row = [timestamp, name, college, batch, phone]
            
            self.worksheet.append_row(row)
            return {
                'success': True,
                'message': f'Registration successful for {name}!'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding registration: {str(e)}'
            }
    
    def get_all_registrations(self):
        """
        Retrieve all registrations
        
        Returns:
            list: List of registration records
        """
        try:
            records = self.worksheet.get_all_records()
            return records
        except Exception as e:
            raise Exception(f"Failed to retrieve registrations: {str(e)}")


if __name__ == "__main__":
    print("Google Sheets handler module loaded successfully")
