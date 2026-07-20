# ZZYL MCP Tools

This manifest is generated from `backend/app/mcp/manifest.py`.
Claude must use the governed HTTP mapping and must not bypass admission confirmation.

## `agent.chat`

Send a natural-language request to the ZZYL agent.

- HTTP: `POST /api/agent/chat`
- Input schema: `{"additionalProperties": false, "properties": {"conversation_id": {"type": ["string", "null"]}, "message": {"minLength": 1, "type": "string"}}, "required": ["message"], "type": "object"}`

## `agent.checkin_recommendation`

Generate a check-in recommendation for an elder.

- HTTP: `POST /api/agent/checkin/recommendation`
- Input schema: `{"additionalProperties": false, "properties": {"elder_name": {"minLength": 1, "type": "string"}}, "required": ["elder_name"], "type": "object"}`

## `agent.care_plan`

Generate a care plan draft for an elder and goal.

- HTTP: `POST /api/agent/care-plan`
- Input schema: `{"additionalProperties": false, "properties": {"care_goal": {"type": "string"}, "elder_name": {"minLength": 1, "type": "string"}}, "required": ["elder_name"], "type": "object"}`

## `agent.alert_analysis`

Analyze a persisted alert by id.

- HTTP: `POST /api/agent/alert-analysis`
- Input schema: `{"additionalProperties": false, "properties": {"alert_id": {"exclusiveMinimum": 0, "type": "integer"}}, "required": ["alert_id"], "type": "object"}`

## `nursing.list_elders`

List elders visible to the service.

- HTTP: `GET /api/nursing/elders`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.list_rooms`

List rooms visible to the service.

- HTTP: `GET /api/nursing/rooms`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.list_beds`

List beds visible to the service.

- HTTP: `GET /api/nursing/beds`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.list_projects`

List nursing projects.

- HTTP: `GET /api/nursing/projects`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.list_alerts`

List alert records.

- HTTP: `GET /api/nursing/alerts`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.list_checkins`

List check-in applications.

- HTTP: `GET /api/nursing/checkins`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`

## `nursing.seed_demo_data`

Seed idempotent local demonstration data.

- HTTP: `POST /api/nursing/demo/seed`
- Input schema: `{"additionalProperties": false, "properties": {}, "type": "object"}`
