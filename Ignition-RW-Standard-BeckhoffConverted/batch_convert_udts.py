#!/usr/bin/env python3
"""
Batch KEPware to Beckhoff UDT Converter

This script converts multiple UDT files from a source directory.

Usage:
    python batch_convert_udts.py source_directory [output_directory]
    
If output_directory is not specified, converted files will be saved in the same 
directory as the source files with '_Beckhoff' suffix.

Example:
    python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/
    python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/ ./converted/
"""

import os
import sys
import json
from pathlib import Path
from convert_kepware_to_beckhoff import KEPwareToBeckhoffConverter


def create_unified_json(converted_udts: list, output_location: str, count: int) -> None:
    """
    Create a unified JSON file containing all converted UDTs in Ignition import format.
    
    Args:
        converted_udts: List of converted UDT dictionaries
        output_location: Directory to save the unified file
        count: Number of successfully converted UDTs
    """
    try:
        from datetime import datetime
        
        # Create unified structure in Ignition import format
        # Ignition expects a root-level "tags" array for UDT imports
        unified_data = {
            "tags": converted_udts
        }
        
        # Determine output file path
        output_path = Path(output_location)
        unified_file = output_path / "RW_Unified_Beckhoff_UDTs.json"
        
        # Save unified file
        with open(unified_file, 'w', encoding='utf-8') as f:
            json.dump(unified_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 UNIFIED FILE CREATED:")
        print(f"   📄 File: {unified_file}")
        print(f"   📊 Contains: {count} UDTs")
        print(f"   💾 Size: {unified_file.stat().st_size:,} bytes")
        print(f"   📋 Format: Ignition UDT Import Format")
        
    except Exception as e:
        print(f"\n❌ Error creating unified JSON file: {e}")


def batch_convert(source_dir: str, output_dir: str = None, create_unified: bool = False) -> None:
    """
    Convert all JSON files in source directory.
    
    Args:
        source_dir: Directory containing JSON files to convert
        output_dir: Directory to save converted files (optional)
        create_unified: If True, also create a unified JSON file with all UDTs (optional)
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    
    # Find all JSON files
    json_files = list(source_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in '{source_dir}'")
        return
    
    print(f"Found {len(json_files)} JSON files to convert:")
    for file in json_files:
        print(f"  - {file.name}")
    
    print(f"\nStarting batch conversion...")
    print("="*60)
    
    converter = KEPwareToBeckhoffConverter()
    successful_conversions = 0
    failed_conversions = 0
    converted_udts = []  # Store converted UDTs for unified file
    
    for json_file in json_files:
        print(f"\n[{successful_conversions + failed_conversions + 1}/{len(json_files)}]")
        
        # Determine output file
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{json_file.stem}_Beckhoff{json_file.suffix}"
        else:
            output_file = json_file.parent / f"{json_file.stem}_Beckhoff{json_file.suffix}"
        
        # Convert file
        if converter.convert_udt(str(json_file), str(output_file)):
            successful_conversions += 1
            
            # If creating unified file, load the converted UDT
            if create_unified:
                try:
                    import json
                    with open(output_file, 'r', encoding='utf-8') as f:
                        converted_udt = json.load(f)
                        converted_udts.append(converted_udt)
                except Exception as e:
                    print(f"    ⚠️ Warning: Could not load converted UDT for unified file: {e}")
        else:
            failed_conversions += 1
    
    # Create unified JSON file if requested
    if create_unified and converted_udts:
        create_unified_json(converted_udts, output_dir or source_dir, successful_conversions)
    
    # Print final summary
    print("\n" + "="*60)
    print("BATCH CONVERSION COMPLETE")
    print("="*60)
    print(f"✅ Successful conversions: {successful_conversions}")
    print(f"❌ Failed conversions: {failed_conversions}")
    print(f"📁 Output location: {output_dir if output_dir else source_dir}")
    
    if successful_conversions > 0:
        print(f"\nNext steps for all converted files:")
        print(f"1. Update OPCTagPath parameters with actual tag paths")
        print(f"2. Update OPCServer parameters with your Beckhoff server name")
        print(f"3. Test the UDTs in Ignition")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python batch_convert_udts.py source_directory [output_directory] [--unified]")
        print("\nArguments:")
        print("  source_directory     Directory containing JSON files to convert")
        print("  output_directory     Directory to save converted files (optional)")
        print("  --unified           Create a unified JSON file with all UDTs (optional)")
        print("\nExamples:")
        print("  python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/")
        print("  python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/ ./converted/")
        print("  python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/ ./converted/ --unified")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = None
    create_unified = False
    
    # Parse arguments
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == "--unified":
            create_unified = True
        elif not output_dir and not arg.startswith("--"):
            output_dir = arg
    
    batch_convert(source_dir, output_dir, create_unified)


if __name__ == "__main__":
    main()