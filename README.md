# Ignition to TwinCAT Struct Converter

This Python script converts Ignition tag definition JSON files to TwinCAT struct format, generating proper `.TcDUT` files that can be directly imported into TwinCAT projects. Supports batch processing of multiple UDT files with comprehensive data type mapping.

## Features

- **✅ Batch Processing**: Convert all UDT files in a folder with a single command using `batch_convert_udts.py`
- **✅ Comprehensive Data Type Mapping**: Full Ignition → TwinCAT type conversion based on official documentation
- **✅ Array Support**: Handles Ignition arrays and converts them to proper TwinCAT array syntax
- **✅ TwinCAT XML Format**: Generates proper `.TcDUT` files with XML structure and unique GUIDs
- **✅ Smart Tooltip Handling**: Handles both string tooltips and complex binding-based tooltip objects
- **✅ TwinCAT Naming Convention**: Converts names like `RW_Digital_Out_V2` → `ST_RW_DigitalOut_HMI_IgnitionExp`
- **✅ OPC UA Integration**: Includes proper OPC UA pragmas for seamless HMI integration
- **✅ Comment Preservation**: Extracts tooltips and converts them to TwinCAT comments and OPC descriptions
- **✅ Proper Default Values**: TwinCAT-compliant default values for all data types
- **✅ Read-Only Detection**: Proper OPC UA access attributes for read-only tags
- **✅ Memory Optimization**: Includes pack_mode attribute for efficient memory usage
- **✅ Organized Output**: Saves files to `TwinCAT_Structs/` directory with proper naming
- **✅ Detailed Reporting**: Comprehensive conversion statistics and error handling

## Data Type Mappings

Based on official Ignition and TwinCAT documentation:

| Ignition Type | TwinCAT Type | Description | Notes |
|---------------|--------------|-------------|-------|
| `Boolean` | `BOOL` | Boolean values | Standard mapping |
| `Byte` | `USINT` | 8-bit unsigned (0-255) | Ignition Byte → TwinCAT USINT |
| `Short` | `INT` | 16-bit signed integer | Standard mapping |
| `Integer` | `DINT` | 32-bit signed integer | Standard mapping |
| `Long` | `LINT` | 64-bit signed integer | Standard mapping |
| `Float` | `REAL` | 32-bit floating point | Standard mapping |
| `Double` | `LREAL` | 64-bit floating point | Standard mapping |
| `String` | `STRING` | Text strings | Standard mapping |
| `DateTime` | `DT` | Date and time | TwinCAT DATE_AND_TIME |
| **Legacy/Export Types** | | | |
| `Float4` | `REAL` | 4-byte float (legacy) | Same as Float |
| `Float8` | `LREAL` | 8-byte float (legacy) | Same as Double |
| `Int4` | `DINT` | 4-byte integer (legacy) | Same as Integer |
| `Int8` | `SINT` | 8-bit signed integer | TwinCAT signed byte |
| `Int16` | `INT` | 16-bit signed integer | Same as Short |
| `Int32` | `DINT` | 32-bit signed integer | Same as Integer |
| `UInt16` | `UINT` | 16-bit unsigned integer | TwinCAT unsigned |
| `UInt32` | `UDINT` | 32-bit unsigned integer | TwinCAT unsigned |
| **Array Types** | | | |
| `String Array` | `ARRAY[0..255] OF STRING` | String arrays | Fixed size arrays |
| `StringArray` | `ARRAY[0..255] OF STRING` | String arrays (shorthand) | Export format |
| `Boolean Array` | `ARRAY[0..255] OF BOOL` | Boolean arrays | Fixed size arrays |
| `Integer Array` | `ARRAY[0..255] OF DINT` | Integer arrays | Fixed size arrays |
| `Float Array` | `ARRAY[0..255] OF REAL` | Float arrays | Fixed size arrays |
| `Double Array` | `ARRAY[0..255] OF LREAL` | Double arrays | Fixed size arrays |

## Usage

### Batch Processing (Recommended)

Process all UDT JSON files in the `Ignition-RW-Standard-ExtractedUDTs/` folder:

```bash
python batch_convert_udts.py
```

This will:
- Find all `.json` files in the UDT folder
- Convert each one to TwinCAT format
- Save results to `TwinCAT_Structs/` directory
- Provide detailed conversion statistics
- Handle errors gracefully and report success/failure for each file

### Single File Conversion

#### Command Line
```bash
python ignition_to_twincat.py "path/to/your/ignition_file.json"
```

#### Interactive Mode
```bash
python ignition_to_twincat.py
```
Then enter the path when prompted.

### Programmatic Usage

```python
from ignition_to_twincat import IgnitionToTwinCATConverter

converter = IgnitionToTwinCATConverter()
if converter.load_ignition_json("your_file.json"):
    converter.save_twincat_file()  # Auto-generates filename
    converter.print_summary()
```

## Example Output

```xml
<?xml version="1.0" encoding="utf-8"?>
<TcPlcObject Version="1.1.0.1">
  <DUT Name="ST_RW_DigitalOut_HMI_IgnitionExp" Id="{3738b510-b777-421b-a85c-32dcba7a068d}">
    <Declaration><![CDATA[    {attribute 'pack_mode' := '1'}
    {attribute 'OPC.UA.DA' := '1'}
    {attribute 'OPC.UA.DA.StructuredType' := '1'}
    (*
    ST_RW_DigitalOut_HMI_IgnitionExp
    ==================================================
    Generated from Ignition UDT: RW_Digital_Out_V2
    Total tags: 13
    Generated on: 2025-09-12 15:45:00
    
    Data type mappings (Ignition -> TwinCAT):
    - Boolean -> BOOL
    - Integer -> DINT, Long -> LINT, Short -> INT
    - Float -> REAL, Double -> LREAL
    - String -> STRING, DateTime -> DT
    - Arrays -> ARRAY[0..255] OF <type>
    *)
    TYPE ST_RW_DigitalOut_HMI_IgnitionExp :
    STRUCT
        {attribute 'OPC.UA.DA' := '1'}
        {attribute 'OPC.UA.DA.Access' := '1'}
        {attribute 'OPC.UA.DA.Description' := 'Output Command to IO Card'}
        // Output Command to IO Card
        S_Output : BOOL := FALSE;		// Read-only tag
        
        {attribute 'OPC.UA.DA' := '1'}
        {attribute 'OPC.UA.DA.Description' := '1= Manual Command to use Substitute PV (override input)'}
        // 1= Manual Command to use Substitute PV (override input)
        HMI_C_ManAuto : BOOL := FALSE;
        
        {attribute 'OPC.UA.DA' := '1'}
        {attribute 'OPC.UA.DA.Description' := 'Manual-Entered Substitute Output'}
        // Manual-Entered Substitute Output
        HMI_C_ManSet : BOOL := FALSE;
        
        // Array example
        {attribute 'OPC.UA.DA' := '1'}
        TimeLimitedFeatures : ARRAY[0..255] OF STRING;
        
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
3. **Memory Attributes**: Pack mode for optimization and OPC UA exposure
4. **OPC UA Pragmas**: Complete OPC UA integration with descriptions and access control
5. **Variable Declarations**: Each tag with appropriate data type, default values, and comments
6. **Documentation**: Header comments with generation info, source details, and mapping reference
7. **Array Support**: Proper TwinCAT array syntax for complex data types

## Batch Processing Results

Example batch run converting 33 UDT files:

```
Batch UDT to TwinCAT Converter
==================================================
Found 33 UDT JSON files to convert:
   1. RW_Analog_In_V2.json
   2. RW_Bool_MB.json
   ... (continues for all files)

==================================================
Starting batch conversion...
==================================================

[1/33] Converting: RW_Analog_In_V2.json
----------------------------------------
Loaded 64 tags from RW_Analog_In_V2.json
TwinCAT struct saved to: TwinCAT_Structs\ST_RW_AnalogIn_HMI_IgnitionExp.TcDUT
✅ SUCCESS: RW_Analog_In_V2.json converted successfully

... (continues for all files)

============================================================
BATCH CONVERSION COMPLETE
============================================================
Total files processed: 33
Successful conversions: 33
Failed conversions: 0

✅ SUCCESSFULLY CONVERTED (33):
   - All UDT files converted successfully

📁 OUTPUT DIRECTORY: TwinCAT_Structs/
   Generated 33 TwinCAT struct files (.TcDUT)

============================================================
🎉 All UDT conversions completed successfully!
```

## Features Extracted from Ignition JSON

### ✅ Converted
- **Tag names** (variable names with sanitization)
- **Data types** (comprehensive Ignition → TwinCAT mapping)
- **Tooltips** (as TwinCAT comments and OPC UA descriptions)
- **Read-only status** (as OPC UA access attributes)
- **Arrays** (converted to TwinCAT array syntax)
- **Binding information** (extracted from complex tooltip objects)

### ❌ Not Converted (Ignition-specific)
- OPC server connection settings
- Security permissions and roles
- History configuration and deadbands
- Tag groups and folder structure
- Expressions and complex bindings
- Alarm configurations

## Example Single File Conversion

```
Ignition to TwinCAT Struct Converter
====================================
Loaded 7 tags from RW_KEPServerEX_Debug_Info.json
TwinCAT struct saved to: TwinCAT_Structs\ST_RW_KepserverexDebugInfo_HMI_IgnitionExp.TcDUT

============================================================
CONVERSION SUMMARY
============================================================
Original Ignition UDT: RW_KEPServerEX_Debug_Info
TwinCAT Struct Name: ST_RW_KepserverexDebugInfo_HMI_IgnitionExp
Total Tags: 7

Data Type Distribution:
  DateTime -> DT: 1 tags
  Int8 -> SINT: 3 tags
  StringArray -> ARRAY[0..255] OF STRING: 2 tags
  String -> STRING: 1 tags

Read-only tags: 7
Read-write tags: 0
============================================================

🔄 Name Conversion:
   Ignition UDT: RW_KEPServerEX_Debug_Info
   TwinCAT Struct: ST_RW_KepserverexDebugInfo_HMI_IgnitionExp
```

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)

## File Structure

```
rw-twincat-ignition-to-struct/
├── ignition_to_twincat.py              # Main converter script
├── batch_convert_udts.py               # Batch processing script
├── README.md                           # This documentation
├── Ignition-RW-Standard-ExtractedUDTs/ # Input folder with UDT JSON files
│   ├── RW_Analog_In_V2.json
│   ├── RW_Bool_MB.json
│   ├── RW_KEPServerEX_Debug_Info.json
│   └── ... (33 total UDT files)
└── TwinCAT_Structs/                    # Generated output files
    ├── ST_RW_AnalogIn_HMI_IgnitionExp.TcDUT
    ├── ST_RW_BoolMb_HMI_IgnitionExp.TcDUT
    ├── ST_RW_KepserverexDebugInfo_HMI_IgnitionExp.TcDUT
    └── ... (33 total TwinCAT struct files)
```

## Key Improvements Made

### Version 2.0 Updates (September 2025)
- ✅ **Fixed tooltip handling**: Now properly handles both string tooltips and complex binding objects
- ✅ **Comprehensive data type mapping**: Based on official Ignition and TwinCAT documentation
- ✅ **Array support**: Full conversion of Ignition arrays to TwinCAT array syntax
- ✅ **Batch processing**: Process entire UDT folders with single command
- ✅ **Enhanced OPC UA integration**: Complete pragma support for HMI connectivity
- ✅ **Error handling**: Robust error handling and detailed reporting
- ✅ **Proper default values**: TwinCAT-compliant defaults (e.g., `DT#1970-01-01-00:00:00` for DateTime)

### Original Issues Fixed
- **TypeError on tooltip processing**: Complex tooltip objects now handled correctly
- **Unknown data type warnings**: All Ignition types now properly mapped to TwinCAT equivalents
- **Missing array support**: Arrays now converted to proper TwinCAT syntax
- **Inconsistent naming**: Standardized naming convention with `_HMI_IgnitionExp` suffix

## Notes

- Variable names are sanitized to follow TwinCAT naming conventions
- Long tooltips are handled appropriately and preserved in OPC UA descriptions
- The script preserves the original tag order from the JSON file
- Memory pack mode is automatically applied for efficient PLC memory usage
- All generated files include comprehensive documentation headers
- Arrays use fixed size `[0..255]` - adjust if needed for your specific requirements

