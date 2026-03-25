@echo off
echo Extracting content from PDF file...
cd /d "c:\Users\boume\Briefs\Filrouge2A\rag"

REM Install PyPDF2 if not already installed
pip install PyPDF2

REM Run the extraction script
python extract_pdf_content.py

echo.
echo PDF content extraction completed!
pause