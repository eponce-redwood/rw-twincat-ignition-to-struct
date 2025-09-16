# KEPware to Beckhoff UDT Converter

This directory contains Python scripts to automatically convert Ignition UDT JSON files from KEPware OPC format to Beckhoff TwinCAT OPC UA format.

## What the Conversion Does

The scripts automatically perform the following conversions:

1. **Parameter Updates**: 
   - Removes KEPware-specific parameters: `Node`, `TIA_PLC_Name`, `Datablock_Name`
   - Adds standardized parameters: `OPCTagPath`, `OPCServer`

2. **OPC Item Path Conversion**:
   - Changes from KEPware format: `nsu=KEPServerEX;s={Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}.TagName`
   - To Beckhoff format: `{OPCTagPath}.hmiIgnition.TagName`

3. **Value Source Updates**:
   - Changes `valueSource` from `"expr"` to `"opc"` for Boolean tags using bit extraction
   - Removes expression properties since Beckhoff exposes individual Boolean variables

4. **OPC Server References**:
   - Converts hardcoded server names to parameter binding: `{OPCServer}`

## Scripts

### 1. Single File Converter (`convert_kepware_to_beckhoff.py`)

Convert a single UDT file:

```bash
python convert_kepware_to_beckhoff.py input.json [output.json]
```

**Examples:**
```bash
# Convert with automatic output naming
python convert_kepware_to_beckhoff.py RW_Digital_Out_V2.json

# Convert with custom output name
python convert_kepware_to_beckhoff.py RW_Digital_Out_V2.json RW_Digital_Out_V2_Beckhoff.json
```

### 2. Batch Converter (`batch_convert_udts.py`)

Convert all JSON files in a directory:

```bash
python batch_convert_udts.py source_directory [output_directory]
```

**Examples:**
```bash
# Convert all files in ExtractedUDTs folder
python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/

# Convert with custom output directory
python batch_convert_udts.py ../Ignition-RW-Standard-ExtractedUDTs/ ./converted/
```

## After Conversion

Once files are converted, you need to customize the parameters for your specific setup:

### 1. Update OPCTagPath Parameter

Replace the placeholder with your actual OPC path:

**Default placeholder:**
```
nsu=urn:BeckhoffAutomation:Ua:PLC1;s=MAIN.YourTagNameHere
```

**Example for actual use:**
```
nsu=urn:BeckhoffAutomation:Ua:PLC1;s=MAIN.testInterlock
```

### 2. Update OPCServer Parameter

Replace the placeholder with your actual Beckhoff server name:

**Default placeholder:**
```
Beckhoff@YourComputerName
```

**Example for actual use:**
```
Beckhoff@CP-6796D4
```

You can find your server name in UA Expert or in the Beckhoff OPC UA server configuration.

## Conversion Output

The scripts provide detailed output showing:
- Which tags were processed
- What changes were made to each tag
- Conversion statistics summary
- Next steps for configuration

Example output:
```
Converting: RW_Digital_Out_V2.json
UDT Name: RW_Digital_Out_V2
  ✓ Updated parameters (removed KEPware-specific, added OPCTagPath/OPCServer)
  Processing tag: S_AlmNotify
    ✓ Updated opcItemPath: S_AlmNotify
    ✓ Updated opcServer to parameter binding
  Processing tag: Cfg_HasOos
    ✓ Updated opcItemPath: Cfg_HasOos
    ✓ Converted from expression to direct OPC (was bit extraction)
    ✓ Updated opcServer to parameter binding
  ...

==================================================
CONVERSION SUMMARY:
==================================================
  Parameters Updated: 1
  Opcitempath Updated: 12
  Valuesource Updated: 8
  Opcserver Updated: 12
  Expressions Removed: 8
==================================================
```

## Requirements

- Python 3.6 or higher
- No additional libraries required (uses only standard library)

## File Structure

```
Ignition-RW-Standard-BeckhoffConverted/
├── convert_kepware_to_beckhoff.py    # Single file converter
├── batch_convert_udts.py             # Batch converter
├── README.md                         # This file
├── RW_Digital_Out_V2_Beckhoff.json   # Example converted file
└── [other converted files...]
```

## Notes

- The scripts preserve all other UDT properties (permissions, history settings, etc.)
- Original files are never modified - new files are created
- The conversion is based on the manual conversion patterns established for the RW_Interlock_V2 and RW_Digital_Out_V2 UDTs
- Boolean tags using bit extraction expressions are automatically converted to direct OPC reads