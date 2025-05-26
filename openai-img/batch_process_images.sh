#!/bin/bash

# batch_process_images.sh
# 
# Batch process all images in the /img folder using openai-img-db.py
# Skips images that have already been processed (exist in database)
#
# Usage: ./batch_process_images.sh [image_directory]
# If no directory is provided, defaults to /img

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENAI_SCRIPT="$SCRIPT_DIR/openai-img-db.py"
DEFAULT_IMG_DIR="/img"
LOG_FILE="$SCRIPT_DIR/batch_processing_$(date +%Y%m%d_%H%M%S).log"

# Python command (will be set by check_prerequisites)
PYTHON_CMD=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}" | tee -a "$LOG_FILE"
}

# Function to validate prerequisites
check_prerequisites() {
    print_status "$BLUE" "🔍 Checking prerequisites..."
    
    # Check if OpenAI script exists
    if [[ ! -f "$OPENAI_SCRIPT" ]]; then
        print_status "$RED" "❌ ERROR: OpenAI script not found at $OPENAI_SCRIPT"
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
        print_status "$RED" "❌ ERROR: OPENAI_API_KEY environment variable not set"
        print_status "$RED" "   Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'"
        exit 1
    fi
    
    print_status "$GREEN" "✅ Prerequisites check completed"
}

# Check if image already exists in database
check_image_exists() {
    local filename="$1"
    
    # Use Python to check if the image already exists in the database
    $PYTHON_CMD -c "
import sys
import os
sys.path.append(os.path.join('$SCRIPT_DIR', '..', 'db'))
from database import DatabaseConnection

def check_exists(filename):
    db = DatabaseConnection()
    if db.connect():
        try:
            result = db.execute_query(
                'SELECT COUNT(*) as count FROM documents WHERE filename = %s AND file_type = %s',
                (filename, 'image')
            )
            count = result[0]['count'] if result else 0
            return count > 0
        except Exception as e:
            print(f'Error checking database: {e}', file=sys.stderr)
            return False
        finally:
            db.disconnect()
    return False

if check_exists('$filename'):
    sys.exit(0)  # Exists
else:
    sys.exit(1)  # Does not exist
"
}

# Process a single image
process_image() {
    local image_path="$1"
    local filename=$(basename "$image_path")
    
    log "Processing: $filename"
    
    # Check if image already exists in database
    if check_image_exists "$filename"; then
        print_status "$YELLOW" "⚠ Skipping $filename - already exists in database"
        return 0
    fi
    
    # Process the image
    if $PYTHON_CMD "$OPENAI_SCRIPT" "$image_path" >> "$LOG_FILE" 2>&1; then
        print_status "$GREEN" "✓ Successfully processed: $filename"
        return 0
    else
        print_status "$RED" "✗ Failed to process: $filename"
        return 1
    fi
}

# Main function
main() {
    local img_dir="${1:-$DEFAULT_IMG_DIR}"
    
    print_status "$BLUE" "OpenAI Image Batch Processing Script"
    print_status "$BLUE" "====================================="
    
    # Check prerequisites
    check_prerequisites
    
    # Check if the image directory exists
    if [[ ! -d "$img_dir" ]]; then
        print_status "$RED" "Error: Image directory '$img_dir' does not exist"
        print_status "$BLUE" "Usage: $0 [image_directory]"
        print_status "$BLUE" "If no directory is provided, defaults to /img"
        exit 1
    fi
    

    
    log "Starting batch processing of images in: $img_dir"
    log "Log file: $LOG_FILE"
    
    # Find all supported image files
    local supported_extensions=("jpg" "jpeg" "png" "gif" "bmp" "webp" "tiff" "tif")
    local image_files=()
    
    for ext in "${supported_extensions[@]}"; do
        while IFS= read -r -d '' file; do
            image_files+=("$file")
        done < <(find "$img_dir" -type f -iname "*.${ext}" -print0 2>/dev/null)
    done
    
    if [[ ${#image_files[@]} -eq 0 ]]; then
        print_status "$YELLOW" "No supported image files found in $img_dir"
        print_status "$BLUE" "Supported formats: ${supported_extensions[*]}"
        exit 0
    fi
    
    print_status "$BLUE" "Found ${#image_files[@]} image files to process"
    
    # Process each image
    local processed=0
    local skipped=0
    local failed=0
    local total=${#image_files[@]}
    
    for i in "${!image_files[@]}"; do
        local current=$((i + 1))
        local image_file="${image_files[$i]}"
        local filename=$(basename "$image_file")
        
        print_status "$BLUE" "[$current/$total] Processing: $filename"
        
        if check_image_exists "$filename"; then
            print_status "$YELLOW" "⚠ Skipping $filename - already exists in database"
            ((skipped++))
        else
            if process_image "$image_file"; then
                ((processed++))
            else
                ((failed++))
            fi
        fi
        
        # Add a small delay to avoid overwhelming the API
        sleep 1
    done
    
    # Summary
    print_status "$BLUE" "====================================="
    print_status "$BLUE" "Batch Processing Summary:"
    print_status "$GREEN" "✓ Successfully processed: $processed"
    print_status "$YELLOW" "⚠ Skipped (already exists): $skipped"
    print_status "$RED" "✗ Failed: $failed"
    print_status "$BLUE" "Total files: $total"
    print_status "$BLUE" "Log file: $LOG_FILE"
    
    if [[ $failed -gt 0 ]]; then
        print_status "$RED" "Some files failed to process. Check the log file for details."
        exit 1
    else
        print_status "$GREEN" "All files processed successfully!"
        exit 0
    fi
}

# Help function
show_help() {
    echo "OpenAI Image Batch Processing Script"
    echo ""
    echo "Usage: $0 [OPTIONS] [IMAGE_DIRECTORY]"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "ARGUMENTS:"
    echo "  IMAGE_DIRECTORY    Directory containing images to process (default: /img)"
    echo ""
    echo "ENVIRONMENT VARIABLES:"
    echo "  OPENAI_API_KEY     Your OpenAI API key (required)"
    echo ""
    echo "PYTHON ENVIRONMENT:"
    echo "  Automatically detects conda/anaconda python or system python3"
    echo "  Requires openai module to be installed"
    echo ""
    echo "SUPPORTED FORMATS:"
    echo "  jpg, jpeg, png, gif, bmp, webp, tiff, tif"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                           # Process images in /img"
    echo "  $0 /path/to/images          # Process images in custom directory"
    echo "  $0 ~/Documents/screenshots  # Process images in home directory"
    echo ""
    echo "The script will:"
    echo "  - Detect and use the best available Python environment"
    echo "  - Check if each image already exists in the database"
    echo "  - Skip images that have already been processed"
    echo "  - Process new images using openai-img-db.py"
    echo "  - Log all activity to a timestamped log file"
    echo "  - Provide a summary of results"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 