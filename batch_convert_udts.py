#!/usr/bin/env python3
"""
Batch UDT Converter Script

This script processes all UDT JSON files in the Ignition-RW-Standard-ExtractedUDTs folder
and converts them to TwinCAT struct format using the existing ignition_to_twincat.py converter.

Author: Automation Script
Date: September 2025
"""

import os
import sys
import glob
from pathlib import Path
from ignition_to_twincat import IgnitionToTwinCATConverter


def batch_convert_udts():
    """Convert all UDT JSON files in the extracted UDTs folder."""
    
    # Set up paths
    script_dir = Path(__file__).parent
    udt_folder = script_dir / "Ignition-RW-Standard-ExtractedUDTs"
    
    print("Batch UDT to TwinCAT Converter")
    print("=" * 50)
    print(f"Source folder: {udt_folder}")
    
    # Find all JSON files (excluding extraction_report.txt)
    json_files = list(udt_folder.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {udt_folder}")
        return
    
    print(f"Found {len(json_files)} UDT JSON files to convert:")
    for i, file in enumerate(json_files, 1):
        print(f"  {i:2d}. {file.name}")
    
    print("\n" + "=" * 50)
    print("Starting batch conversion...")
    print("=" * 50)
    
    # Track conversion results
    successful_conversions = []
    failed_conversions = []
    
    # Process each file
    for i, json_file in enumerate(json_files, 1):
        print(f"\n[{i}/{len(json_files)}] Converting: {json_file.name}")
        print("-" * 40)
        
        try:
            # Create converter instance for each file
            converter = IgnitionToTwinCATConverter()
            
            # Load and convert the file
            if converter.load_ignition_json(str(json_file)):
                if converter.save_twincat_file():
                    successful_conversions.append(json_file.name)
                    print(f"✅ SUCCESS: {json_file.name} converted successfully")
                else:
                    failed_conversions.append((json_file.name, "Failed to save TwinCAT file"))
                    print(f"❌ FAILED: {json_file.name} - Failed to save TwinCAT file")
            else:
                failed_conversions.append((json_file.name, "Failed to load JSON file"))
                print(f"❌ FAILED: {json_file.name} - Failed to load JSON file")
                
        except Exception as e:
            failed_conversions.append((json_file.name, str(e)))
            print(f"❌ ERROR: {json_file.name} - {str(e)}")
    
    # Print final summary
    print("\n" + "=" * 60)
    print("BATCH CONVERSION COMPLETE")
    print("=" * 60)
    print(f"Total files processed: {len(json_files)}")
    print(f"Successful conversions: {len(successful_conversions)}")
    print(f"Failed conversions: {len(failed_conversions)}")
    
    if successful_conversions:
        print(f"\n✅ SUCCESSFULLY CONVERTED ({len(successful_conversions)}):")
        for file in successful_conversions:
            print(f"   - {file}")
    
    if failed_conversions:
        print(f"\n❌ FAILED CONVERSIONS ({len(failed_conversions)}):")
        for file, error in failed_conversions:
            print(f"   - {file}: {error}")
    
    # Check output directory
    output_dir = script_dir / "TwinCAT_Structs"
    if output_dir.exists():
        tcdut_files = list(output_dir.glob("*.TcDUT"))
        print(f"\n📁 OUTPUT DIRECTORY: {output_dir}")
        print(f"   Generated {len(tcdut_files)} TwinCAT struct files (.TcDUT)")
        
        if tcdut_files:
            print("   Generated files:")
            for file in sorted(tcdut_files):
                print(f"     - {file.name}")
    
    print("\n" + "=" * 60)
    
    return len(successful_conversions), len(failed_conversions)


if __name__ == "__main__":
    try:
        success_count, failed_count = batch_convert_udts()
        
        if failed_count == 0:
            print("🎉 All UDT conversions completed successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  Batch conversion completed with {failed_count} errors.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)