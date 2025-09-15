#!/usr/bin/env python3
"""
Ignition to TwinCAT Struct Converter

This script converts Ignition tag definition JSON files to TwinCAT struct format.
It extracts the relevant tag information and generates proper TwinCAT TYPE definitions.

Author: Automation Script
Date: September 2025
"""

import json
import os
import sys
import re
import uuid
from pathlib import Path


class IgnitionToTwinCATConverter:
    """Converts Ignition tag definitions to TwinCAT struct format."""
    
    # Data type mapping from Ignition to TwinCAT based on official documentation
    # Reference: https://docs.inductiveautomation.com/docs/8.1/platform/tags/tag-data-types
    # and TwinCAT IEC 61131-3 data types
    DATA_TYPE_MAPPING = {
        # Standard Ignition primitives to TwinCAT
        'Boolean': 'BOOL',
        'Byte': 'USINT',           # Ignition Byte (0-255) -> TwinCAT USINT (0-255)
        'Short': 'INT',            # Ignition Short (16-bit signed) -> TwinCAT INT
        'Integer': 'DINT',         # Ignition Integer (32-bit signed) -> TwinCAT DINT
        'Long': 'LINT',            # Ignition Long (64-bit signed) -> TwinCAT LINT
        'Float': 'REAL',           # Ignition Float (32-bit) -> TwinCAT REAL
        'Double': 'LREAL',         # Ignition Double (64-bit) -> TwinCAT LREAL
        'String': 'STRING',        # Ignition String -> TwinCAT STRING
        'DateTime': 'DT',          # Ignition DateTime -> TwinCAT DATE_AND_TIME (DT)
        
        # Legacy/alternate naming found in exports
        'Boolean': 'BOOL',
        'Float4': 'REAL',          # 4-byte float = REAL
        'Float8': 'LREAL',         # 8-byte float = LREAL (double precision)
        'Int4': 'DINT',            # 4-byte int = DINT
        'Int8': 'SINT',            # 8-bit signed int = SINT
        'Int16': 'INT',            # 16-bit signed int = INT
        'Int32': 'DINT',           # 32-bit signed int = DINT
        'UInt16': 'UINT',          # 16-bit unsigned int = UINT
        'UInt32': 'UDINT',         # 32-bit unsigned int = UDINT
        
        # Array types (Ignition -> TwinCAT arrays)
        'Byte Array': 'ARRAY[0..255] OF USINT',
        'Short Array': 'ARRAY[0..255] OF INT',
        'Integer Array': 'ARRAY[0..255] OF DINT',
        'Long Array': 'ARRAY[0..255] OF LINT',
        'Float Array': 'ARRAY[0..255] OF REAL',
        'Double Array': 'ARRAY[0..255] OF LREAL',
        'Boolean Array': 'ARRAY[0..255] OF BOOL',
        'String Array': 'ARRAY[0..255] OF STRING',
        'DateTime Array': 'ARRAY[0..255] OF DT',
        
        # Shorthand array names sometimes found in exports
        'StringArray': 'ARRAY[0..255] OF STRING',
    }
    
    def __init__(self, udt_mapping=None):
        self.tags = []
        self.struct_name = ""
        self.parameters = {}
        self.output_folder = "TwinCAT_Structs"
        self.udt_mapping = udt_mapping or self._build_udt_mapping()
        self.nested_structs = {}  # For tracking folder structures
    
    def _build_udt_mapping(self):
        """Build mapping from Ignition UDT type IDs to TwinCAT struct names."""
        import os
        import glob
        
        udt_mapping = {}
        
        # Scan all JSON files in the UDT directory to build the mapping
        udt_folder = "Ignition-RW-Standard-ExtractedUDTs"
        if os.path.exists(udt_folder):
            json_files = glob.glob(os.path.join(udt_folder, "*.json"))
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    
                    # Extract the UDT name from the file
                    udt_name = data.get('name', '')
                    if udt_name:
                        # Create the type ID pattern (assuming Redwood namespace)
                        type_id = f"Redwood/{udt_name}"
                        
                        # Generate TwinCAT struct name using the same logic as generate_twincat_name
                        twincat_name = self._generate_twincat_struct_name(udt_name)
                        
                        udt_mapping[type_id] = twincat_name
                        
                except Exception as e:
                    print(f"Warning: Could not process {json_file} for UDT mapping: {e}")
        
        return udt_mapping
    
    def _generate_twincat_struct_name(self, ignition_name):
        """Generate TwinCAT struct name from Ignition UDT name."""
        # Convert name to TwinCAT naming convention
        name_parts = []
        current_part = ""
        
        for char in ignition_name:
            if char == '_':
                if current_part:
                    name_parts.append(current_part.capitalize())
                    current_part = ""
            else:
                current_part += char
        
        if current_part:
            name_parts.append(current_part.capitalize())
        
        # Join parts and add prefix/suffix
        converted_name = ''.join(name_parts)
        return f"ST_{converted_name}_HMI_IgnitionExp"
    
    def load_ignition_json(self, json_file_path):
        """Load and parse the Ignition JSON file."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Extract basic information
            self.struct_name = data.get('name', 'UnknownStruct')
            self.parameters = data.get('parameters', {})
            
            # Extract tags (recursively handle folders and nested structures)
            raw_tags = data.get('tags', [])
            self.tags = []
            self.nested_structs = {}
            
            self._extract_tags_with_nested_structs(raw_tags)
            
            print(f"Loaded {len(self.tags)} tags from {json_file_path}")
            if self.nested_structs:
                print(f"Found {len(self.nested_structs)} nested structures")
            return True
            
        except FileNotFoundError:
            print(f"Error: File {json_file_path} not found.")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {json_file_path}: {e}")
            return False
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def _extract_tags_with_nested_structs(self, tags_array, folder_prefix=""):
        """Extract tags while preserving folder hierarchy via OPC UA pragmas and handling UDT instances."""
        for tag in tags_array:
            tag_type = tag.get('tagType', '')
            tag_name = tag.get('name', 'Unknown')
            
            if tag_type == 'Folder':
                # For folders, process contents and track folder path for organization
                folder_name = self._sanitize_name(tag_name)
                nested_tags = tag.get('tags', [])
                
                # Create folder prefix for tracking hierarchy (for comments/organization)
                new_prefix = f"{folder_prefix}{folder_name}_" if folder_prefix else f"{folder_name}_"
                
                # Recursively process folder contents with the prefix for tracking only
                self._extract_tags_with_nested_structs(nested_tags, new_prefix)
                    
            elif tag_type == 'UdtInstance':
                # Reference an existing UDT struct - this creates an actual struct reference
                type_id = tag.get('typeId', '')
                instance_name = self._sanitize_name(tag_name)
                
                # Apply folder prefix for UDT instances to avoid naming conflicts
                prefixed_name = f"{folder_prefix}{instance_name}" if folder_prefix else instance_name
                
                if type_id in self.udt_mapping:
                    twincat_struct_name = self.udt_mapping[type_id]
                    
                    udt_ref = {
                        'name': prefixed_name,
                        'twincat_type': twincat_struct_name,
                        'access_rights': 'ReadWrite',
                        'tooltip': f'UDT Instance: {tag_name} ({type_id})',
                        'is_udt_reference': True,
                        'folder_path': folder_prefix.rstrip('_') if folder_prefix else None
                    }
                    self.tags.append(udt_ref)
                else:
                    print(f"Warning: Unknown UDT type '{type_id}' for instance '{tag_name}'")
                    
            elif tag_type == 'AtomicTag' or tag.get('dataType'):
                # Regular atomic tag - use original name, store folder path for organization
                tag_info = self._extract_tag_info(tag)  # Don't pass folder_prefix
                if tag_info:
                    # Store folder path for OPC UA pragma generation and comments
                    tag_info['folder_path'] = folder_prefix.rstrip('_') if folder_prefix else None
                    self.tags.append(tag_info)
    
    def _extract_folder_contents(self, tags_array, folder_tags, folder_nested_structs):
        """Extract contents of a folder into separate lists."""
        for tag in tags_array:
            tag_type = tag.get('tagType', '')
            tag_name = tag.get('name', 'Unknown')
            
            if tag_type == 'Folder':
                # Nested folder within folder
                subfolder_name = self._sanitize_name(tag_name)
                nested_tags = tag.get('tags', [])
                
                if nested_tags:
                    subfolder_struct_name = f"ST_{subfolder_name}"
                    subfolder_tags = []
                    subfolder_nested_structs = {}
                    
                    self._extract_folder_contents(nested_tags, subfolder_tags, subfolder_nested_structs)
                    
                    folder_nested_structs[subfolder_struct_name] = {
                        'tags': subfolder_tags,
                        'nested_structs': subfolder_nested_structs
                    }
                    
                    folder_ref = {
                        'name': subfolder_name,
                        'twincat_type': subfolder_struct_name,
                        'access_rights': 'ReadWrite',
                        'tooltip': f'Subfolder: {tag_name}',
                        'is_nested_struct': True
                    }
                    folder_tags.append(folder_ref)
                    
            elif tag_type == 'UdtInstance':
                # UDT instance within folder
                type_id = tag.get('typeId', '')
                instance_name = self._sanitize_name(tag_name)
                
                if type_id in self.udt_mapping:
                    twincat_struct_name = self.udt_mapping[type_id]
                    
                    udt_ref = {
                        'name': instance_name,
                        'twincat_type': twincat_struct_name,
                        'access_rights': 'ReadWrite',
                        'tooltip': f'UDT Instance: {tag_name} ({type_id})',
                        'is_udt_reference': True
                    }
                    folder_tags.append(udt_ref)
                else:
                    print(f"Warning: Unknown UDT type '{type_id}' for instance '{tag_name}'")
                    
            elif tag_type == 'AtomicTag' or tag.get('dataType'):
                # Atomic tag within folder
                tag_info = self._extract_tag_info(tag)
                if tag_info:
                    folder_tags.append(tag_info)
    
    def _sanitize_name(self, name):
        """Sanitize name for TwinCAT compatibility."""
        # Remove spaces and special characters, replace with underscores
        import re
        sanitized = re.sub(r'[^\w]', '_', name)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized
    
    def _extract_tag_info(self, tag):
        """Extract relevant information from a single tag."""
        tag_info = {}
        
        # Required fields
        name = tag.get('name')
        data_type = tag.get('dataType')
        
        if not name or not data_type:
            return None
        
        # Use original tag name without folder prefix
        tag_info['name'] = self._sanitize_name(name)
        tag_info['dataType'] = data_type
        
        # Handle tooltip - can be string or dict with binding info
        tooltip_raw = tag.get('tooltip', '')
        if isinstance(tooltip_raw, dict):
            # If tooltip is a dict with binding info, extract the binding or use empty string
            tag_info['tooltip'] = tooltip_raw.get('binding', '').strip()
        elif isinstance(tooltip_raw, str):
            tag_info['tooltip'] = tooltip_raw.strip()
        else:
            tag_info['tooltip'] = str(tooltip_raw).strip()
        
        tag_info['readOnly'] = tag.get('readOnly', False)
        
        # Clean up tooltip - remove unicode escape sequences and extra whitespace
        if tag_info['tooltip']:
            tag_info['tooltip'] = tag_info['tooltip'].replace('\\u003d', '=')
            tag_info['tooltip'] = re.sub(r'\s+', ' ', tag_info['tooltip'])
        
        return tag_info
    
    def _convert_to_twincat_name(self, ignition_name):
        """Convert Ignition UDT name to TwinCAT struct naming convention."""
        # Remove version suffixes like _V2
        name = re.sub(r'_V\d+$', '', ignition_name)
        
        # Convert naming pattern: RW_Analog_In -> ST_RW_AnalogIn_HMI_IgnitionExp
        # Split by underscores and convert to PascalCase for middle parts
        parts = name.split('_')
        if len(parts) >= 3 and parts[0] == 'RW':
            # Keep RW prefix, convert rest to PascalCase
            middle_parts = []
            for part in parts[1:]:
                # Convert to PascalCase
                middle_parts.append(part.capitalize())
            
            twincat_name = f"ST_RW_{''.join(middle_parts)}_HMI_IgnitionExp"
        else:
            # Fallback: just add ST_ prefix and make PascalCase
            twincat_name = f"ST_{name.replace('_', '')}_HMI_IgnitionExp"
        
        return twincat_name
    
    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        import os
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"Created output directory: {self.output_folder}")
    
    def _map_data_type(self, ignition_type):
        """Map Ignition data type to TwinCAT data type."""
        twincat_type = self.DATA_TYPE_MAPPING.get(ignition_type, ignition_type)
        
        if twincat_type == ignition_type and ignition_type not in self.DATA_TYPE_MAPPING:
            print(f"Warning: Unknown data type '{ignition_type}', using as-is")
        
        return twincat_type
    
    def _format_comment(self, tooltip, max_length=80):
        """Format tooltip as TwinCAT comment."""
        if not tooltip:
            return ""
        
        # Clean and format the comment
        comment = tooltip.strip()
        if len(comment) > max_length:
            comment = comment[:max_length-3] + "..."
        
        return f"// {comment}"
    
    def _sanitize_variable_name(self, name):
        """Ensure variable name follows TwinCAT naming conventions."""
        # TwinCAT variable names should start with letter or underscore
        # and contain only letters, numbers, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # Ensure it starts with a letter or underscore
        if sanitized and not (sanitized[0].isalpha() or sanitized[0] == '_'):
            sanitized = '_' + sanitized
        
        return sanitized
    
    def _generate_opc_pragmas(self, tag):
        """Generate OPC UA pragmas for a tag, using actual tag descriptions."""
        pragmas = []
        
        # Basic OPC UA exposure (always enabled)
        pragmas.append("        {attribute 'OPC.UA.DA' := '1'}")
        
        # For UDT references, enable StructuredType
        if tag.get('is_udt_reference'):
            pragmas.append("        {attribute 'OPC.UA.DA.StructuredType' := '1'}")
        
        # Access rights - read-only if specified
        if tag.get('readOnly'):
            pragmas.append("        {attribute 'OPC.UA.DA.Access' := '1'}")
        
        # Description from actual tag tooltip (not folder path)
        if tag.get('tooltip'):
            # Use the actual description from the Ignition tag
            description = tag['tooltip'].replace("'", "''")
            pragmas.append(f"        {{attribute 'OPC.UA.DA.Description' := '{description}'}}")
        
        return pragmas
    
    def _sanitize_name(self, name):
        """Sanitize name for TwinCAT compatibility."""
        # Remove spaces and special characters, replace with underscores
        import re
        sanitized = re.sub(r'[^\w]', '_', name)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized
    
    def generate_twincat_struct(self):
        """Generate the TwinCAT struct definition (just the struct content)."""
        if not self.tags:
            return "// No tags found to convert"
        
        # Convert struct name to TwinCAT convention
        twincat_struct_name = self._convert_to_twincat_name(self.struct_name)
        
        lines = []
        
        # Add struct attributes for memory optimization and OPC UA
        lines.append("    {attribute 'pack_mode' := '1'}")
        lines.append("    {attribute 'OPC.UA.DA' := '1'}")
        lines.append("    {attribute 'OPC.UA.DA.StructuredType' := '1'}")
        lines.append("    (*")
        lines.append(f"    {twincat_struct_name}")
        lines.append("    " + "="*50)
        lines.append(f"    Generated from Ignition UDT: {self.struct_name}")
        lines.append(f"    Total tags: {len(self.tags)}")
        lines.append(f"    Generated on: {self._get_timestamp()}")
        lines.append("    *)")
        lines.append(f"    TYPE {twincat_struct_name} :")
        lines.append("    STRUCT")
        
        # Add variables
        for i, tag in enumerate(self.tags):
            # Add spacing for readability
            if i > 0 and i % 5 == 0:
                lines.append("")
            
            # Generate OPC UA pragmas for atomic tags (not UDT references)
            if not tag.get('is_udt_reference'):
                opc_pragmas = self._generate_opc_pragmas(tag)
                lines.extend(opc_pragmas)
                
                # Format comment if tooltip exists (for atomic tags only)
                if tag.get('tooltip') and not tag.get('folder_path'):
                    comment = tag['tooltip'].strip()
                    if len(comment) > 70:
                        comment = comment[:67] + "..."
                    lines.append(f"        // {comment}")
            
            line = self._generate_tag_line(tag)
            if line:
                lines.append(f"        {line}")
        
        lines.append("    END_STRUCT")
        lines.append("    END_TYPE")
        
        return "\n".join(lines)
    
    def _generate_tag_line(self, tag):
        """Generate a single tag line for TwinCAT struct."""
        var_name = self._sanitize_variable_name(tag['name'])
        
        # Handle different tag types
        if tag.get('is_udt_reference'):
            # Reference to another UDT struct
            twincat_type = tag['twincat_type']
            var_line = f"{var_name} : {twincat_type};"
            
            # Add tooltip as comment
            if tag.get('tooltip'):
                var_line += f"\t\t// {tag['tooltip']}"
                
        else:
            # Regular atomic tag - generate pragmas and variable declaration
            
            # Map data type
            twincat_type = self._map_data_type(tag['dataType'])
            
            # Add variable declaration with proper spacing
            var_line = f"{var_name} : {twincat_type}"
            
            # Add default value based on TwinCAT type
            if twincat_type == 'BOOL':
                var_line += " := FALSE"
            elif twincat_type in ['REAL', 'LREAL']:
                var_line += " := 0.0"
            elif twincat_type in ['SINT', 'INT', 'DINT', 'LINT', 'USINT', 'UINT', 'UDINT', 'ULINT', 'BYTE', 'WORD', 'DWORD', 'LWORD']:
                var_line += " := 0"
            elif twincat_type in ['STRING', 'WSTRING']:
                var_line += " := ''"
            elif twincat_type == 'DT':  # DATE_AND_TIME
                var_line += " := DT#1970-01-01-00:00:00"
            elif twincat_type.startswith('ARRAY'):
                # For arrays, no default initialization needed (TwinCAT handles this)
                pass
            else:
                # For any unmapped types, don't add default value
                pass
            
            var_line += ";"
            
            # Add read-only comment if applicable
            if tag.get('readOnly'):
                var_line += "\t\t// Read-only tag"
            
            # Add folder path comment if applicable
            if tag.get('folder_path'):
                folder_comment = f"\t\t// Folder: {tag['folder_path'].replace('_', '/')}"
                if not tag.get('readOnly'):
                    var_line += folder_comment
                else:
                    var_line += f", {folder_comment.strip()}"
        
        return var_line
        
        return "\n".join(lines)
    
    def generate_twincat_xml(self):
        """Generate the complete TwinCAT XML file content."""
        twincat_struct_name = self._convert_to_twincat_name(self.struct_name)
        struct_content = self.generate_twincat_struct()
        
        # Generate a unique GUID for this DUT
        dut_id = str(uuid.uuid4())
        
        xml_content = f'''<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="{twincat_struct_name}" Id="{{{dut_id}}}">
    <Declaration><![CDATA[{struct_content}
]]></Declaration>
  </DUT>
</TcPlcObject>'''
        
        return xml_content
    
    def _get_timestamp(self):
        """Get current timestamp for header comment."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_twincat_file(self, output_path=None):
        """Save the generated TwinCAT struct to a file."""
        import os
        
        # Ensure output directory exists
        self._ensure_output_directory()
        
        if output_path is None:
            # Generate filename with TwinCAT naming convention and .TcDUT extension
            twincat_struct_name = self._convert_to_twincat_name(self.struct_name)
            output_path = os.path.join(self.output_folder, f"{twincat_struct_name}.TcDUT")
        
        # Generate XML content
        xml_content = self.generate_twincat_xml()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(xml_content)
            print(f"TwinCAT struct saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def print_summary(self):
        """Print conversion summary."""
        twincat_name = self._convert_to_twincat_name(self.struct_name)
        
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        print(f"Original Ignition UDT: {self.struct_name}")
        print(f"TwinCAT Struct Name: {twincat_name}")
        print(f"Total Tags: {len(self.tags)}")
        
        if self.nested_structs:
            print(f"Nested Structures: {len(self.nested_structs)}")
        
        # Count different tag types
        atomic_tags = 0
        nested_struct_refs = 0
        udt_refs = 0
        type_counts = {}
        
        for tag in self.tags:
            if tag.get('is_nested_struct'):
                nested_struct_refs += 1
            elif tag.get('is_udt_reference'):
                udt_refs += 1
            else:
                # Regular atomic tag
                atomic_tags += 1
                dt = tag.get('dataType', 'Unknown')
                type_counts[dt] = type_counts.get(dt, 0) + 1
        
        print(f"\nTag Composition:")
        print(f"  Atomic tags: {atomic_tags}")
        print(f"  Nested struct references: {nested_struct_refs}")
        print(f"  UDT references: {udt_refs}")
        
        if type_counts:
            print("\nAtomic Data Type Distribution:")
            for dt, count in type_counts.items():
                twincat_type = self._map_data_type(dt)
                print(f"  {dt} -> {twincat_type}: {count} tags")
        
        # Count read-only tags (only for atomic tags)
        readonly_count = sum(1 for tag in self.tags if tag.get('readOnly') and not tag.get('is_nested_struct') and not tag.get('is_udt_reference'))
        readwrite_count = atomic_tags - readonly_count
        
        if atomic_tags > 0:
            print(f"\nAtomic Tag Access:")
            print(f"  Read-only: {readonly_count}")
            print(f"  Read-write: {readwrite_count}")
        
        print("="*60)


def main():
    """Main function to run the converter."""
    print("Ignition to TwinCAT Struct Converter")
    print("====================================")
    
    # Get input file path
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = input("Enter path to Ignition JSON file: ").strip('"')
    
    if not input_file:
        print("No input file specified. Exiting.")
        return
    
    # Initialize converter
    converter = IgnitionToTwinCATConverter()
    
    # Load and convert
    if converter.load_ignition_json(input_file):
        # Save the converted struct (will use automatic naming and directory)
        if converter.save_twincat_file():
            converter.print_summary()
            
            # Show the TwinCAT struct name conversion
            twincat_name = converter._convert_to_twincat_name(converter.struct_name)
            print(f"\n🔄 Name Conversion:")
            print(f"   Ignition UDT: {converter.struct_name}")
            print(f"   TwinCAT Struct: {twincat_name}")
            
            # Ask if user wants to see the output
            show_output = input("\nDo you want to see the generated struct? (y/n): ").lower()
            if show_output in ['y', 'yes']:
                print("\n" + "="*60)
                print("GENERATED TWINCAT XML CONTENT")
                print("="*60)
                xml_content = converter.generate_twincat_xml()
                print(xml_content[:2000])  # Show first 2000 characters
                if len(xml_content) > 2000:
                    print("\n... (content truncated, full content saved to file)")
        else:
            print("Failed to save the converted file.")
    else:
        print("Failed to load the input file.")


if __name__ == "__main__":
    main()