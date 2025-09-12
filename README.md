# Ignition to TwinCAT Struct Converter

This Python script converts Ignition tag definition JSON files to TwinCAT struct format, generating proper `.TcDUT` files that can be directly imported into TwinCAT projects.

## Features

- **TwinCAT XML Format**: Generates proper `.TcDUT` files with XML structure and unique GUIDs
- **Automatic Data Type Mapping**: Converts Ignition data types to appropriate TwinCAT types
- **TwinCAT Naming Convention**: Converts names like `RW_Digital_Out_V2` → `ST_RW_DigitalOut`
- **Comment Preservation**: Extracts tooltips from Ignition tags and converts them to TwinCAT comments
- **Default Values**: Automatically assigns appropriate default values for each data type
- **Read-Only Detection**: Adds comments for read-only tags
- **Memory Optimization**: Includes pack_mode attribute for efficient memory usage
- **Organized Output**: Saves files to `TwinCAT_Structs/` directory
- **Detailed Reporting**: Provides comprehensive conversion statistics

## Data Type Mappings

| Ignition Type | TwinCAT Type | Description |
|---------------|--------------|-------------|
| `Boolean` | `BOOL` | Boolean values |
| `Float4` | `REAL` | 32-bit floating point |
| `String` | `STRING` | Text strings |
| `Int4` | `INT` | 16-bit signed integer |
| `Int16` | `INT` | 16-bit signed integer |
| `Int32` | `DINT` | 32-bit signed integer |
| `UInt16` | `UINT` | 16-bit unsigned integer |
| `UInt32` | `UDINT` | 32-bit unsigned integer |
| `Double` | `LREAL` | 64-bit floating point |
| `Byte` | `BYTE` | 8-bit unsigned integer |

## Usage

### Command Line

```bash
python ignition_to_twincat.py "path/to/your/ignition_file.json"
```

### Interactive Mode

```bash
python ignition_to_twincat.py
```
Then enter the path when prompted.

### Programmatic Usage

```python
from ignition_to_twincat import IgnitionToTwinCATConverter

converter = IgnitionToTwinCATConverter()
if converter.load_ignition_json("your_file.json"):
    converter.save_twincat_file("output_struct.txt")
    converter.print_summary()
```

## Example Output

```xml
<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="ST_RW_DigitalOut" Id="{3738b510-b777-421b-a85c-32dcba7a068d}">
    <Declaration><![CDATA[    {attribute 'pack_mode' := '1'}
    (*
    ST_RW_DigitalOut
    ==================================================
    Generated from Ignition UDT: RW_Digital_Out_V2
    Total tags: 13
    Generated on: 2025-09-12 14:28:30
    *)
    TYPE ST_RW_DigitalOut :
    STRUCT
        // Output Command to IO Card
        S_Output : BOOL := FALSE;		// Read-only tag
        // 1= Manual Command to use Substitute PV (override input)
        HMI_C_ManAuto : BOOL := FALSE;
        // Manual-Entered Substitute Output
        HMI_C_ManSet : BOOL := FALSE;
        
        // ... more variables ...
        
    END_STRUCT
    END_TYPE
]]></Declaration>
  </DUT>
</TcPlcObject>
```

## Files Generated

The script creates `.TcDUT` files in the `TwinCAT_Structs/` directory containing:

1. **XML Header**: Proper TwinCAT XML structure with version and unique GUID
2. **Struct Declaration**: TwinCAT TYPE/STRUCT format within CDATA section
3. **Memory Attributes**: Pack mode for optimization
4. **Variable Declarations**: Each tag with appropriate data type, default values, and comments
5. **Documentation**: Header comments with generation info and source details

## Features Extracted from Ignition JSON

### ✅ Converted
- Tag names (variable names)
- Data types (with mapping)
- Tooltips (as comments)
- Read-only status (as attributes)

### ❌ Not Converted (Ignition-specific)
- OPC server settings
- Security permissions
- History configuration
- Tag groups
- Expressions and bindings

## Example Test Run

```
Ignition to TwinCAT Struct Converter
====================================
Loaded 64 tags from Ignition-RW-Standard\RW_Analog_In_V2.json
Created output directory: TwinCAT_Structs
TwinCAT struct saved to: TwinCAT_Structs\ST_RW_AnalogIn.TcDUT

============================================================
CONVERSION SUMMARY
============================================================
Original Ignition UDT: RW_Analog_In_V2
TwinCAT Struct Name: ST_RW_AnalogIn
Total Tags: 64

Data Type Distribution:
  Boolean -> BOOL: 33 tags
  Float4 -> REAL: 29 tags
  Int4 -> INT: 2 tags

Read-only tags: 25
Read-write tags: 39
============================================================

🔄 Name Conversion:
   Ignition UDT: RW_Analog_In_V2
   TwinCAT Struct: ST_RW_AnalogIn
```

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## File Structure

```
rw-twincat-ignition-to-struct/
├── ignition_to_twincat.py      # Main converter script
├── example_usage.py            # Example usage script
├── README.md                   # This documentation
└── Ignition-RW-Standard/
    ├── RW_Analog_In_V2.json           # Input Ignition JSON
    └── RW_Analog_In_V2_TwinCAT.txt    # Generated TwinCAT struct
```

## Notes

- Variable names are sanitized to follow TwinCAT naming conventions
- Long tooltips are truncated to 80 characters for readability
- The script preserves the original tag order from the JSON file
- Memory pack mode is automatically applied for efficient PLC memory usage

## Future Enhancements

- Support for nested structures
- Array type handling
- Batch processing of multiple JSON files
- Custom data type mapping configuration
- Integration with TwinCAT project files