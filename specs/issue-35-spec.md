# Technical Specification — Issue #35

## 1. Issue Overview

| Field       | Value                                              |
|-------------|----------------------------------------------------|
| Title       | SampleWaitPipeline.json having invalid timeZone    |
| Description | The `timeZone` field is set to `UTC` but should be `India Standard Time` (IST) |
| Labels      | None                                               |
| Priority    | Low                                                |
| State       | Closed                                             |

## 2. Problem Analysis

The `SampleWaitPipeline.json` file defines an Azure Data Factory `ScheduleTrigger` named `Daily11AMUTCTrigger`. Its `recurrence.timeZone` field was set to `"UTC"`, but the intended operational timezone for the pipeline schedule is India Standard Time (IST, UTC+5:30).

This causes the trigger to fire at 02:00 UTC instead of 02:00 IST, a 5h30m discrepancy, resulting in the pipeline running at the wrong local time.

Root cause: The `timeZone` value in the `typeProperties.recurrence` block was set to `"UTC"` rather than the Windows timezone identifier `"India Standard Time"`.

## 3. Proposed Solution

A single-field patch to `SampleWaitPipeline.json`:

- Change `"timeZone": "UTC"` → `"timeZone": "India Standard Time"`

No structural or architectural changes are needed. The fix is entirely confined to one JSON key-value pair.

## 4. Step-by-Step Implementation

1. **Update timeZone field** — In `SampleWaitPipeline.json` at `properties.typeProperties.recurrence.timeZone`, replace `"UTC"` with `"India Standard Time"`.
2. **Commit the change** — Commit with a clear message referencing issue #35.
3. **Open a PR** — Submit for review and merge into `main`.

## 5. Verification Strategy

### Manual Checks

- Open `SampleWaitPipeline.json` and confirm `"timeZone": "India Standard Time"` is present.
- Validate the JSON is well-formed (e.g., `cat SampleWaitPipeline.json | python -m json.tool`).
- Deploy to Azure Data Factory and confirm the trigger's timezone shows as IST in the ADF portal.

### Integration Tests

- Trigger a manual run and verify the next scheduled execution time aligns with IST (UTC+5:30).

## 6. Files to Modify

| File Path                  | Nature of Change                                         |
|----------------------------|----------------------------------------------------------|
| `SampleWaitPipeline.json`  | Change `timeZone` from `"UTC"` to `"India Standard Time"` |

## 7. New Files to Create

None.

## 8. Existing Utilities to Leverage

| Utility            | Benefit                                              |
|--------------------|------------------------------------------------------|
| `gh pr create`     | Standard PR workflow already in use on this repo     |

## 9. Acceptance Criteria

- `SampleWaitPipeline.json` contains `"timeZone": "India Standard Time"`
- JSON file remains valid and well-formed
- No other fields in the file are modified
- Change is merged to `main`

## 10. Out of Scope

- Changes to any other pipeline JSON files
- Renaming the trigger (`Daily11AMUTCTrigger` name is not part of this issue)
- Modifying `startTime` or `frequency` fields
