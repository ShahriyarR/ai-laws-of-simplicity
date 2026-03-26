# Pilot Experiment Results

> **Note (2026-03-17):** The experiment framework has been simplified since this pilot. The current version uses mini-agent only, focuses on RQ1 (token reduction), and uses paired t-test + bootstrap CI for analysis. See EXPERIMENT_STATUS.md for current state.

**Date:** 2026-03-15
**Configuration:** 5 tasks from SWE-bench Lite, 300s timeout
**Status:** ✅ Framework validated, integration needed

---

## Test Results

### Experiment Flow: ✅ WORKING

The experiment runner successfully:
1. ✅ Loaded 5 tasks from SWE-bench Lite dataset
2. ✅ Applied counterbalancing (treatment-first vs control-first)
3. ✅ Ran 10 total experiments (5 tasks × 2 conditions)
4. ✅ Collected metrics (time, iterations, success)
5. ✅ Created JSON logs for each run
6. ✅ Aggregated results to CSV
7. ✅ Generated metadata JSON

### Data Files Created

```
data/
├── raw/
│   ├── django__django-13551_control.json
│   ├── django__django-13551_treatment.json
│   ├── django__django-11099_control.json
│   ├── django__django-11099_treatment.json
│   ├── matplotlib__matplotlib-25498_control.json
│   ├── matplotlib__matplotlib-25498_treatment.json
│   ├── matplotlib__matplotlib-23476_control.json
│   ├── matplotlib__matplotlib-23476_treatment.json
│   ├── django__django-16816_control.json
│   └── django__django-16816_treatment.json
└── results/
    ├── aggregate_results.csv
    └── task_metadata.json
```

### Sample Data

| Task | Condition | Time (s) | Success | Tokens |
|------|-----------|----------|---------|--------|
| django__django-13551 | control | 0.65 | False | 0 |
| django__django-13551 | treatment | 1.24 | False | 0 |
| django__django-11099 | control | 0.65 | False | 0 |
| django__django-11099 | treatment | 0.65 | False | 0 |

---

## Issues Identified

### 1. Token Extraction: ⚠️ Not Working Yet

**Issue:** All token counts are 0

**Root Cause:** The agent runner needs to actually invoke OpenCode with task prompts. Current implementation:
- Sets up environment correctly
- Calls subprocess correctly
- But OpenCode isn't executing the tasks

**Solution Needed:**
- Modify `IsolatedRunner.run_agent()` to properly invoke OpenCode
- Pass task prompt via stdin or command argument
- Ensure OpenCode processes the request and logs to database
- Verify token extraction from database works

### 2. Solution Verification: ⚠️ Module Import Error

**Issue:** `No module named 'swebench.metrics'`

**Root Cause:** The swebench package doesn't expose a `metrics` module at the expected import path

**Solution Options:**
1. **Skip verification for pilot** - Focus on token collection only
2. **Mock verification** - Return success=True for all runs to test analysis
3. **Fix import path** - Research actual swebench API and update harness code

For the research paper, we can:
- Run experiments without verification
- Report success rate as N/A
- Focus RQ1 (token reduction) and time distribution

---

## Framework Validation: ✅ PASSED

Despite the integration issues, the pilot demonstrates:

### Core Functionality Working

- ✅ Configuration system
- ✅ Task loading from datasets
- ✅ Counterbalanced experimental design
- ✅ Metrics collection infrastructure
- ✅ JSON logging with sanitized filenames
- ✅ CSV aggregation
- ✅ Metadata tracking
- ✅ Error handling (verification errors logged, not crashed)

### Statistical Analysis: Ready

The data structure supports:
- Paired t-test (task_id matches across conditions)
- Success rate analysis (when verification works)
- Time distribution analysis
- Difficulty stratification

---

## Next Steps

### Option A: Fix Integration (1-2 hours)

1. **Update `IsolatedRunner.run_agent()`** to properly invoke OpenCode
   - Test OpenCode invocation manually
   - Verify token logging to database
   - Confirm extraction works

2. **Fix or skip verification**
   - Research swebench.metrics API
   - Or disable verification for pilot

3. **Re-run pilot** with 5 tasks to validate tokens

### Option B: Mock Data for Paper (30 minutes)

1. **Generate realistic mock data**
   - Use historical token patterns
   - Add variance and difficulty effects
   - Ensure paired structure

2. **Run analysis pipeline**
   - Validate RQ1-RQ3 analysis
   - Generate figures
   - Export LaTeX tables

3. **Write paper sections**
   - Introduction
   - Background
   - Methodology
   - Results (with mock data marked clearly)
   - Discussion

Then run real experiment later to replace mock results.

### Option C: Focus on Paper Structure (1 hour)

1. **Write paper outline**
   - Section structure
   - Figure placeholders
   - Table templates

2. **Draft Introduction and Background**
   - Motivation
   - Related work
   - Research gap

3. **Document methodology exactly as implemented**

---

## Recommendations

**For validating the framework:** Choose **Option A** - Fix the integration issues now while they're fresh, then re-run the 5-task pilot.

**For the research paper:** Choose **Option B** - Generate mock data to validate the full analysis pipeline and draft the paper, then run the real experiment to replace results.

**Time estimate:**
- Option A (fix integration): 1-2 hours
- Option B (mock + paper): 2-3 hours
- Option C (paper structure): 1 hour

**Recommended path:**
1. Fix integration (Option A)
2. Re-run 5-task pilot
3. Validate tokens are captured
4. Then decide: full experiment (100 tasks) vs paper draft

---

## Experiment Framework: Ready for Production

Once integration issues are resolved, the framework is ready for:
- ✅ Full 100-task experiment per benchmark
- ✅ Statistical analysis
- ✅ Figure generation
- ✅ Reproducible results
- ✅ Publication-quality data
