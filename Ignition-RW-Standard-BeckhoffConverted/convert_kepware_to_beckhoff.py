#!/usr/bin/env python3
"""
KEPware to Beckhoff UDT Converter

This script automates the conversion of Ignition UDT JSON files from KEPware OPC format 
to Beckhoff TwinCAT OPC UA format.

Usage:
    python convert_kepware_to_beckhoff.py input.json [output.json]
    
If output.json is not specified, it will append '_Beckhoff' to the input filename.

Changes made during conversion:
1. Updates parameters: Node/TIA_PLC_Name/Datablock_Name -> OPCTagPath/OPCServer
2. Converts opcItemPath bindings from KEPware to Beckhoff format
3. Changes valueSource from 'expr' to 'opc' for Boolean tags using bit extraction
4. Removes expression properties for converted Boolean tags
5. Updates opcServer references to use parameter binding

Author: Automated conversion based on manual conversion patterns
Date: September 2025
"""

import json
import sys
import os
import re
from typing import Dict, Any, List
from pathlib import Path


class KEPwareToBeckhoffConverter:
    """Converts Ignition UDT files from KEPware to Beckhoff format."""
    
    def __init__(self):
        self.conversion_stats = {
            'parameters_updated': 0,
            'opcItemPath_updated': 0,
            'valueSource_updated': 0,
            'opcServer_updated': 0,
            'expressions_removed': 0,
            'tags_skipped': 0
        }
    
    def convert_udt(self, input_file: str, output_file: str = None) -> bool:
        """
        Convert a UDT file from KEPware to Beckhoff format.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file (optional)
            
        Returns:
            bool: True if conversion successful, False otherwise
        """
        try:
            # Load the input JSON
            with open(input_file, 'r', encoding='utf-8') as f:
                udt_data = json.load(f)
            
            print(f"Converting: {input_file}")
            print(f"UDT Name: {udt_data.get('name', 'Unknown')}")
            
            # Convert parameters
            self._convert_parameters(udt_data)
            
            # Convert tags
            if 'tags' in udt_data:
                self._convert_tags(udt_data['tags'])
            
            # Determine output file
            if output_file is None:
                input_path = Path(input_file)
                output_file = str(input_path.parent / f"{input_path.stem}_Beckhoff{input_path.suffix}")
            
            # Save the converted JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(udt_data, f, indent=2, ensure_ascii=False)
            
            print(f"Converted file saved: {output_file}")
            self._print_conversion_stats()
            
            return True
            
        except Exception as e:
            print(f"Error converting file: {e}")
            return False
    
    def _convert_parameters(self, udt_data: Dict[str, Any]) -> None:
        """Convert parameters from KEPware format to Beckhoff format."""
        if 'parameters' not in udt_data:
            return
        
        parameters = udt_data['parameters']
        new_parameters = {}
        
        # Add standardized OPC parameters
        new_parameters['OPCTagPath'] = {
            "dataType": "String",
            "value": "nsu=urn:BeckhoffAutomation:Ua:PLC1;s=MAIN.YourTagNameHere"
        }
        
        new_parameters['OPCServer'] = {
            "dataType": "String", 
            "value": "Beckhoff@YourComputerName"
        }
        
        # Keep other parameters that aren't KEPware-specific
        kepware_params = {'Node', 'TIA_PLC_Name', 'Datablock_Name'}
        for param_name, param_value in parameters.items():
            if param_name not in kepware_params:
                new_parameters[param_name] = param_value
        
        udt_data['parameters'] = new_parameters
        self.conversion_stats['parameters_updated'] += 1
        print(f"  ✓ Updated parameters (removed KEPware-specific, added OPCTagPath/OPCServer)")
    
    def _convert_tags(self, tags: List[Dict[str, Any]]) -> None:
        """Convert all tags in the UDT."""
        for i, tag in enumerate(tags):
            tag_name = tag.get('name', f'Tag_{i}')
            value_source = tag.get('valueSource', '')
            
            print(f"  Processing tag: {tag_name} (valueSource: {value_source})")
            
            # Only process tags that have OPC connections
            if self._should_convert_tag(tag):
                # Convert opcItemPath
                if 'opcItemPath' in tag:
                    self._convert_opc_item_path(tag, tag_name)
                
                # Convert valueSource and expressions for Boolean tags
                if tag.get('dataType') == 'Boolean' and 'expression' in tag:
                    self._convert_boolean_tag(tag, tag_name)
                
                # Convert opcServer
                if 'opcServer' in tag and isinstance(tag['opcServer'], str):
                    self._convert_opc_server(tag, tag_name)
            else:
                self.conversion_stats['tags_skipped'] += 1
                print(f"    ⏭️ Skipping (Ignition-internal tag)")
    
    def _should_convert_tag(self, tag: Dict[str, Any]) -> bool:
        """
        Determine if a tag should be converted from KEPware to Beckhoff format.
        
        Convert only tags that represent actual PLC variables:
        1. valueSource: "opc" - Direct OPC mapping
        2. valueSource: "expr" with opcItemPath - Calculated from OPC data (bit extraction)
        
        Skip Ignition-internal tags:
        1. valueSource: "expr" without opcItemPath - Pure Ignition calculations
        2. valueSource: "memory" - Ignition memory variables
        """
        value_source = tag.get('valueSource', '')
        has_opc_item_path = 'opcItemPath' in tag
        
        if value_source == 'opc':
            # Direct OPC mapping - always convert
            return True
        elif value_source == 'expr':
            # Expression - convert only if it references OPC data
            return has_opc_item_path
        elif value_source == 'memory':
            # Memory tags are Ignition-internal - skip
            return False
        else:
            # Unknown valueSource - be conservative and convert only if it has OPC connection
            return has_opc_item_path
    
    def _convert_opc_item_path(self, tag: Dict[str, Any], tag_name: str) -> None:
        """Convert opcItemPath from KEPware to Beckhoff format."""
        opc_item_path = tag['opcItemPath']
        
        if isinstance(opc_item_path, dict) and 'binding' in opc_item_path:
            binding = opc_item_path['binding']
            
            # Check if it's KEPware format
            if 'KEPServerEX' in binding or '{Node}' in binding:
                # Extract the tag name from the end of the path
                # Look for patterns like .TagName at the end
                path_parts = binding.split('.')
                if len(path_parts) > 0:
                    tag_suffix = path_parts[-1]
                    # Remove any parameter bindings from the suffix
                    tag_suffix = re.sub(r'\{.*?\}', '', tag_suffix)
                    
                    if tag_suffix:
                        new_binding = f"{{OPCTagPath}}.hmiIgnition.{tag_suffix}"
                    else:
                        new_binding = f"{{OPCTagPath}}.hmiIgnition.{tag_name}"
                else:
                    new_binding = f"{{OPCTagPath}}.hmiIgnition.{tag_name}"
                
                tag['opcItemPath']['binding'] = new_binding
                self.conversion_stats['opcItemPath_updated'] += 1
                print(f"    ✓ Updated opcItemPath: {tag_suffix}")
    
    def _convert_boolean_tag(self, tag: Dict[str, Any], tag_name: str) -> None:
        """Convert Boolean tags from expression-based to direct OPC."""
        if tag.get('valueSource') == 'expr' and 'expression' in tag:
            # Check if expression is doing bit extraction (contains & operator)
            expression = tag['expression']
            if '&' in expression and '{[.]S_HMISts}' in expression:
                # This is bit extraction, convert to direct OPC
                tag['valueSource'] = 'opc'
                del tag['expression']
                self.conversion_stats['valueSource_updated'] += 1
                self.conversion_stats['expressions_removed'] += 1
                print(f"    ✓ Converted from expression to direct OPC (was bit extraction)")
    
    def _convert_opc_server(self, tag: Dict[str, Any], tag_name: str) -> None:
        """Convert hardcoded opcServer to parameter binding."""
        if isinstance(tag['opcServer'], str):
            tag['opcServer'] = {
                "bindType": "parameter",
                "binding": "{OPCServer}"
            }
            self.conversion_stats['opcServer_updated'] += 1
            print(f"    ✓ Updated opcServer to parameter binding")
    
    def _print_conversion_stats(self) -> None:
        """Print conversion statistics."""
        print("\n" + "="*50)
        print("CONVERSION SUMMARY:")
        print("="*50)
        for stat_name, count in self.conversion_stats.items():
            readable_name = stat_name.replace('_', ' ').title()
            print(f"  {readable_name}: {count}")
        print("="*50)


def main():
    """Main function to handle command line arguments and run conversion."""
    if len(sys.argv) < 2:
        print("Usage: python convert_kepware_to_beckhoff.py input.json [output.json]")
        print("\nExample:")
        print("  python convert_kepware_to_beckhoff.py RW_Digital_Out_V2.json")
        print("  python convert_kepware_to_beckhoff.py RW_Digital_Out_V2.json RW_Digital_Out_V2_Beckhoff.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)
    
    # Create converter and run conversion
    converter = KEPwareToBeckhoffConverter()
    success = converter.convert_udt(input_file, output_file)
    
    if success:
        print(f"\n✅ Conversion completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Update OPCTagPath parameter with your actual tag path")
        print(f"2. Update OPCServer parameter with your Beckhoff server name")
        print(f"3. Test the UDT in Ignition")
    else:
        print(f"\n❌ Conversion failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()