#!/usr/bin/env python3
"""
Batch UDT Converter Script

This script processes all UDT JSON files and converts them to TwinCAT struct format 
using the existing ignition_to_twincat.py converter.

Usage:
    python batch_convert_udts.py [source_directory] [output_directory]
    
If source_directory is not specified, defaults to Ignition-RW-Standard-ExtractedUDTs
If output_directory is not specified, defaults to TwinCAT_Structs

Examples:
    python batch_convert_udts.py
    python batch_convert_udts.py ../other-udts/
    python batch_convert_udts.py ../other-udts/ ../output-structs/

Author: Automation Script
Date: September 2025
"""

import os
import sys
import glob
from pathlib import Path
from ignition_to_twincat import IgnitionToTwinCATConverter


def batch_convert_udts(source_dir=None, output_dir=None):
    """Convert all UDT JSON files from source directory to TwinCAT structs."""
    
    # Set up paths
    script_dir = Path(__file__).parent
    
    # Default source directory
    if source_dir is None:
        udt_folder = script_dir / "Ignition-RW-Standard-ExtractedUDTs"
    else:
        udt_folder = Path(source_dir)
    
    # Default output directory  
    if output_dir is None:
        output_folder = script_dir / "TwinCAT_Structs"
    else:
        output_folder = Path(output_dir)
    
    print("Batch UDT to TwinCAT Converter")
    print("=" * 50)
    print(f"Source folder: {udt_folder}")
    print(f"Output folder: {output_folder}")
    
    # Validate source directory
    if not udt_folder.exists():
        print(f"Error: Source directory '{udt_folder}' does not exist.")
        return 0, 1
    
    # Create output directory if it doesn't exist
    output_folder.mkdir(parents=True, exist_ok=True)
    
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
            
            # Set custom output folder
            converter.output_folder = str(output_folder)
            
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
    if output_folder.exists():
        tcdut_files = list(output_folder.glob("*.TcDUT"))
        print(f"\n📁 OUTPUT DIRECTORY: {output_folder}")
        print(f"   Generated {len(tcdut_files)} TwinCAT struct files (.TcDUT)")
        
        if tcdut_files:
            print("   Generated files:")
            for file in sorted(tcdut_files):
                print(f"     - {file.name}")
    
    print("\n" + "=" * 60)
    
    return len(successful_conversions), len(failed_conversions)


def main():
    """Main function to handle command line arguments."""
    # Parse command line arguments
    source_dir = None
    output_dir = None
    
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Show usage if help requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Usage: python batch_convert_udts.py [source_directory] [output_directory]")
        print("\nArguments:")
        print("  source_directory   Directory containing JSON UDT files (default: Ignition-RW-Standard-ExtractedUDTs)")
        print("  output_directory   Directory to save TwinCAT struct files (default: TwinCAT_Structs)")
        print("\nExamples:")
        print("  python batch_convert_udts.py")
        print("  python batch_convert_udts.py ../other-udts/")
        print("  python batch_convert_udts.py ../other-udts/ ../output-structs/")
        sys.exit(0)
    
    try:
        success_count, failed_count = batch_convert_udts(source_dir, output_dir)
        
        if failed_count == 0:
            print("🎉 All UDT conversions completed successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  Batch conversion completed with {failed_count} errors.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()