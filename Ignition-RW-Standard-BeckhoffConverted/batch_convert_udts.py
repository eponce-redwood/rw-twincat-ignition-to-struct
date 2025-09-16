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
from pathlib import Path
from convert_kepware_to_beckhoff import KEPwareToBeckhoffConverter


def batch_convert(source_dir: str, output_dir: str = None) -> None:
    """
    Convert all JSON files in source directory.
    
    Args:
        source_dir: Directory containing JSON files to convert
        output_dir: Directory to save converted files (optional)
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
        else:
            failed_conversions += 1
    
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
        print("Usage: python batch_convert_udts.py source_directory [output_directory]")
        print("\nExamples:")
        print("  python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/")
        print("  python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/ ./converted/")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    batch_convert(source_dir, output_dir)


if __name__ == "__main__":
    main()