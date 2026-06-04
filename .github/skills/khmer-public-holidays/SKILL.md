---
name: khmer-public-holidays-api
description: "Create and implement a Khmer public holidays API with endpoints, data model, validation, tests, and documentation."
user-invocable: true
---

# Khmer Public Holidays API

This skill guides the creation of a workspace-scoped API for Khmer public holidays. It is designed for building or extending a backend service with:
- holiday data model and validation
- REST API endpoints for list, detail, create, update, delete
- locale-aware Khmer and English names
- persistence, tests, and documentation

## Use when

- you want to implement a new API for Khmer public holidays
- you want to design or refactor holiday endpoints for a project
- you want a reproducible workflow for holiday data modeling, validation, and docs

## Workflow

1. Confirm the target stack and deployment scope
   - language / framework (Node.js, Python, Java, .NET, etc.)
   - database or storage option (SQL, NoSQL, JSON, in-memory)
   - whether the repository already contains API patterns to follow

2. Define the Khmer holiday domain model
   - required fields: `id`, `name_kh`, `name_en`, `date`
   - optional fields: `type`, `description`, `is_fixed`, `notes`, `locale`
   - validation rules: valid ISO date, non-empty names, unique date per holiday
   - support Khmer names and translations consistently

3. Design API contract and routes
   - `GET /holidays` → list all holidays
   - `GET /holidays/:id` → holiday details
   - `POST /holidays` → create a holiday
   - `PUT /holidays/:id` or `PATCH /holidays/:id` → update a holiday
   - `DELETE /holidays/:id` → remove a holiday
   - include example request/response payloads and status codes

4. Implement the service layer
   - map routes to controllers or handlers
   - add validation and error handling
   - implement persistence for holiday records
   - include Khmer-specific formatting or locale metadata when needed

5. Add tests and examples
   - unit tests for validation, model rules, and route behavior
   - integration tests for endpoint responses
   - sample data for Khmer public holidays and edge cases

6. Document the API
   - describe holiday fields, required payloads, and response shapes
   - include examples for Khmer and English holiday names
   - note any locale-specific behavior or data conventions

## Quality checks

- API includes both Khmer and English name fields
- dates are validated and normalized to ISO format
- create/update operations reject invalid or duplicate holidays
- list/detail endpoints return consistent payloads
- tests cover successful and failing paths
- documentation clearly explains usage and sample payloads

## Clarifying questions

If details are missing, ask:
- Which backend stack should this API use?
- Should holiday data be stored in a database or a static JSON file?
- Do we need multilingual responses or only Khmer naming?
- Should the API support public holiday categories or fixed vs movable dates?

## Example prompts

- "Create a Khmer public holidays API in Node.js with Express and SQLite."
- "Add REST endpoints for Khmer public holidays to the existing backend."
- "Design holiday data validation rules for Khmer public holiday records."
- "Generate tests and documentation for Khmer public holiday endpoints."
