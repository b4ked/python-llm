# PDF Batch Processing Script

This script (`process_all_pdfs.sh`) processes all PDF files in the `reports` folder using the `openai-pdf-db.py` script and stores the extracted text content in a PostgreSQL database.

## Features

- 🔍 **Automatic Discovery**: Finds all PDF files in the reports directory
- 📊 **Progress Tracking**: Real-time progress bar and status updates
- 🎨 **Colored Output**: Easy-to-read colored terminal output
- 📝 **Detailed Logging**: Comprehensive log file with timestamps
- ⚡ **Error Handling**: Continues processing even if individual files fail
- 📈 **Summary Report**: Final summary with success/error counts
- 🛡️ **Prerequisites Check**: Validates environment before processing
- 💾 **Database Integration**: Stores extracted text in PostgreSQL database

## Prerequisites

1. **Python 3** installed and accessible via `python3` command
2. **OpenAI API Key** set as environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. **PostgreSQL Database** configured and accessible (see main README-DB.md)
4. **Required Python packages** installed (openai, psycopg2, etc.)

## Usage

### Basic Usage

```bash
# Navigate to the openai-pdf directory
cd openai-pdf

# Run the batch processing script
./process_all_pdfs.sh
```

### Step-by-Step Process

1. **Prerequisites Check**: The script validates all requirements
2. **File Discovery**: Scans the `reports` folder for PDF files
3. **Confirmation**: Asks for user confirmation before processing
4. **Batch Processing**: Processes each PDF file with progress updates
5. **Summary Report**: Shows final results and statistics

### Example Output

```
🚀 PDF Batch Processing Script
===============================
Script: process_all_pdfs.sh
Started: 2024-01-15 14:30:25
Reports directory: /path/to/openai-pdf/reports
Log file: /path/to/openai-pdf/processing_log_20240115_143025.log

🔍 Checking prerequisites...
✅ Prerequisites check completed

🔍 Scanning for PDF files...
📁 Found 50 PDF files to process

⚡ About to process 50 PDF files
Do you want to continue? (y/N): y

🏁 Starting batch processing...

Progress: [=========================-----] 25/50 (50%)
📄 Processing: Sample_Report.pdf (42.0 KB)
✅ SUCCESS: Sample_Report.pdf processed successfully
   📊 Database ID: 123
   📝 Text length: 2,456 characters

📊 PROCESSING SUMMARY
====================
Total files found: 50
Files processed: 50
Successful: 48
Errors: 2
Skipped: 0

✅ Successfully processed files:
   • Report1.pdf
   • Report2.pdf
   ...

❌ Files with errors:
   • Corrupted_File.pdf
   • Empty_File.pdf

📋 Detailed log saved to: processing_log_20240115_143025.log
⚠️  Processing completed with 2 errors
```

## Output Files

### Log File
- **Location**: `processing_log_YYYYMMDD_HHMMSS.log`
- **Content**: Detailed processing information for each file
- **Format**: Timestamped entries with full output from each processing attempt

### Database Storage
- **Table**: `documents`
- **Fields**: id, filename, content, file_size, file_type, processed_at
- **Access**: Use helper functions in `openai-pdf-db.py` to retrieve data

## Error Handling

The script handles various error scenarios:

- **Missing files**: Skips non-existent files
- **Processing errors**: Continues with next file if one fails
- **API errors**: Captures and logs OpenAI API issues
- **Database errors**: Reports database connection/storage issues
- **Interruption**: Graceful handling of Ctrl+C with summary

## Configuration

You can modify these variables at the top of the script:

```bash
# Paths (automatically detected)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="${SCRIPT_DIR}/reports"
PYTHON_SCRIPT="${SCRIPT_DIR}/openai-pdf-db.py"

# Logging
LOG_FILE="${SCRIPT_DIR}/processing_log_$(date +%Y%m%d_%H%M%S).log"
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x process_all_pdfs.sh
   ```

2. **Python Not Found**
   - Ensure Python 3 is installed
   - Check if `python3` command works

3. **OpenAI API Key Missing**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

4. **Database Connection Issues**
   - Check PostgreSQL is running
   - Verify database credentials in environment variables
   - See main README-DB.md for database setup

5. **No PDF Files Found**
   - Ensure PDF files are in the `reports` directory
   - Check file permissions

### Debug Mode

For debugging, you can run individual files manually:
```bash
python3 openai-pdf-db.py reports/your-file.pdf
```

## Performance Notes

- **Processing Time**: Each PDF takes 10-30 seconds depending on size and content
- **API Limits**: Script includes 1-second delays between files to respect rate limits
- **Memory Usage**: Minimal memory footprint, processes one file at a time
- **Disk Space**: Log files can grow large with many files

## Integration

This script integrates with:
- **openai-pdf-db.py**: Main processing script
- **PostgreSQL Database**: Storage backend
- **OpenAI API**: Text extraction service

For database queries and management, see the helper functions in `openai-pdf-db.py`:
- `get_document_by_id(doc_id)`
- `get_documents_by_filename(filename)`
- `list_all_documents()` 