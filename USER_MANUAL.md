# Smart Expense Analyzer - User Manual

## Getting Started

### What is Smart Expense Analyzer?
Smart Expense Analyzer is an intelligent expense management tool that automatically processes your receipts and invoices using AI-powered OCR technology. Simply upload a photo of your receipt, and the system will extract key information like amount, date, vendor, and category.

### Key Features
- **Automatic OCR Processing**: Extract text from receipt images and PDFs
- **Smart Categorization**: Automatically categorize expenses (food, transport, office, etc.)
- **Web Dashboard**: View and manage expenses through an intuitive interface
- **Mobile-Friendly**: Works on smartphones, tablets, and desktop computers
- **Secure Storage**: All data encrypted and stored securely in AWS cloud

## Accessing the Application

### Web Interface
1. Open your web browser
2. Navigate to: `http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com`
3. The dashboard will load automatically

### System Requirements
- **Web Browser**: Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet Connection**: Required for uploading and processing
- **File Formats**: JPEG, PNG, PDF files up to 10MB

## Uploading Receipts

### Step-by-Step Upload Process

1. **Access Upload Section**
   - Click the "Upload Receipt" button on the main dashboard
   - Or navigate directly to the upload page at `/upload-receipt.html`
   - Or drag and drop files directly onto the upload area

2. **Select Your Receipt**
   - Click "Choose File" to browse your device
   - Select a clear photo or scan of your receipt
   - Supported formats: .jpg, .jpeg, .png, .pdf

3. **Upload and Processing**
   - Click "Upload" to start processing
   - Wait for the "Processing..." indicator
   - Processing typically takes 5-15 seconds

4. **Review Extracted Data**
   - System will display extracted information
   - Verify amount, date, vendor, and category
   - Make corrections if needed

### Tips for Best Results

**Photo Quality**:
- Ensure receipt is well-lit and in focus
- Avoid shadows and glare
- Capture the entire receipt including totals
- Hold camera steady to prevent blur

**Receipt Condition**:
- Flatten crumpled receipts before photographing
- Clean any dirt or stains that might obscure text
- For faded receipts, try adjusting lighting

**File Size**:
- Keep files under 10MB for faster processing
- Compress large images if necessary
- PDF files should be text-based, not scanned images

## Using the Dashboard

### Main Dashboard Overview
The dashboard displays your expense data in an organized, easy-to-read format.

**Dashboard Sections**:
- **Summary Cards**: Total expenses, monthly spending, category breakdown
- **Recent Expenses**: Latest uploaded receipts and their details
- **Monthly View**: Calendar-style view of expenses by date
- **Category Charts**: Visual breakdown of spending by category

### Filtering and Searching

**Filter by Month**:
1. Use the month selector dropdown
2. Choose desired month/year
3. Dashboard updates automatically

**Filter by Category**:
1. Click on category filter buttons
2. Select one or multiple categories
3. View filtered results instantly

**Search Expenses**:
1. Use the search box at the top
2. Search by vendor name, description, or amount
3. Results update as you type

### Viewing Expense Details

**Individual Expense View**:
1. Click on any expense in the list
2. View detailed information including:
   - Original receipt image
   - Extracted text data
   - Processing confidence score
   - Edit options

**Bulk Operations**:
- Select multiple expenses using checkboxes
- Export selected expenses to CSV
- Delete multiple expenses at once

## Managing Your Expenses

### Editing Expense Information

1. **Access Edit Mode**
   - Click the "Edit" button on any expense
   - Or double-click on editable fields

2. **Modify Details**
   - Update amount, category, description, or vendor
   - Changes are saved automatically
   - Original receipt image remains unchanged

3. **Category Management**
   - Choose from predefined categories:
     - Food & Dining
     - Transportation
     - Office Supplies
     - Healthcare
     - Entertainment
     - Utilities
     - Other

### Deleting Expenses

**Single Expense**:
1. Click the trash icon next to the expense
2. Confirm deletion in the popup dialog
3. Expense is permanently removed

**Multiple Expenses**:
1. Select expenses using checkboxes
2. Click "Delete Selected" button
3. Confirm bulk deletion

### Exporting Data

**Export Options**:
- **CSV Format**: Spreadsheet-compatible file
- **PDF Report**: Formatted expense report
- **JSON Data**: Raw data for developers

**Export Process**:
1. Select date range or specific expenses
2. Choose export format
3. Click "Export" button
4. Download file to your device

## Mobile Usage

### Mobile Web Interface
The application is fully responsive and works on mobile devices.

**Mobile Features**:
- Touch-friendly interface
- Camera integration for direct photo capture
- Swipe gestures for navigation
- Optimized for small screens

### Taking Photos on Mobile

1. **Camera Access**
   - Tap "Upload Receipt" button
   - Allow camera permissions when prompted
   - Use "Take Photo" option

2. **Photo Guidelines**
   - Hold phone steady
   - Ensure receipt fills most of the frame
   - Tap to focus on the receipt text
   - Use good lighting (avoid flash if possible)

3. **Review and Upload**
   - Preview photo before uploading
   - Retake if image is unclear
   - Tap "Upload" to process

## Troubleshooting

### Common Issues and Solutions

**Upload Problems**:
- *File too large*: Compress image or use lower resolution
- *Unsupported format*: Convert to JPEG, PNG, or PDF
- *Upload fails*: Check internet connection and try again

**Processing Issues**:
- *Poor text extraction*: Retake photo with better lighting
- *Wrong category*: Manually edit the category after processing
- *Missing information*: Add details manually in edit mode

**Dashboard Problems**:
- *Expenses not showing*: Refresh page or check date filters
- *Slow loading*: Clear browser cache and cookies
- *Display issues*: Try a different browser or update current one

### Getting Help

**Self-Service Options**:
- Check this user manual for detailed instructions
- Review FAQ section for common questions
- Use the built-in help tooltips throughout the interface

**Contact Support**:
- Email: support@expense-analyzer.com
- Response time: Within 24 hours
- Include screenshots and error messages when reporting issues

## Frequently Asked Questions

**Q: Is my data secure?**
A: Yes, all data is encrypted and stored securely in AWS cloud infrastructure with enterprise-grade security.

**Q: Can I access my expenses from multiple devices?**
A: Yes, your expenses are stored in the cloud and accessible from any device with internet access.

**Q: What happens if OCR extraction is incorrect?**
A: You can manually edit any extracted information. The system learns from corrections to improve accuracy.

**Q: Can I upload receipts in languages other than English?**
A: Currently, the system works best with English receipts. Multi-language support is planned for future releases.

**Q: Is there a limit to how many receipts I can upload?**
A: There are no hard limits, but very large volumes may incur additional AWS costs.

**Q: Can I integrate this with my accounting software?**
A: Data can be exported in CSV format for import into most accounting systems. API integration is available for developers.

## Tips and Best Practices

### Maximizing Accuracy
- Take photos in good lighting conditions
- Ensure receipts are flat and fully visible
- Keep receipts organized and upload promptly
- Review and correct extracted data when necessary

### Organizing Expenses
- Use consistent vendor names for better tracking
- Add detailed descriptions for unclear purchases
- Regularly review and categorize expenses
- Export data monthly for backup purposes

### Privacy and Security
- Log out when using shared computers
- Don't share your access credentials
- Regularly review your expense data for accuracy
- Report any suspicious activity immediately

## Advanced Features

### Bulk Upload
- Select multiple files at once
- Drag and drop multiple receipts
- Batch processing for efficiency
- Progress tracking for large uploads

### Data Analytics
- Monthly spending trends
- Category-wise analysis
- Vendor spending patterns
- Custom date range reports

### Integration Options
- REST API for developers
- Webhook notifications
- CSV/JSON data export
- Third-party accounting software compatibility