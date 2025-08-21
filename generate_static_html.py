#!/usr/bin/env python3
import boto3
import json

def main():
    """Generate static HTML from DynamoDB data with error handling"""
    
    # Get data from DynamoDB - force fresh data
    expenses = []
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ExpenseRecords')
        
        # Scan all items with pagination
        response = table.scan()
        expenses.extend(response['Items'])
        
        # Handle pagination if more than 1MB of data
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            expenses.extend(response['Items'])
        
        print(f"✅ Loaded {len(expenses)} expenses from DynamoDB")
        
        if len(expenses) == 0:
            print("⚠️  No expenses found in DynamoDB")
            
    except Exception as e:
        print(f"❌ DynamoDB error: {e}")
        print("Cannot generate dashboard without data")
        return

    # Group by category and month
    category_totals = {}
    month_totals = {}
    total_amount = 0

    for expense in expenses:
        category = expense.get('category', 'uncategorized')
        amount = float(expense.get('amount', 0))
        date = expense.get('date', expense.get('processed_at', '').split('T')[0])
        month = date[:7] if date else '2024-01'  # YYYY-MM format
        
        # Category totals
        if category not in category_totals:
            category_totals[category] = {'total': 0, 'count': 0}
        category_totals[category]['total'] += amount
        category_totals[category]['count'] += 1
        
        # Month totals
        if month not in month_totals:
            month_totals[month] = {}
        if category not in month_totals[month]:
            month_totals[month][category] = {'total': 0, 'count': 0}
        month_totals[month][category]['total'] += amount
        month_totals[month][category]['count'] += 1
        
        total_amount += amount

    # Generate HTML with actual data
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Expense Analyzer</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; font-weight: 300; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .main-content {{ padding: 40px; }}
        .month-selector {{ margin-bottom: 30px; text-align: center; }}
        .month-selector select {{ padding: 12px 20px; font-size: 1.1em; border: 2px solid #4facfe; border-radius: 10px; background: white; color: #333; cursor: pointer; }}
        .month-selector select:focus {{ outline: none; box-shadow: 0 0 10px rgba(79, 172, 254, 0.3); }}
        .total-summary {{ background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border-radius: 15px; padding: 30px; text-align: center; margin-bottom: 30px; }}
        .total-summary h2 {{ font-size: 1.5em; margin-bottom: 15px; font-weight: 500; }}
        .total-amount {{ font-size: 3em; font-weight: 700; margin-bottom: 10px; }}
        .total-items {{ font-size: 1.1em; opacity: 0.9; }}
        .month-summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; padding: 25px; text-align: center; margin-bottom: 20px; display: none; }}
        .month-summary h3 {{ font-size: 1.3em; margin-bottom: 10px; }}
        .month-amount {{ font-size: 2.2em; font-weight: 700; }}
        .category-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; }}
        .category-card {{ background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-left: 5px solid #4facfe; transition: all 0.3s ease; }}
        .category-card:hover {{ transform: translateY(-5px); box-shadow: 0 15px 40px rgba(0,0,0,0.15); }}
        .category-card h3 {{ color: #333; font-size: 1.3em; margin-bottom: 15px; font-weight: 600; text-transform: capitalize; }}
        .category-amount {{ font-size: 2.5em; font-weight: 700; color: #4facfe; margin-bottom: 10px; }}
        .category-count {{ color: #666; font-size: 1em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Smart Expense Analyzer</h1>
            <p>Expense summary dashboard</p>
        </div>
        
        <div class="main-content">
            <div class="month-selector">
                <select id="monthSelect" onchange="filterByMonth()">
                    <option value="all">All Time</option>'''

    # Add month options
    for month in sorted(month_totals.keys(), reverse=True):
        year, month_num = month.split('-')
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        html_content += f'\n                    <option value="{month}">{month_names[int(month_num)]} {year}</option>'

    html_content += f'''
                </select>
            </div>
            
            <div class="total-summary" id="totalSummary">
                <h2>Total Expenses</h2>
                <div class="total-amount">${total_amount:.2f}</div>
                <div class="total-items">{len(expenses)} items</div>
            </div>
            
            <div class="month-summary" id="monthSummary">
                <h3 id="monthTitle">Month</h3>
                <div class="month-amount" id="monthAmount">$0.00</div>
                <div id="monthItems">0 items</div>
            </div>
            
            <div class="category-grid" id="categoryGrid">
                <!-- Categories will be populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <script>
        let allExpenses = [];
        let monthData = {{}};
        let allTimeData = {{}};
        
        // API Gateway URL - will be replaced during generation
        const API_BASE = 'API_GATEWAY_URL_PLACEHOLDER';
        
        async function loadExpenseData() {{
            try {{
                console.log('Loading fresh data from API...');
                const response = await fetch(`${{API_BASE}}/expenses?t=${{Date.now()}}`, {{
                    method: 'GET',
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }});
                
                if (!response.ok) {{
                    throw new Error(`API error: ${{response.status}}`);
                }}
                
                const apiData = await response.json();
                console.log('API response:', apiData);
                
                // Handle different API response formats
                if (Array.isArray(apiData)) {{
                    allExpenses = apiData;
                }} else if (apiData.expenses && Array.isArray(apiData.expenses)) {{
                    allExpenses = apiData.expenses;
                }} else if (apiData.Items && Array.isArray(apiData.Items)) {{
                    allExpenses = apiData.Items;
                }} else {{
                    console.error('Unexpected API response format:', apiData);
                    throw new Error('API returned invalid data format');
                }}
                
                console.log(`Loaded ${{allExpenses.length}} expenses from API`);
                
                processExpenseData();
                updateUI();
                
            }} catch (error) {{
                console.error('Error loading expense data:', error);
                console.error('Error details:', error.message);
                document.getElementById('categoryGrid').innerHTML = 
                    `<div style="text-align: center; color: #666; grid-column: 1/-1;">Error: ${{error.message}}<br>Check browser console for details.</div>`;
            }}
        }}
        
        function processExpenseData() {{
            allTimeData = {{}};
            monthData = {{}};
            
            console.log('Processing', allExpenses.length, 'expenses');
            
            allExpenses.forEach((expense, index) => {{
                try {{
                    const category = expense.category || 'other';
                    const amount = parseFloat(expense.amount || 0);
                    const date = expense.date || (expense.processed_at ? expense.processed_at.split('T')[0] : '2024-01');
                    const month = date.substring(0, 7); // YYYY-MM
                    
                    if (isNaN(amount)) {{
                        console.warn(`Invalid amount for expense ${{index}}:`, expense.amount);
                        return;
                    }}
                    
                    // All-time data
                    if (!allTimeData[category]) {{
                        allTimeData[category] = {{ total: 0, count: 0 }};
                    }}
                    allTimeData[category].total += amount;
                    allTimeData[category].count += 1;
                    
                    // Monthly data
                    if (!monthData[month]) {{
                        monthData[month] = {{}};
                    }}
                    if (!monthData[month][category]) {{
                        monthData[month][category] = {{ total: 0, count: 0 }};
                    }}
                    monthData[month][category].total += amount;
                    monthData[month][category].count += 1;
                    
                }} catch (err) {{
                    console.error(`Error processing expense ${{index}}:`, err, expense);
                }}
            }});
            
            console.log('Processed categories:', Object.keys(allTimeData));
        }}
        
        function updateUI() {{
            // Update total summary
            const totalAmount = Object.values(allTimeData).reduce((sum, cat) => sum + cat.total, 0);
            const totalCount = allExpenses.length;
            
            document.getElementById('totalSummary').querySelector('.total-amount').textContent = `$${{totalAmount.toFixed(2)}}`;
            document.getElementById('totalSummary').querySelector('.total-items').textContent = `${{totalCount}} items`;
            
            // Update month selector
            const monthSelect = document.getElementById('monthSelect');
            const currentValue = monthSelect.value;
            monthSelect.innerHTML = '<option value="all">All Time</option>';
            
            Object.keys(monthData).sort().reverse().forEach(month => {{
                const [year, monthNum] = month.split('-');
                const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                const option = document.createElement('option');
                option.value = month;
                option.textContent = `${{monthNames[parseInt(monthNum)]}} ${{year}}`;
                monthSelect.appendChild(option);
            }});
            
            monthSelect.value = currentValue;
            filterByMonth();
        }}
        
        function filterByMonth() {{
            const selectedMonth = document.getElementById('monthSelect').value;
            const totalSummary = document.getElementById('totalSummary');
            const monthSummary = document.getElementById('monthSummary');
            
            if (selectedMonth === 'all') {{
                totalSummary.style.display = 'block';
                monthSummary.style.display = 'none';
                displayCategories(allTimeData);
            }} else {{
                totalSummary.style.display = 'none';
                monthSummary.style.display = 'block';
                displayMonthData(selectedMonth);
            }}
        }}
        
        function displayMonthData(month) {{
            const monthNames = {{'01': 'January', '02': 'February', '03': 'March', '04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September', '10': 'October', '11': 'November', '12': 'December'}};
            const [year, monthNum] = month.split('-');
            
            document.getElementById('monthTitle').textContent = `${{monthNames[monthNum]}} ${{year}}`;
            
            const data = monthData[month] || {{}};
            let totalAmount = 0;
            let totalCount = 0;
            
            Object.values(data).forEach(cat => {{
                totalAmount += cat.total;
                totalCount += cat.count;
            }});
            
            document.getElementById('monthAmount').textContent = `$${{totalAmount.toFixed(2)}}`;
            document.getElementById('monthItems').textContent = `${{totalCount}} items`;
            
            displayCategories(data);
        }}
        
        function displayCategories(categories) {{
            const grid = document.getElementById('categoryGrid');
            grid.innerHTML = '';
            
            console.log('Displaying categories:', categories);
            
            if (!categories || Object.keys(categories).length === 0) {{
                grid.innerHTML = '<div style="text-align: center; color: #666; grid-column: 1/-1;">No expenses found for this period.</div>';
                return;
            }}
            
            try {{
                Object.entries(categories).sort((a, b) => b[1].total - a[1].total).forEach(([category, data]) => {{
                    const card = document.createElement('div');
                    card.className = 'category-card';
                    card.innerHTML = `
                        <h3>${{category || 'Unknown'}}</h3>
                        <div class="category-amount">$${{(data.total || 0).toFixed(2)}}</div>
                        <div class="category-count">${{data.count || 0}} item${{(data.count || 0) !== 1 ? 's' : ''}}</div>
                    `;
                    grid.appendChild(card);
                }});
            }} catch (err) {{
                console.error('Error displaying categories:', err);
                grid.innerHTML = `<div style="text-align: center; color: #666; grid-column: 1/-1;">Error displaying categories: ${{err.message}}</div>`;
            }}
        }}
        
        // Load data on page load
        document.addEventListener('DOMContentLoaded', loadExpenseData);
        
        // Auto-refresh every 60 seconds (reduced frequency)
        setInterval(loadExpenseData, 60000);
    </script>
</body>
</html>'''

    # Write to file
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Add navigation buttons to the generated HTML
    html_content = html_content.replace(
        '<p>Expense summary dashboard</p>',
        '''<p>Expense summary dashboard</p>
            <div class="nav-buttons">
                <a href="upload-receipt.html" class="nav-btn">📄 Upload Receipt</a>
                <a href="#" class="nav-btn" onclick="loadExpenseData(); return false;">🔄 Refresh Data</a>
            </div>'''
    )
    
    # Add CSS for navigation buttons
    html_content = html_content.replace(
        '.header p { font-size: 1.1em; opacity: 0.9; }',
        '''.header p { font-size: 1.1em; opacity: 0.9; }
        .nav-buttons { margin-top: 20px; }
        .nav-btn { background: rgba(255,255,255,0.2); color: white; border: 2px solid rgba(255,255,255,0.3); padding: 12px 24px; margin: 0 10px; border-radius: 25px; text-decoration: none; font-weight: 500; transition: all 0.3s ease; }
        .nav-btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-2px); }'''
    )
    
    # Get API Gateway URL
    try:
        apigateway = boto3.client('apigateway')
        apis = apigateway.get_rest_apis()
        api_id = None
        for api in apis['items']:
            if 'expense' in api['name'].lower():
                api_id = api['id']
                break
        
        if api_id:
            region = boto3.Session().region_name or 'us-east-1'
            api_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
            html_content = html_content.replace('API_GATEWAY_URL_PLACEHOLDER', api_url)
            print(f"Using API URL: {api_url}")
        else:
            # Fallback to known working API
            api_url = "https://lsb82opiz7.execute-api.us-east-1.amazonaws.com/prod"
            html_content = html_content.replace('API_GATEWAY_URL_PLACEHOLDER', api_url)
            print(f"Using fallback API URL: {api_url}")

    except Exception as e:
        print(f"Error getting API URL: {e}")
    
    # Write updated content
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Upload to S3 (optional)
    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(
            'frontend/index.html',
            'expense-analyzer-frontend',
            'index.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'no-cache, no-store, must-revalidate',
                'Expires': '0'
            }
        )
        print(f'✅ Uploaded index.html to S3 ({len(expenses)} records)')
        
        # Upload upload-receipt.html
        s3_client.upload_file(
            'frontend/upload-receipt.html',
            'expense-analyzer-frontend',
            'upload-receipt.html',
            ExtraArgs={
                'ContentType': 'text/html',
                'CacheControl': 'no-cache, no-store, must-revalidate',
                'Expires': '0'
            }
        )
        print('Uploaded upload-receipt.html to S3')
        
        # Get website URL
        region = boto3.Session().region_name or 'us-east-1'
        website_url = f'http://expense-analyzer-frontend.s3-website-{region}.amazonaws.com'
        print(f'Frontend URL: {website_url}')
        print(f'Upload Page: {website_url}/upload-receipt.html')
        
    except Exception as e:
        print(f'S3 upload failed: {e}')
        print('HTML files saved locally only')
        print('Local files: frontend/index.html, upload-receipt.html')

    print('Static HTML generated successfully')
    print(f'Total: ${total_amount:.2f} ({len(expenses)} items)')
    for category, data in category_totals.items():
        print(f'  {category}: ${data["total"]:.2f} ({data["count"]} items)')
    print('\nFiles generated:')
    print('- frontend/index.html (dashboard)')
    print('- upload-receipt.html (upload page)')

if __name__ == '__main__':
    main()