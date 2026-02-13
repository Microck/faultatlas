# Indagine Demo Sample Output

This fixture is used by `demo/run_demo.py --mode mock`.

```json
{
  "mode": "mock",
  "subject": "booking",
  "store": "memory",
  "scenario_input": {
    "request": "Book a flight from NYC to LAX on 15/02/2026",
    "date": "15/02/2026",
    "from": "NYC",
    "to": "LAX"
  },
  "failure_event": {
    "failure_id": "booking-20260211120000000000",
    "subject": "booking",
    "failure_type": "validation_error",
    "timestamp": "2026-02-11T12:00:00Z",
    "trace_id": null,
    "error": "'15/02/2026' does not match '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'",
    "metadata": {
      "status": "failed",
      "error": {
        "tool": "search_flights",
        "code": "schema_validation_failed",
        "message": "'15/02/2026' does not match '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'",
        "details": {
          "path": "date"
        }
      }
    }
  },
  "findings": {
    "findings": {
      "trace_analyzer": [
        {
          "failure_step": 1,
          "total_steps": 1,
          "failure_location": "step 1 (subject_result)",
          "error": "'15/02/2026' does not match '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'",
          "reasoning_chain": [
            "subject_result: call search_flights with args {\"date\": \"15/02/2026\", \"from\": \"NYC\", \"to\": \"LAX\"}",
            "subject_result: input {\"date\": \"15/02/2026\", \"from\": \"NYC\", \"request\": \"Book a flight from NYC to LAX on 15/02/2026\", \"to\": \"LAX\"}",
            "subject_result: error '15/02/2026' does not match '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'"
          ]
        }
      ],
      "tool_analyzer": [
        {
          "tool": "search_flights",
          "issue": "tool_misuse_detected",
          "expected": null,
          "actual": {
            "tool_calls": [
              {
                "step": 1,
                "step_name": "subject_result",
                "tool_name": "search_flights",
                "args": {
                  "date": "15/02/2026",
                  "from": "NYC",
                  "to": "LAX"
                }
              }
            ],
            "schema_mismatches": [
              {
                "step": 1,
                "step_name": "subject_result",
                "tool": "search_flights",
                "code": "schema_validation_failed",
                "message": "'15/02/2026' does not match '^\\\\d{4}-\\\\d{2}-\\\\d{2}$'",
                "path": "date",
                "details": null
              }
            ],
            "wrong_tool_selection": false,
            "wrong_tool_reason": null
          }
        }
      ]
    }
  },
  "diagnosis": {
    "root_cause": "TOOL_MISUSE",
    "sub_type": "schema_mismatch",
    "confidence": 0.9,
    "explanation": "Tool invocation parameters violate the registered tool schema.",
    "affected_subjects": [
      "search"
    ],
    "similar_past_failure_ids": [],
    "similar_past_failures": 0
  },
  "fixes": [
    {
      "fix_type": "TOOL_CONFIG_FIX",
      "title": "Normalize booking dates before tool validation",
      "rationale": "Add a pre-validation transformation step so date inputs are converted to YYYY-MM-DD before calling the flight search tool.",
      "changes": [
        {
          "file": "src/subjects/booking_agent.py",
          "change_type": "insert_pre_validation",
          "before": "    active_registry.validate_payload(payload[\"tool_calls\"][0])",
          "after": "    payload[\"tool_calls\"][0][\"args\"] = normalize_date_args(payload[\"tool_calls\"][0][\"args\"])\\n    active_registry.validate_payload(payload[\"tool_calls\"][0])",
          "diff": "--- a/src/subjects/booking_agent.py\\n+++ b/src/subjects/booking_agent.py\\n@@ -1 +1,2 @@\\n+    payload[\"tool_calls\"][0][\"args\"] = normalize_date_args(payload[\"tool_calls\"][0][\"args\"])\\n     active_registry.validate_payload(payload[\"tool_calls\"][0])\\n"
        }
      ]
    }
  ]
}
```
