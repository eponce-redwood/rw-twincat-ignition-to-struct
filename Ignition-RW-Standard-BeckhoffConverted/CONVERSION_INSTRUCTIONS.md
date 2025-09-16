# Converting Ignition UDT Tags from KEPware to Beckhoff

This document provides step-by-step instructions for converting Ignition UDT (User Defined Type) tags from KEPware format to Beckhoff TwinCAT format.

## Overview

The conversion process involves changing OPC item paths from KEPware's hierarchical structure to Beckhoff's OPC UA format, which uses namespace 4 (`ns=4`) and simplified tag paths.

## Key Differences

### KEPware Format (Before)
```json
"opcItemPath": {
  "bindType": "parameter",
  "binding": "nsu=KEPServerEX;s={Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}.TagName"
}
"opcServer": "KEPServerEX_CHP01"
```

### Beckhoff Format (After)
```json
"opcItemPath": {
  "bindType": "parameter",
  "binding": "nsu=urn:BeckhoffAutomation:Ua:PLC1;s={OPCTagPath}.hmiIgnition.TagName"
}
"opcServer": {
  "bindType": "parameter",
  "binding": "{OPCServer}"
}
```

## Step-by-Step Conversion Process

### 1. Identify Tags to Convert

Look for tags with these characteristics:
- `opcItemPath` containing `nsu=KEPServerEX`
- Hardcoded `opcServer` values like `KEPServerEX_CHP01`
- Complex path structures with `{Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}`

### 2. Update OPC Item Paths

For each tag, replace the KEPware path format:

**Find:**
```json
"opcItemPath": {
  "bindType": "parameter",
  "binding": "nsu=KEPServerEX;s={Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}.TagName"
}
```

**Replace with:**
```json
"opcItemPath": {
  "bindType": "parameter",
  "binding": "nsu=urn:BeckhoffAutomation:Ua:PLC1;s={OPCTagPath}.hmiIgnition.TagName"
}
```

### 3. Update OPC Server References

**Replace hardcoded server:**
```json
"opcServer": "KEPServerEX_CHP01"
```

**With parameter binding:**
```json
"opcServer": {
  "bindType": "parameter",
  "binding": "{OPCServer}"
}
```

### 4. Handle Special Cases

#### Float Tags with @Long Suffix
Remove the `@Long` suffix from Beckhoff paths:

**KEPware:**
```json
"binding": "nsu=KEPServerEX;s={Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}.HMI_Cfg_IntlkOffDly@Long"
```

**Beckhoff:**
```json
"binding": "nsu=urn:BeckhoffAutomation:Ua:PLC1;s={OPCTagPath}.hmiIgnition.HMI_Cfg_IntlkOffDly"
```

#### Mixed Format Tags
Some tags might already use `ns=4` format but still reference KEPware servers. Update these to use consistent Beckhoff formatting.

## Example Conversion

### Before (KEPware)
```json
{
  "opcItemPath": {
    "bindType": "parameter",
    "binding": "nsu=KEPServerEX;s={Node}.{TIA_PLC_Name}.Blocks.{Datablock_Name}.S_Tripped"
  },
  "valueSource": "expr",
  "expression": "{[.]S_HMIBits}&8",
  "dataType": "Boolean",
  "name": "S_Tripped",
  "opcServer": "KEPServerEX_CHP01"
}
```

### After (Beckhoff)
```json
{
  "opcItemPath": {
    "bindType": "parameter",
    "binding": "ns=4;s={PLCTagPath}.hmiIgnition.S_Tripped"
  },
  "opcServer": {
    "bindType": "parameter",
    "binding": "{PLCName}"
  },
  "valueSource": "expr",
  "expression": "{[.]S_HMIBits}&8",
  "dataType": "Boolean",
  "name": "S_Tripped"
}
```

## Validation Checklist

After conversion, verify:

- [ ] All `opcItemPath` bindings use `nsu=urn:BeckhoffAutomation:Ua:PLC1;s={OPCTagPath}.hmiIgnition.TagName` format
- [ ] No hardcoded `KEPServerEX_CHP01` references remain
- [ ] All `opcServer` entries use parameter binding `{OPCServer}`
- [ ] No `@Long` suffixes in Beckhoff paths
- [ ] JSON syntax is valid (no duplicate keys)

## UDT Parameters Required

When using the converted UDT, ensure these parameters are defined:

```json
"parameters": {
  "OPCTagPath": {
    "dataType": "String",
    "value": ""
  },
  "OPCServer": {
    "dataType": "String", 
    "value": ""
  }
}
```

## Usage Example

When creating a tag instance, you need to specify:

### Required Parameters:
- **OPCTagPath**: `MAIN.testInterlock` (base path to your TwinCAT variable)
- **OPCServer**: The exact name of your Beckhoff OPC UA connection in Ignition
  - Check Config → OPC UA → Connections in Ignition Gateway
  - Common names: `BeckhoffOPCUA`, `TwinCAT_OPC_UA`, `Beckhoff_PLC`
  - Use the exact "Connection Name" from your Ignition configuration

### Finding Your OPC Connection Name:
1. Open Ignition Gateway webpage
2. Navigate to Config → OPC UA → Connections  
3. Find your Beckhoff/TwinCAT connection
4. Use the exact value from the "Connection Name" column

### Example Configuration:
```json
{
  "OPCTagPath": "MAIN.testInterlock",
  "OPCServer": "BeckhoffOPCUA"
}
```

The resulting OPC paths will be:
- `nsu=urn:BeckhoffAutomation:Ua:PLC1;s=MAIN.testInterlock.hmiIgnition.S_Tripped`
- `nsu=urn:BeckhoffAutomation:Ua:PLC1;s=MAIN.testInterlock.hmiIgnition.HMI_C_Reset`
- etc.

## Common Errors to Avoid

1. **Duplicate opcServer keys**: Remove hardcoded values before adding parameter bindings
2. **Mixing formats**: Don't combine KEPware and Beckhoff path styles in the same UDT
3. **Missing hmiIgnition**: Ensure the `.hmiIgnition.` structure is included in all paths
4. **Incorrect namespace**: Always use `ns=4` for Beckhoff OPC UA

## Files Converted

- ✅ `RW_Interlock_V2_Beckhoff.json` - Completed conversion example

## Next Steps

1. Use this document to convert other UDT files in the workspace
2. Test converted UDTs with actual Beckhoff hardware
3. Update any dependent configurations or templates
4. Document any TwinCAT-specific requirements discovered during testing