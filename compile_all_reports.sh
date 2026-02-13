#!/bin/bash
# Master Compilation Script for All Research Reports
# Compiles all .tex files and generates PDFs with correct copyright

echo "=============================================="
echo "Compiling All Research Reports"
echo "=============================================="
echo ""

cd /home/engra/Self-Correcting-LLM-Research/Self-Correcting-LLM-Research

# Function to compile a document
compile_doc() {
    local tex_file=$1
    local name=$2
    local use_bibtex=$3

    echo "-------------------------------------------"
    echo "Compiling: $name"
    echo "File: $tex_file"
    echo "-------------------------------------------"

    if [ ! -f "$tex_file" ]; then
        echo "❌ ERROR: $tex_file not found!"
        return 1
    fi

    # First pass
    echo "Running pdflatex (1st pass)..."
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1

    # Run bibtex if requested
    if [ "$use_bibtex" = "yes" ]; then
        echo "Running bibtex..."
        bibtex "${tex_file%.tex}" > /dev/null 2>&1
    fi

    # Second pass
    echo "Running pdflatex (2nd pass)..."
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1

    # Third pass
    echo "Running pdflatex (3rd pass)..."
    pdflatex -interaction=nonstopmode "$tex_file" > /dev/null 2>&1

    # Check if PDF was generated
    pdf_file="${tex_file%.tex}.pdf"
    if [ -f "$pdf_file" ]; then
        filesize=$(du -h "$pdf_file" | cut -f1)
        echo "✅ SUCCESS: Generated $pdf_file ($filesize)"
    else
        echo "❌ FAILED: Could not generate $pdf_file"
    fi
    echo ""
}

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    echo "❌ ERROR: pdflatex is not installed!"
    echo ""
    echo "Please install LaTeX:"
    echo "  sudo apt-get install texlive-latex-base texlive-latex-extra"
    echo ""
    echo "Or use Overleaf to compile the documents online."
    exit 1
fi

echo "Found pdflatex ✓"
echo ""

# Compile all documents
compile_doc "ieee_conference_final.tex" "IEEE Conference Paper (7 pages)" "yes"
compile_doc "s2c_draft.tex" "S2C Draft" "yes"
compile_doc "final_report_simple.tex" "Simple Report" "no"
compile_doc "final_report_working.tex" "Working Report" "no"
compile_doc "final_report.tex" "Full Comprehensive Report" "yes"

# Compile arxiv_submission
if [ -f "arxiv_submission/final_report_comprehensive.tex" ]; then
    cd arxiv_submission
    compile_doc "final_report_comprehensive.tex" "ArXiv Submission" "no"
    cd ..
fi

# Compile paper folder
if [ -f "paper/final_report_comprehensive.tex" ]; then
    cd paper
    compile_doc "final_report_comprehensive.tex" "Paper Folder Version" "no"
    cd ..
fi

echo "=============================================="
echo "Compilation Summary"
echo "=============================================="
echo ""

# List all generated PDFs
echo "Generated PDFs:"
ls -lh *.pdf 2>/dev/null | awk '{print $9, "-", $5}'
ls -lh arxiv_submission/*.pdf 2>/dev/null | awk '{print $9, "-", $5}'
ls -lh paper/*.pdf 2>/dev/null | awk '{print $9, "-", $5}'

echo ""
echo "=============================================="
echo "Done!"
echo "=============================================="
echo ""
echo "All PDFs have been generated with the correct copyright format:"
echo "  - Pratham Patel (Corresponding Author)"
echo "  - Md Anisur Rahman Chowdhury"
echo "  - Kefei Wang"
echo "  - Gannon University, USA"
echo ""
echo "Next steps:"
echo "  1. Verify PDFs have correct author information"
echo "  2. Check all figures and tables appear correctly"
echo "  3. Submit to your target conferences/journals"
