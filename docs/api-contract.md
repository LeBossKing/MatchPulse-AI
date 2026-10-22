# API contract

## Implemented: GET /health

No request body or authentication is required in this local development foundation.

Successful response (`200 OK`):

```json
{
  "status": "ok",
  "service": "matchpulse-api",
  "version": "0.1.0",
  "environment": "development"
}
```

`environment` can be `development`, `test`, or `production`. This endpoint reports API availability; it does not validate Azure access, model availability, or event processing.

Interactive documentation: <http://127.0.0.1:8000/docs>.
OpenAPI schema: <http://127.0.0.1:8000/openapi.json>.

## Planned in Task 3/4

| Endpoint | Planned purpose | Current status |
| --- | --- | --- |
| `GET /matches/demo` | Match metadata and initial statistics. | Not implemented. |
| `GET /matches/demo/events` | Validated synthetic event list. | Not implemented. |
| `POST /events/process` | Run the selected event through the workflow. | Not implemented. |

Before implementing these endpoints, agree on event types, identifiers, timestamps, attacking direction, coordinate conventions, optional annotations, evidence references, audience/language fields, trace statuses, and error responses. Publish matching request/response examples and TypeScript types here.

Repeated selection and personalization must not count an event twice in match statistics. Missing tactical annotations must produce limited explanations rather than invented facts.
