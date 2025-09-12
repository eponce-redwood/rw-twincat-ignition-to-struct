#!/usr/bin/env python3
"""
Script to extract individual UDTs from the big Ignition JSON export file.
Each UDT in the big JSON file will be saved as a separate JSON file.
Only the latest version of each UDT will be extracted based on versioning patterns.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

def get_version_priority(udt_name):
    """
    Determine the version priority of a UDT name.
    Higher numbers indicate newer/preferred versions.
    """
    name_lower = udt_name.lower()
    
    # Test versions get lowest priority (including space in name)
    if 'test' in name_lower:
        return 0
    
    # Check for V2, V3, etc. (highest priority)
    v_match = re.search(r'_v(\d+)$', name_lower)
    if v_match:
        return 1000 + int(v_match.group(1))
    
    # Special cases for specific naming patterns
    if name_lower.endswith('_new'):
        return 100
    if name_lower.endswith('_reverse'):
        return 90
    if name_lower.endswith('_hybrid'):
        return 80
    
    # Base version (no suffix) gets medium priority
    return 50

def get_base_name(udt_name):
    """
    Extract the base name from a UDT by removing version suffixes.
    """
    # Remove common version suffixes (order matters - more specific patterns first)
    patterns = [
        r'_Hybrid\s+TEST$',  # _Hybrid TEST (with space)
        r'_Hybrid_TEST$',    # _Hybrid_TEST  
        r'_Hybrid_New$',     # _Hybrid_New
        r'_Hybrid_Reverse$', # _Hybrid_Reverse
        r'_V\d+$',           # _V2, _V3, etc.
        r'_TEST$',           # _TEST
        r'_New$',            # _New
        r'_Reverse$',        # _Reverse
        r'_Hybrid$',         # _Hybrid (must be after the specific hybrid variants)
    ]
    
    base_name = udt_name
    for pattern in patterns:
        base_name = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
    
    return base_name

def extract_udts_from_big_json():
    """
    Extract individual UDTs from the big JSON file and save them as separate files.
    Only the latest version of each UDT will be extracted.
    """
    # Define file paths
    workspace_dir = Path(__file__).parent
    big_json_file = workspace_dir / "Ignition-RW-Standard-ManualExport-BigJSON" / "RW_Ignition_Big_Export.json"
    output_dir = workspace_dir / "Ignition-RW-Standard-ExtractedUDTs"
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Load the big JSON file
    print(f"Loading big JSON file: {big_json_file}")
    try:
        with open(big_json_file, 'r', encoding='utf-8') as f:
            big_json_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {big_json_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}")
        return
    
    # Check if the structure is as expected
    if 'tags' not in big_json_data:
        print("Error: Expected 'tags' key not found in the JSON file")
        return
    
    tags = big_json_data['tags']
    print(f"Found {len(tags)} UDTs in the big JSON file")
    
    # Group UDTs by base name and find the latest version of each
    udt_groups = defaultdict(list)
    
    for i, udt in enumerate(tags):
        if not isinstance(udt, dict):
            print(f"Warning: Tag {i} is not a dictionary, skipping")
            continue
            
        if 'name' not in udt:
            print(f"Warning: Tag {i} has no 'name' field, skipping")
            continue
        
        udt_name = udt['name']
        
        # Skip UDTs that don't start with 'RW_'
        if not udt_name.startswith('RW_'):
            print(f"Info: Skipping '{udt_name}' (doesn't start with 'RW_')")
            continue
        
        base_name = get_base_name(udt_name)
        priority = get_version_priority(udt_name)
        
        udt_groups[base_name].append({
            'name': udt_name,
            'priority': priority,
            'data': udt
        })
    
    # Select the latest version of each UDT group
    latest_udts = {}
    for base_name, udts in udt_groups.items():
        # Sort by priority (highest first) and then by name for consistency
        latest_udt = max(udts, key=lambda x: (x['priority'], x['name']))
        latest_udts[latest_udt['name']] = latest_udt['data']
        
        if len(udts) > 1:
            all_names = [u['name'] for u in udts]
            print(f"Multiple versions found for '{base_name}': {all_names}")
            print(f"  -> Selected: '{latest_udt['name']}' (priority: {latest_udt['priority']})")
    
    # Extract the selected UDTs
    extracted_count = 0
    skipped_count = 0
    
    for udt_name, udt_data in latest_udts.items():
        # Create filename
        filename = f"{udt_name}.json"
        output_file = output_dir / filename
        
        # Save the UDT as a separate JSON file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(udt_data, f, indent=2, ensure_ascii=False)
            print(f"Extracted: {filename}")
            extracted_count += 1
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            skipped_count += 1
    
    print(f"\nExtraction complete!")
    print(f"Successfully extracted: {extracted_count} UDTs (latest versions only)")
    print(f"Total UDT groups processed: {len(udt_groups)}")
    print(f"Errors: {skipped_count}")
    print(f"Output directory: {output_dir}")
    
    # List the extracted files
    extracted_files = sorted([f.name for f in output_dir.glob("*.json")])
    print(f"\nExtracted UDT files:")
    for filename in extracted_files:
        print(f"  - {filename}")
    
    # Generate extraction report
    report_file = output_dir / "extraction_report.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("UDT Extraction Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: RW_Ignition_Big_Export.json\n")
            f.write(f"Total UDTs in source: {len(tags)}\n")
            f.write(f"UDT groups processed: {len(udt_groups)}\n")
            f.write(f"UDTs extracted: {extracted_count}\n\n")
            
            f.write("EXTRACTED UDTs (Latest Versions Only):\n")
            f.write("-" * 40 + "\n")
            for udt_name in sorted(latest_udts.keys()):
                f.write(f"{udt_name}\n")
            
            f.write(f"\nVERSION SELECTION DETAILS:\n")
            f.write("-" * 40 + "\n")
            for base_name, udts in sorted(udt_groups.items()):
                if len(udts) > 1:
                    f.write(f"\nBase: {base_name}\n")
                    f.write(f"  Available versions:\n")
                    for udt in sorted(udts, key=lambda x: (-x['priority'], x['name'])):
                        status = "✓ SELECTED" if udt['name'] in latest_udts else "  skipped"
                        f.write(f"    {udt['name']} (priority: {udt['priority']}) {status}\n")
                else:
                    f.write(f"{base_name}: {udts[0]['name']} (single version)\n")
            
            f.write(f"\nFILES CREATED:\n")
            f.write("-" * 40 + "\n")
            for filename in sorted(extracted_files):
                f.write(f"{filename}\n")
        
        print(f"\nExtraction report saved to: {report_file}")
        
    except Exception as e:
        print(f"Warning: Failed to generate report: {e}")

if __name__ == "__main__":
    extract_udts_from_big_json()