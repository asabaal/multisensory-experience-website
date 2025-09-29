#!/usr/bin/env python3
"""
Generate the complete JavaScript fileData array for the HTML report
"""

import json
from pathlib import Path

def load_file_assessment_data():
    """Load the Stage 8 file assessment results"""
    data_file = Path("pr_analysis_output/file_assessment_results.json")
    
    if not data_file.exists():
        print(f"❌ File not found: {data_file}")
        return None
    
    with open(data_file, 'r') as f:
        return json.load(f)

def generate_js_file_data(assessment_data):
    """Generate JavaScript fileData array from assessment data"""
    
    file_assessments = assessment_data.get('file_assessments', [])
    
    print(f"📊 Generating JavaScript for {len(file_assessments)} files...")
    
    js_lines = ["        const fileData = ["]
    
    for i, file_data in enumerate(file_assessments):
        # Convert to JavaScript object format
        js_obj = {
            "file_path": file_data.get('file_path', ''),
            "merge_readiness": file_data.get('merge_readiness', 'unknown'),
            "business_impact_score": file_data.get('business_impact_score', 5),
            "technical_risk_score": file_data.get('technical_risk_score', 5),
            "overall_assessment": file_data.get('overall_assessment', {}),
            "detailed_feedback": file_data.get('detailed_feedback', ''),
            "recommendations": file_data.get('recommendations', [])
        }
        
        # Convert to pretty JSON string and format for JavaScript
        js_string = json.dumps(js_obj, indent=16)
        
        # Add comma except for last item
        if i < len(file_assessments) - 1:
            js_string += ","
        
        js_lines.append(js_string)
    
    js_lines.append("        ];")
    
    return "\n".join(js_lines)

def main():
    # Load the assessment data
    assessment_data = load_file_assessment_data()
    if not assessment_data:
        return
    
    # Generate JavaScript
    js_content = generate_js_file_data(assessment_data)
    
    # Save to file
    output_file = Path("pr_analysis_output/complete_file_data.js")
    with open(output_file, 'w') as f:
        f.write(js_content)
    
    print(f"✅ Generated complete JavaScript file data: {output_file}")
    print(f"📊 Contains {len(assessment_data.get('file_assessments', []))} files")
    
    # Show first few lines as preview
    print(f"\n📋 Preview (first 50 lines):")
    lines = js_content.split('\n')
    for i, line in enumerate(lines[:50]):
        print(f"{i+1:3d}: {line}")
    
    if len(lines) > 50:
        print(f"... and {len(lines) - 50} more lines")

if __name__ == "__main__":
    main()