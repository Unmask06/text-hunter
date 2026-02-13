# Use Cases

TextHunter is designed to solve common data extraction challenges in the Oil & Gas industry. Here are real-world use cases and how to apply them.

## Line List Generation

### Overview
Extract line numbers from P&IDs and isometric drawings to create comprehensive line lists without manual data entry.

### Industry Context
In Oil & Gas projects, line lists are critical documents that catalog all process piping. When working with AutoCAD-based P&IDs (rather than SPPID), extracting line numbers from drawings is typically a manual process.

### How to Use TextHunter

**Step 1: Prepare Your Documents**
- Export your P&IDs or isometric drawings to PDF from AutoCAD
- Ensure line numbers are text (not raster images)

**Step 2: Define Line Number Pattern**

Common line number formats in Oil & Gas:
```
Format: XX-XXX-XXXX-XXX
Examples:
- 12-AB-1234-A1B (2-digit area, 2-char service, 4-digit sequence, class)
- 24-PW-5678-C2D (Process Water line)
- 10-FG-9012-D3E (Fuel Gas line)

Regex Pattern: \d{2}-[A-Z]{2,3}-\d{4}-[A-Z]\d[A-Z]?
```

**Alternative Formats:**
```
# Simpler format: XX-XXXX-XX
Pattern: \d{2}-\d{4}-[A-Z]{2}
Examples: 12-1234-AB, 24-5678-CD

# With line size: X"-XX-XXXX
Pattern: \d{1,2}"-[A-Z]{2}-\d{4}
Examples: 6"-AB-1234, 12"-PW-5678
```

**Step 3: Extract and Export**
- Upload all P&ID PDFs
- Apply the line number pattern
- Export to Excel with drawing references

**Step 4: Post-Processing**
- Sort by area or service code
- Add additional columns (line size, specification, material)
- Import to your line list database

### Benefits
- ✅ Eliminate manual transcription errors
- ✅ Process 100+ drawings in minutes
- ✅ Ensure no lines are missed
- ✅ Easy updates when drawings are revised

---

## Instrument List Extraction

### Overview
Create instrument indexes from P&IDs by extracting all instrument tags, perfect for instrument database population and verification.

### Industry Context
Instrument lists are essential for procurement, installation, and maintenance. When P&IDs are created in AutoCAD (not SPPID), there's no built-in database to export from - the drawings are the source of truth.

### How to Use TextHunter

**Step 1: Understanding Instrument Tag Formats**

Common ISA tag formats:
```
Format: FFF-XXXX[S]
Where:
- F = Function (1-3 letters)
- X = Loop number (3-4 digits)
- S = Suffix (optional, for splits/redundancy)

Examples by Function:
- FT-101, FT-2345A    (Flow Transmitter)
- PT-501, PT-6789B    (Pressure Transmitter)
- LT-301, LT-4567     (Level Transmitter)
- TT-201, TT-8901C    (Temperature Transmitter)
- AIT-401             (Analyzer Indicating Transmitter)
- FCV-102, FCV-2346A  (Flow Control Valve)
- PCV-502, PCV-6790B  (Pressure Control Valve)
- PSV-601, PSV-7891   (Pressure Safety Valve)
```

**Step 2: Define Patterns**

Basic instrument pattern:
```regex
[A-Z]{2,3}-\d{3,4}[A-Z]?

Matches:
✓ FT-101
✓ PT-2345
✓ LT-401A
✓ AIT-5678B
```

Specific instrument types:
```regex
# All transmitters (ending with T)
[A-Z]{1,2}T-\d{3,4}[A-Z]?

# All control valves (ending with V or CV)
[A-Z]{1,2}[C]?V-\d{3,4}[A-Z]?

# All indicators (containing I)
[A-Z]*I[A-Z]+-\d{3,4}[A-Z]?
```

**Step 3: Extract by Area or System**

Upload P&IDs by area and use file identifier patterns to track location:
```regex
# Extract drawing number from filename
# Example: P&ID-12-AB-001.pdf → 12-AB-001
P&ID-(\d{2}-[A-Z]{2}-\d{3})
```

**Step 4: Build Your Instrument Database**
- Export to Excel
- Add columns: Service, Type, Range, Location
- Import to your CMMS or instrument tracking system

### Benefits
- ✅ Complete instrument count for procurement
- ✅ Verify instrument index against drawings
- ✅ Track instruments by area or system
- ✅ Foundation for hook-up drawing lists

---

## Equipment List Generation

### Overview
Extract equipment tags from general arrangement drawings, plot plans, and P&IDs to create comprehensive equipment lists.

### Industry Context
Equipment lists are needed for:
- Equipment procurement and tracking
- Maintenance planning (CMMS setup)
- Construction planning
- Commissioning checklists

For AutoCAD-based designs, equipment tags must be manually extracted from drawings - a time-consuming and error-prone process.

### How to Use TextHunter

**Step 1: Equipment Tag Formats**

Standard equipment tags:
```
Format: X-XXXX[S]
Where:
- First letter = Equipment type
- Numbers = Sequence
- Suffix = Parallel/standby units

Examples:
- P-101A, P-101B      (Pumps - parallel)
- V-2301              (Vessel)
- E-4501A, E-4501B    (Heat Exchangers - parallel)
- C-789               (Compressor)
- T-1234              (Tank)
- F-567               (Filter)
- R-890               (Reactor)
- S-123               (Separator)
```

**Step 2: Define Equipment Patterns**

All equipment:
```regex
[A-Z]{1,2}-\d{3,4}[A-Z]?

Matches:
✓ P-101A
✓ V-2301
✓ E-4501B
✓ C-789
```

Specific equipment types:
```regex
# All pumps
P-\d{3,4}[A-Z]?

# All vessels (V, T, S, R)
[VTSR]-\d{3,4}[A-Z]?

# All rotating equipment (P, C, B for pumps, compressors, blowers)
[PCB]-\d{3,4}[A-Z]?
```

**Step 3: Extract from Multiple Drawing Types**

TextHunter can process:
- General Arrangement Drawings
- Plot Plans
- P&IDs
- Equipment Layout Drawings

Upload all relevant PDFs to get complete coverage.

**Step 4: Create Master Equipment List**
- Export to Excel
- Remove duplicates (equipment appears on multiple drawings)
- Add columns: Description, Size, Vendor, Location
- Track installation status

### Benefits
- ✅ Complete equipment count for budgeting
- ✅ Foundation for maintenance planning
- ✅ Construction material requisitions
- ✅ Commissioning package preparation

---

## Advanced Use Cases

### 1. Valve List Extraction

Extract all valve tags from P&IDs:
```regex
# Valve format: XXX-XXXX or XX-XXXX
[A-Z]{2,3}-\d{4}

Examples:
- HV-1234    (Hand Valve)
- CV-5678    (Check Valve)
- BDV-9012   (Blow Down Valve)
- MOV-3456   (Motor Operated Valve)
```

### 2. Drawing Number Extraction

Extract drawing numbers from title blocks:
```regex
# Format: P&ID-XX-XXX-XXX
P&ID-\d{2}-[A-Z]{2,3}-\d{3}

# Format: ISO-XXXX-XX-XX
ISO-\d{4}-\d{2}-\d{2}
```

### 3. Specification Call-outs

Extract pipe specifications:
```regex
# Format: SPEC-XXXX
SPEC-\d{4}[A-Z]?

Examples:
- SPEC-1234
- SPEC-5678A
```

### 4. Area Classification

Extract area classification zones:
```regex
# Format: DIV X, ZONE X, or CLASS X
(DIV|ZONE|CLASS)\s+[012]

Examples:
- DIV 1
- ZONE 2
- CLASS 1
```

### 5. Material Take-Off

Extract valve and fitting counts:
```regex
# Format: (QTY X) or QTY: X
(?:QTY:?\s+|[(]QTY\s+)(\d+)
```

---

## Integration with Workflows

### Quality Assurance
- Extract tags from as-built drawings
- Compare against original design
- Identify discrepancies or additions

### Document Control
- Extract revision numbers and dates
- Track drawing changes over time
- Maintain revision history

### Procurement
- Generate material requisitions from line lists
- Create purchase orders from equipment lists
- Track vendor tag numbers

### Construction
- Create installation work packages
- Generate punch lists
- Track completion status

### Commissioning
- Create system boundaries from line lists
- Generate instrument calibration lists
- Build loop check sheets

---

## Best Practices

### 📋 Document Preparation
1. **Ensure Text Quality**: Use CAD-to-PDF export rather than scanning when possible
2. **Consistent Naming**: Use systematic PDF filenames for easier sorting
3. **Batch by Type**: Process similar drawings together (all P&IDs, then all ISOs)

### 🎯 Pattern Development
1. **Start Small**: Test pattern on one PDF before batch processing
2. **Use Samples**: Collect 5-10 examples before creating pattern
3. **Validate Results**: Spot-check exports against original drawings

### 📊 Data Management
1. **Export Regularly**: Save Excel files after each extraction session
2. **Version Control**: Track extraction dates and drawing revisions
3. **Backup Data**: Keep copies of both PDFs and exported data

### 🔄 Continuous Improvement
1. **Refine Patterns**: Update regex as you find edge cases
2. **Build Library**: Save successful patterns for reuse
3. **Share Knowledge**: Document patterns for team members

---

## Industry-Specific Tips

### Offshore Platforms
- Equipment often includes deck/module location (e.g., "A-P-101" for Module A)
- Include location prefix in your pattern

### Refineries
- Complex line numbering with unit numbers (e.g., "U100-12-AB-1234")
- Pattern must account for unit prefix

### Pipeline Projects
- Line numbers include KP (kilometer post) references
- May need to extract both line tag and location

### LNG Facilities
- Cryogenic lines have special designation
- Equipment includes complex heat exchanger bundles

---

## Summary

TextHunter streamlines data extraction from technical drawings, saving hours of manual work while reducing errors. Whether you're generating line lists, instrument lists, or equipment lists, the pattern-based approach adapts to your specific naming conventions and document formats.

**Ready to start?** Return to the [How to Use](/how-to-use) guide to begin extracting data from your PDFs.

**Questions?** The key is starting with good examples and refining your patterns based on results. The AI regex generator can help if you're not familiar with regular expressions.
