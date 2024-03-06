# Pagination User Guide

## Overview
The dashboard now supports pagination to efficiently display 1253+ visa records.

## How to Use Pagination

### Navigation Controls
Located at the bottom of the "All Records" table:

```
[⏮ First] [◀ Previous] Page 1 of 26 (1253 records) [Next ▶] [Last ⏭] [50 per page ▼]
```

### Buttons
- **⏮ First**: Jump to the first page
- **◀ Previous**: Go to the previous page
- **Next ▶**: Go to the next page
- **Last ⏭**: Jump to the last page

### Records Per Page
Choose how many records to display per page:
- 25 per page
- 50 per page (default)
- 100 per page
- 200 per page

### Page Information
Shows: "Page X of Y (Z records)"
- X = Current page number
- Y = Total number of pages
- Z = Total number of records

## Features

### 1. Searching with Pagination
- Type in the search box to filter records
- Search automatically resets to page 1
- Pagination updates based on search results
- Search works across all fields (name, visa no, passport, employer, etc.)

### 2. Exporting Data
- Click "📥 Export CSV" to download ALL records
- Export includes all 1253+ records, not just the current page
- CSV includes all 14 fields

### 3. Other Tabs (Not Paginated)
- **Recent**: Shows last 50 records
- **By Employer**: Shows all employers with record counts
- **By Date**: Shows all dates with record counts

These tabs always show complete data for better overview.

## Examples

### Example 1: Viewing Records
1. Open dashboard
2. Click "📋 All Records" tab
3. See first 50 records (default)
4. Click "Next ▶" to see records 51-100
5. Click "Last ⏭" to jump to the last page

### Example 2: Searching
1. Type "Pakistan" in search box
2. See all Pakistani nationals (paginated)
3. Navigate through pages if more than 50 results
4. Clear search to return to all records

### Example 3: Changing Page Size
1. Click dropdown showing "50 per page"
2. Select "100 per page"
3. Now see 100 records per page
4. Fewer pages to navigate

### Example 4: Exporting
1. Search for specific records (optional)
2. Click "📥 Export CSV"
3. ALL records exported (not just current page)
4. Open CSV in Excel

## Performance Benefits

### Before Pagination
- Loading 1253 records at once
- Slow page load
- Browser lag when scrolling
- Difficult to find specific records

### After Pagination
- Loading only 50 records at a time
- Fast page load
- Smooth scrolling
- Easy navigation with page numbers
- Search works efficiently

## Tips

1. **Use Search First**: If looking for specific records, use search to narrow down results
2. **Adjust Page Size**: For quick browsing, use 100 or 200 per page
3. **Export for Analysis**: Use CSV export for detailed analysis in Excel
4. **Use Filters**: Click "View Records" in Employers or Dates tabs to filter

## Keyboard Shortcuts (Future Enhancement)
Coming soon:
- Arrow keys for page navigation
- Enter to jump to specific page
- Ctrl+F for quick search focus

---
**Dashboard URL**: http://127.0.0.1:5000
**Total Records**: 1253+
**Default Page Size**: 50 records
