#!/bin/bash
# Create ZIP files for Overleaf upload
# All .tex files have been updated with correct copyright

echo "=========================================="
echo "Creating ZIP Files for Overleaf"
echo "=========================================="
echo ""

cd /home/engra/Self-Correcting-LLM-Research/Self-Correcting-LLM-Research

# Function to create ZIP
create_zip() {
    local zipname=$1
    shift
    local files=("$@")
    
    echo "Creating $zipname..."
    zip -q -r "$zipname" "${files[@]}" 2>/dev/null
    
    if [ -f "$zipname" ]; then
        size=$(du -h "$zipname" | cut -f1)
        echo "✅ Created: $zipname ($size)"
    else
        echo "❌ Failed: $zipname"
    fi
}

# 1. IEEE Conference Paper (PRIORITY)
echo "1. IEEE Conference Paper (7 pages)"
create_zip "ieee_conference.zip" \
    "ieee_conference_final.tex" \
    "IEEEtran.cls" \
    "arxiv_submission/graphs/s2c_framework_architecture.pdf" \
    "arxiv_submission/graphs/training_performance_curves.pdf" \
    "arxiv_submission/graphs/gsm8k_main_results.pdf" \
    "arxiv_submission/graphs/ablation_study_results.pdf" \
    "arxiv_submission/graphs/error_analysis_comprehensive.pdf"
echo ""

# 2. S2C Draft
echo "2. S2C Draft"
create_zip "s2c_draft.zip" \
    "s2c_draft.tex" \
    "IEEEtran.cls"
echo ""

# 3. Simple Report
echo "3. Simple Report"
create_zip "simple_report.zip" \
    "final_report_simple.tex"
echo ""

# 4. Working Report
echo "4. Working Report"
create_zip "working_report.zip" \
    "final_report_working.tex"
echo ""

# 5. Full Report
echo "5. Full Report (Large)"
create_zip "full_report.zip" \
    "final_report.tex" \
    "IEEEtran.cls" \
    "arxiv_submission/graphs/"
echo ""

# 6. ArXiv Submission
echo "6. ArXiv Submission"
cd arxiv_submission 2>/dev/null
if [ -f "final_report_comprehensive.tex" ]; then
    zip -q -r ../arxiv_submission.zip \
        final_report_comprehensive.tex \
        graphs/ 2>/dev/null
    cd ..
    if [ -f "arxiv_submission.zip" ]; then
        size=$(du -h "arxiv_submission.zip" | cut -f1)
        echo "✅ Created: arxiv_submission.zip ($size)"
    fi
else
    cd ..
    echo "⚠️ Skipped: arxiv_submission (file not found)"
fi
echo ""

# 7. Paper Folder
echo "7. Paper Folder"
cd paper 2>/dev/null
if [ -f "final_report_comprehensive.tex" ]; then
    zip -q -r ../paper_submission.zip \
        final_report_comprehensive.tex 2>/dev/null
    cd ..
    if [ -f "paper_submission.zip" ]; then
        size=$(du -h "paper_submission.zip" | cut -f1)
        echo "✅ Created: paper_submission.zip ($size)"
    fi
else
    cd ..
    echo "⚠️ Skipped: paper_submission (file not found)"
fi
echo ""

echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Created ZIP files:"
ls -lh *.zip 2>/dev/null | awk '{print "  " $9 " - " $5}'
echo ""
echo "Upload these ZIP files to Overleaf:"
echo "1. Go to https://www.overleaf.com"
echo "2. Click 'New Project' → 'Upload Project'"
echo "3. Upload each ZIP file"
echo "4. Click 'Recompile' to generate PDF"
echo "5. Download the PDF with correct copyright!"
echo ""
echo "📌 START WITH: ieee_conference.zip (7-page conference paper)"
