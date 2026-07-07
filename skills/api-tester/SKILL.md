---
name: api-tester
description: Quick API endpoint testing using curl with structured output
---

# API Tester

Interactive API testing tool that constructs and executes HTTP requests.

## When to use

- Quick manual testing of an API endpoint during development
- Debugging a failing request
- Verifying API behavior without a dedicated client

## Instructions

1. **Ask for the endpoint details** — method (GET, POST, PUT, DELETE, PATCH), URL, headers, body
2. **Construct the curl command** with proper flags:
   - `-X METHOD` for HTTP method
   - `-H "Header: value"` for each header
   - `-d '{"key": "value"}'` for JSON body
   - `-v` for verbose output (include response headers)
3. **Execute and display results** — show status code, response headers, and body
4. **Format the response** — pretty-print JSON, show timing information

## Example

```bash
# POST to create a resource
curl -X POST http://localhost:3000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' \
  -w "\n\n⏱ Timing: %{time_total}s\n"

# GET with verbose output
curl -v http://localhost:3000/abc1234
```

## Common scenarios

- **Auth testing**: `-H "Authorization: Bearer <token>"`
- **File upload**: `-F "file=@path/to/file"`
- **Query params**: `"http://localhost:3000/api?page=1&limit=10"`
- **Follow redirects**: `-L` flag
- **Custom timeout**: `--connect-timeout 5 --max-time 10`
