#!/bin/bash
# IEEE Conference Paper Compilation Script
# This script compiles the IEEE conference paper with all figures

echo "=========================================="
echo "IEEE Conference Paper Compilation Script"
echo "=========================================="
echo ""

# Navigate to the paper directory
cd /home/engra/Self-Correcting-LLM-Research/Self-Correcting-LLM-Research

echo "Step 1: Checking for required files..."
echo ""

# Check if the main .tex file exists
if [ ! -f "ieee_conference_final.tex" ]; then
    echo "❌ ERROR: ieee_conference_final.tex not found!"
    exit 1
fi
echo "✓ Found: ieee_conference_final.tex"

# Check if IEEEtran.cls exists
if [ ! -f "IEEEtran.cls" ]; then
    echo "❌ ERROR: IEEEtran.cls not found!"
    exit 1
fi
echo "✓ Found: IEEEtran.cls"

# Check for required figures
echo ""
echo "Step 2: Checking for required figures..."
declare -a figures=(
    "arxiv_submission/graphs/s2c_framework_architecture.pdf"
    "arxiv_submission/graphs/training_performance_curves.pdf"
    "arxiv_submission/graphs/gsm8k_main_results.pdf"
    "arxiv_submission/graphs/ablation_study_results.pdf"
    "arxiv_submission/graphs/error_analysis_comprehensive.pdf"
)

all_figures_found=true
for fig in "${figures[@]}"; do
    if [ -f "$fig" ]; then
        echo "✓ Found: $fig"
    else
        echo "❌ Missing: $fig"
        all_figures_found=false
    fi
done

if [ "$all_figures_found" = false ]; then
    echo ""
    echo "⚠️  WARNING: Some figures are missing!"
    echo "The paper will compile but figures may not appear."
    echo ""
fi

# Check if pdflatex is available
echo ""
echo "Step 3: Checking for LaTeX installation..."
if ! command -v pdflatex &> /dev/null; then
    echo "❌ ERROR: pdflatex is not installed!"
    echo ""
    echo "To install LaTeX on Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended"
    echo ""
    echo "Alternatively, you can:"
    echo "1. Upload ieee_conference_final.tex to Overleaf"
    echo "2. Upload all figures from arxiv_submission/graphs/"
    echo "3. Compile online"
    exit 1
fi
echo "✓ Found: pdflatex"

# Compile the paper
echo ""
echo "Step 4: Compiling the paper..."
echo "=========================================="
echo ""

echo "Running pdflatex (1st pass)..."
pdflatex -interaction=nonstopmode ieee_conference_final.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ First pass completed"
else
    echo "⚠️  First pass completed with warnings (this is normal)"
fi

echo "Running bibtex..."
bibtex ieee_conference_final > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Bibliography processed"
else
    echo "⚠️  Bibliography processing skipped (no .bib file)"
fi

echo "Running pdflatex (2nd pass)..."
pdflatex -interaction=nonstopmode ieee_conference_final.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Second pass completed"
else
    echo "⚠️  Second pass completed with warnings"
fi

echo "Running pdflatex (3rd pass for references)..."
pdflatex -interaction=nonstopmode ieee_conference_final.tex > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Third pass completed"
else
    echo "⚠️  Third pass completed with warnings"
fi

echo ""
echo "=========================================="
echo "Compilation Complete!"
echo "=========================================="
echo ""

# Check if PDF was generated
if [ -f "ieee_conference_final.pdf" ]; then
    echo "✅ SUCCESS: ieee_conference_final.pdf has been generated!"
    echo ""

    # Get file size
    filesize=$(du -h "ieee_conference_final.pdf" | cut -f1)
    echo "📄 File size: $filesize"

    # Count pages
    if command -v pdfinfo &> /dev/null; then
        pages=$(pdfinfo ieee_conference_final.pdf 2>/dev/null | grep Pages | awk '{print $2}')
        echo "📑 Page count: $pages pages"

        if [ "$pages" -le 7 ]; then
            echo "✓ Within IEEE conference page limit (≤7 pages)"
        else
            echo "⚠️  WARNING: Exceeds IEEE conference page limit ($pages > 7 pages)"
        fi
    fi

    echo ""
    echo "You can now:"
    echo "  1. View the PDF: xdg-open ieee_conference_final.pdf"
    echo "  2. Submit to IEEE conference"
    echo ""
else
    echo "❌ ERROR: PDF was not generated!"
    echo ""
    echo "Check the log file for errors:"
    echo "  cat ieee_conference_final.log"
    echo ""
fi

# Cleanup auxiliary files (optional)
read -p "Do you want to clean up auxiliary files (.aux, .log, .bbl, .blg)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f ieee_conference_final.aux ieee_conference_final.log ieee_conference_final.bbl ieee_conference_final.blg \
          ieee_conference_final.out ieee_conference_final.toc
    echo "✓ Auxiliary files cleaned up"
fi

echo ""
echo "Done!"
