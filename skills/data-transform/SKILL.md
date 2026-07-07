---
name: data-transform
description: Convert between JSON, CSV, YAML, base64, date formats, and other data formats
---

# Data Transform

Converts data between common formats for data migration and API integration.

## When to use

- You need to convert data from one format to another
- Processing CSV exports or JSON API responses
- Encoding/decoding base64 or date strings
- Transforming data between different schemas

## Instructions

1. **Identify the source format** — JSON, CSV, YAML, XML, base64, or raw text
2. **Identify the target format** — what format does the consumer expect?
3. **Handle edge cases**:
   - Nested objects vs flat CSV columns
   - Arrays vs repeating field prefixes
   - Special characters and encoding
   - Date/time zone conversions
4. **Generate the transformed output** with a summary of what was transformed

## Common transformations

| From | To | Notes |
|------|----|-------|
| JSON | CSV | Flatten nested structures into dot-notation columns |
| CSV | JSON | Detect types (strings, numbers, booleans) from values |
| JSON | YAML | Preserve structure, add comments |
| base64 | string | Handle character encoding (UTF-8, Latin-1) |
| ISO 8601 | locale date | Handle timezone conversions |
| XML | JSON | Map attributes vs elements |

## Example

```javascript
// JSON → CSV transformation
// Input: [{ "name": "Alice", "age": 30 }, { "name": "Bob", "age": 25 }]
// Output:
// name,age
// Alice,30
// Bob,25
```

## Edge cases

- Empty arrays or objects (output empty file or null?)
- Mixed types in arrays (warn about type coercion)
- Very large files (stream processing vs in-memory)
- Unicode and special characters (ensure proper encoding)
