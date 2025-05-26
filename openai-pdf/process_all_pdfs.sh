#!/bin/bash

# process_all_pdfs.sh
# Script to process all PDF files in the reports folder using openai-pdf-db.py
# Provides detailed progress tracking, error handling, and summary reporting

set -e  # Exit on any error (can be overridden for individual file processing)

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="${SCRIPT_DIR}/reports"
PYTHON_SCRIPT="${SCRIPT_DIR}/openai-pdf-db.py"
LOG_FILE="${SCRIPT_DIR}/processing_log_$(date +%Y%m%d_%H%M%S).log"

# Counters
TOTAL_FILES=0
PROCESSED_FILES=0
SUCCESS_COUNT=0
ERROR_COUNT=0
SKIPPED_COUNT=0

# Arrays to track results
declare -a SUCCESS_FILES=()
declare -a ERROR_FILES=()
declare -a SKIPPED_FILES=()

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ${message}" >> "$LOG_FILE"
}

# Function to print progress bar
print_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "\r${BLUE}Progress: [${GREEN}"
    printf "%*s" $filled | tr ' ' '='
    printf "${NC}${BLUE}"
    printf "%*s" $empty | tr ' ' '-'
    printf "] %d/%d (%d%%)${NC}" $current $total $percentage
}

# Function to validate prerequisites
check_prerequisites() {
    print_status "$CYAN" "🔍 Checking prerequisites..."
    
    # Check if Python script exists
    if [[ ! -f "$PYTHON_SCRIPT" ]]; then
        print_status "$RED" "❌ ERROR: Python script not found at $PYTHON_SCRIPT"
        exit 1
    fi
    
    # Check if reports directory exists
    if [[ ! -d "$REPORTS_DIR" ]]; then
        print_status "$RED" "❌ ERROR: Reports directory not found at $REPORTS_DIR"
        exit 1
    fi
    
    # Check if Python is available (prefer conda/anaconda python)
    if command -v python &> /dev/null && python -c "import openai" &> /dev/null; then
        PYTHON_CMD="python"
        print_status "$GREEN" "✅ Using conda/anaconda python with openai module"
    elif command -v python3 &> /dev/null && python3 -c "import openai" &> /dev/null; then
        PYTHON_CMD="python3"
        print_status "$GREEN" "✅ Using python3 with openai module"
    else
        print_status "$RED" "❌ ERROR: Python with openai module not found"
        print_status "$RED" "   Please install openai: pip install openai"
        exit 1
    fi
    
    # Check for OpenAI API key
    if [[ -z "$OPENAI_API_KEY" ]]; then
        print_status "$YELLOW" "⚠️  WARNING: OPENAI_API_KEY environment variable not set"
        print_status "$YELLOW" "   Make sure to set it before running this script"
    fi
    
    print_status "$GREEN" "✅ Prerequisites check completed"
}

# Function to get file size in human readable format
get_file_size() {
    local file=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        stat -f%z "$file" | awk '{
            if ($1 < 1024) print $1 " B"
            else if ($1 < 1048576) printf "%.1f KB\n", $1/1024
            else if ($1 < 1073741824) printf "%.1f MB\n", $1/1048576
            else printf "%.1f GB\n", $1/1073741824
        }'
    else
        # Linux
        stat --printf="%s" "$file" | awk '{
            if ($1 < 1024) print $1 " B"
            else if ($1 < 1048576) printf "%.1f KB\n", $1/1024
            else if ($1 < 1073741824) printf "%.1f MB\n", $1/1048576
            else printf "%.1f GB\n", $1/1073741824
        }'
    fi
}

# Function to process a single PDF file
process_pdf() {
    local pdf_file=$1
    local filename=$(basename "$pdf_file")
    local file_size=$(get_file_size "$pdf_file")
    
    print_status "$BLUE" "📄 Processing: $filename ($file_size)"
    
    # Create a temporary log file for this specific file
    local temp_log=$(mktemp)
    
    # Run the Python script and capture output
    if $PYTHON_CMD "$PYTHON_SCRIPT" "$pdf_file" > "$temp_log" 2>&1; then
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        SUCCESS_FILES+=("$filename")
        print_status "$GREEN" "✅ SUCCESS: $filename processed successfully"
        
        # Extract useful information from the output
        if grep -q "Database ID:" "$temp_log"; then
            local db_id=$(grep "Database ID:" "$temp_log" | awk '{print $NF}')
            print_status "$GREEN" "   📊 Database ID: $db_id"
        fi
        
        if grep -q "Text length:" "$temp_log"; then
            local text_length=$(grep "Text length:" "$temp_log" | awk '{print $(NF-1)}')
            print_status "$GREEN" "   📝 Text length: $text_length characters"
        fi
        
    else
        ERROR_COUNT=$((ERROR_COUNT + 1))
        ERROR_FILES+=("$filename")
        print_status "$RED" "❌ ERROR: Failed to process $filename"
        
        # Show error details
        print_status "$RED" "   Error details:"
        while IFS= read -r line; do
            print_status "$RED" "   $line"
        done < "$temp_log"
    fi
    
    # Append the temp log to main log
    echo "--- Processing $filename ---" >> "$LOG_FILE"
    cat "$temp_log" >> "$LOG_FILE"
    echo "--- End $filename ---" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Clean up temp log
    rm -f "$temp_log"
    
    PROCESSED_FILES=$((PROCESSED_FILES + 1))
}

# Function to print final summary
print_summary() {
    echo ""
    print_status "$PURPLE" "📊 PROCESSING SUMMARY"
    print_status "$PURPLE" "===================="
    print_status "$CYAN" "Total files found: $TOTAL_FILES"
    print_status "$CYAN" "Files processed: $PROCESSED_FILES"
    print_status "$GREEN" "Successful: $SUCCESS_COUNT"
    print_status "$RED" "Errors: $ERROR_COUNT"
    print_status "$YELLOW" "Skipped: $SKIPPED_COUNT"
    
    if [[ ${#SUCCESS_FILES[@]} -gt 0 ]]; then
        echo ""
        print_status "$GREEN" "✅ Successfully processed files:"
        for file in "${SUCCESS_FILES[@]}"; do
            print_status "$GREEN" "   • $file"
        done
    fi
    
    if [[ ${#ERROR_FILES[@]} -gt 0 ]]; then
        echo ""
        print_status "$RED" "❌ Files with errors:"
        for file in "${ERROR_FILES[@]}"; do
            print_status "$RED" "   • $file"
        done
    fi
    
    if [[ ${#SKIPPED_FILES[@]} -gt 0 ]]; then
        echo ""
        print_status "$YELLOW" "⏭️  Skipped files:"
        for file in "${SKIPPED_FILES[@]}"; do
            print_status "$YELLOW" "   • $file"
        done
    fi
    
    echo ""
    print_status "$CYAN" "📋 Detailed log saved to: $LOG_FILE"
    
    if [[ $ERROR_COUNT -eq 0 ]]; then
        print_status "$GREEN" "🎉 All files processed successfully!"
        exit 0
    else
        print_status "$YELLOW" "⚠️  Processing completed with $ERROR_COUNT errors"
        exit 1
    fi
}

# Main execution
main() {
    # Print header
    echo ""
    print_status "$PURPLE" "🚀 PDF Batch Processing Script"
    print_status "$PURPLE" "==============================="
    print_status "$CYAN" "Script: $(basename "$0")"
    print_status "$CYAN" "Started: $(date)"
    print_status "$CYAN" "Reports directory: $REPORTS_DIR"
    print_status "$CYAN" "Log file: $LOG_FILE"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    echo ""
    
    # Count PDF files
    print_status "$CYAN" "🔍 Scanning for PDF files..."
    
    # Find all PDF files (case insensitive)
    # Use a more compatible approach instead of mapfile
    pdf_files=()
    while IFS= read -r -d '' file; do
        pdf_files+=("$file")
    done < <(find "$REPORTS_DIR" -type f -iname "*.pdf" -print0 | sort -z)
    TOTAL_FILES=${#pdf_files[@]}
    
    if [[ $TOTAL_FILES -eq 0 ]]; then
        print_status "$YELLOW" "⚠️  No PDF files found in $REPORTS_DIR"
        exit 0
    fi
    
    print_status "$GREEN" "📁 Found $TOTAL_FILES PDF files to process"
    echo ""
    
    # Ask for confirmation
    print_status "$YELLOW" "⚡ About to process $TOTAL_FILES PDF files"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "$YELLOW" "🛑 Processing cancelled by user"
        exit 0
    fi
    
    echo ""
    print_status "$GREEN" "🏁 Starting batch processing..."
    echo ""
    
    # Process each PDF file
    for i in "${!pdf_files[@]}"; do
        local pdf_file="${pdf_files[$i]}"
        local current=$((i + 1))
        
        # Print progress
        print_progress $current $TOTAL_FILES
        echo ""
        
        # Process the file
        process_pdf "$pdf_file"
        echo ""
        
        # Small delay to avoid overwhelming the API
        sleep 1
    done
    
    # Print final summary
    print_summary
}

# Trap to ensure summary is printed even if script is interrupted
trap 'echo ""; print_status "$RED" "🛑 Script interrupted"; print_summary' INT TERM

# Run main function
main "$@" 