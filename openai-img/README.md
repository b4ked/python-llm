# OpenAI Image Text Extraction

This script extracts text from images using OpenAI's Vision API and stores the results in a PostgreSQL database.

## Features

- Extracts text from various image formats (JPG, PNG, GIF, BMP, WebP, TIFF)
- Uses OpenAI's GPT-4o Vision model for accurate text recognition
- Stores extracted text in PostgreSQL database with metadata
- Follows the same format as the PDF extraction script for consistency
- Provides detailed progress feedback and error handling

## Prerequisites

1. **OpenAI API Key**: Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **PostgreSQL Database**: Ensure the PostgreSQL database is running and accessible. The script uses the database configuration from `../db/config.py`.

3. **Python Dependencies**: Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python openai-img-db.py /path/to/your/image.jpg
```

### Supported Image Formats

- JPG/JPEG
- PNG
- GIF
- BMP
- WebP
- TIFF/TIF

### Example

```bash
# Extract text from a screenshot
python openai-img-db.py ~/Documents/screenshot.png

# Extract text from a scanned document
python openai-img-db.py /Users/username/Downloads/receipt.jpg
```

## Output Format

The extracted text follows this format:
1. **Title Line**: A concise 3-6 word title summarizing the image content
2. **Blank Line**: Separator
3. **Full Text**: Complete extracted text in original formatting

Example output:
```
Invoice Payment Receipt

Invoice #: 12345
Date: 2024-01-15
Amount: $150.00
...
```

## Database Storage

The script stores the following information in the `documents` table:
- `filename`: Original image filename
- `content`: Extracted text content
- `file_size`: Image file size in bytes
- `file_type`: Set to "image"
- `processed_at`: Timestamp of processing

## Error Handling

The script handles various error conditions:
- Missing or invalid image files
- Unsupported image formats
- Missing OpenAI API key
- Database connection issues
- API request failures

## Integration with Database

The script uses the same database utilities as other components in the project:
- Connects to PostgreSQL using configuration from `../db/config.py`
- Uses the `DatabaseConnection` class from `../db/database.py`
- Stores data in the same `documents` table as PDF processing

## Performance Notes

- Image processing time depends on image size and complexity
- Large images may take longer to process
- The script includes a 60-second timeout for API requests
- Maximum response length is limited to 4000 tokens

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY not set"**
   - Ensure the environment variable is properly set
   - Check that the API key is valid and has sufficient credits

2. **"Failed to connect to database"**
   - Verify PostgreSQL is running
   - Check database configuration in `../db/config.py`
   - Ensure the `documents` table exists

3. **"Unsupported image format"**
   - Convert the image to a supported format (JPG, PNG, etc.)
   - Check that the file extension matches the actual format

4. **API timeout or rate limiting**
   - Wait a moment and try again
   - Check your OpenAI API usage limits
   - Ensure you have sufficient API credits

### Debug Mode

For additional debugging information, you can modify the script to include more verbose logging or run it with Python's verbose flag:

```bash
python -v openai-img-db.py /path/to/image.jpg
```

## Related Scripts

- `../openai-pdf/openai-pdf-db.py`: PDF text extraction
- `../db/database.py`: Database utilities
- `../db/example_vector_usage.py`: Vector embedding examples 