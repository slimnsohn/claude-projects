# Credit Card Statement Analyzer

A local web application for analyzing credit card statements from CSV files.

## Features

- **Drag & Drop Upload**: Simply drag your CSV file onto the webpage
- **Smart CSV Parsing**: Automatically detects common CSV formats from major banks
- **Transaction Categorization**: Auto-categorizes transactions (Food, Shopping, Gas, etc.)
- **Visual Analytics**: 
  - Spending by category (doughnut chart)
  - Daily spending trends (line chart)
  - Summary cards with key metrics
- **Transaction Table**: Detailed view of all transactions
- **Responsive Design**: Works on desktop and mobile

## How to Use

1. Open `index.html` in your web browser
2. Download a CSV statement from your bank
3. Drag and drop the CSV file onto the upload area
4. View your spending analysis instantly

## Supported CSV Formats

The app automatically detects and handles various CSV formats including:
- Date columns: "Date", "Transaction Date", "Posted Date"
- Description columns: "Description", "Transaction", "Merchant", "Memo"
- Amount columns: "Amount", "Debit", "Credit", "Transaction Amount"

## Privacy

- **100% Local**: All processing happens in your browser
- **No Data Upload**: Your financial data never leaves your computer
- **No Tracking**: No analytics or tracking code

## Browser Requirements

- Modern web browser with JavaScript enabled
- No additional software installation required

## File Structure

- `index.html` - Main application page
- `styles.css` - Styling and responsive design
- `script.js` - Core application logic and CSV processing
- `README.md` - This documentation