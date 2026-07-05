# Technical Specification — Issue #31

## 1. Issue Overview

| Field       | Value                                              |
|-------------|----------------------------------------------------|
| Title       | SampleWaitPipeline.json having invalid timeZone    |
| Description | The `timeZone` field in `SampleWaitPipeline.json` was set to `UTC` instead of the required `India Standard Time` (IST). |
| Labels      | None                                               |
| State       | Closed                                             |
| Priority    | Low                                                |

## 2. Problem Analysis

The `SampleWaitPipeline.json` file defines an Azure Data Factory `ScheduleTrigger`.
Its `recurrence.timeZone` property was set to `"UTC"` when it should be `"India Standard Time"`.

Root cause: the value was manually set (or reset) to `"UTC"` in a prior commit.
No code logic generates this value — it is a static configuration field.
The correct value, per the issue reporter, is `"India Standard Time"` (the Windows timezone ID recognised by Azure Data Factory for IST, UTC+5:30).

Current state of `SampleWaitPipeline.json` (post-fix):
```json
"timeZone": "India Standard Time"
```
The issue is already resolved and closed. This spec documents the fix for future reference.

## 3. Proposed Solution

Single-field patch: ensure `recurrence.timeZone` in `SampleWaitPipeline.json`
is set to `"India Standard Time"` and kept that way.

No architectural changes required. The fix is a one-line JSON value change.

**Trade-off:** Azure Data Factory uses Windows timezone IDs (e.g. `"India Standard Time"`),
not IANA IDs (e.g. `"Asia/Kolkata"`). Using the wrong format causes ADF to reject the trigger or
silently fall back to UTC — so the exact string `"India Standard Time"` must be preserved.

## 4. Step-by-Step Implementation

1. **Verify current value** — open `SampleWaitPipeline.json` and confirm `timeZone` field value.
2. **Update if needed** — change `"timeZone": "UTC"` to `"timeZone": "India Standard Time"`.
3. **Commit** — commit with a message referencing the issue (e.g. `fix: set timeZone to India Standard Time in SampleWaitPipeline.json (#31)`).
4. **Deploy / publish** — re-publish the trigger in Azure Data Factory to apply the change.

## 5. Verification Strategy

### Unit Tests
- Parse `SampleWaitPipeline.json` → assert `properties.typeProperties.recurrence.timeZone === "India Standard Time"`.

### Integration Tests
- Deploy trigger to ADF dev environment → confirm trigger schedule shows IST (UTC+5:30) in ADF Studio.

### Manual Checks
- Open `SampleWaitPipeline.json` in editor → confirm `timeZone` value is `"India Standard Time"`.
- In ADF Studio, inspect the trigger's recurrence timezone → it should display as `(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi`.

## 6. Files to Modify

| File Path                   | Nature of Change                                     |
|-----------------------------|------------------------------------------------------|
| `SampleWaitPipeline.json`   | Change `timeZone` from `"UTC"` to `"India Standard Time"` |

## 7. New Files to Create

None.

## 8. Existing Utilities to Leverage

| Utility / Resource              | Benefit                                                   |
|---------------------------------|-----------------------------------------------------------|
| Azure Data Factory timezone IDs | Authoritative list of valid Windows TZ IDs accepted by ADF |
| Git history (`git log`)         | Tracks prior back-and-forth changes to this field         |

## 9. Acceptance Criteria

- `SampleWaitPipeline.json` contains `"timeZone": "India Standard Time"`.
- The ADF trigger runs on IST schedule without UTC offset errors.
- No other JSON fields in the file are modified.

## 10. Out of Scope

- Changes to `Monthly_SampleWaitPipeline.json` or `Weekly_SampleWaitPipeline.json` (unless separately reported).
- Switching to IANA timezone IDs — ADF requires Windows timezone ID format.
- Automating timezone validation across all pipeline JSON files.
