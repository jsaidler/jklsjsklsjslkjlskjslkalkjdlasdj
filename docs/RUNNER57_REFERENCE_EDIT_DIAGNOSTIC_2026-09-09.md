# Runner57 — FLUX.2 Klein reference-edit diagnostic

Status date: **2026-09-09**

Status: **HARNESS/EXECUTOR FAILURE NOT YET CLASSIFIED; MODEL EDIT CAPABILITY REMAINS PENDING**

## Context

Runner56 already proved the isolated `Z:\AI\Flux2Klein` runtime, exact model hashes and reference-free T2I inference on the RTX 3060 12 GB workstation.

Runner57 is the next gate for `single_reference_edit` and `multi_reference_edit` through the generic Asset Studio adapter.

## Observed local attempts

The isolated ComfyUI runtime starts successfully on port 8192 and reports the expected pinned package versions. The Klein diffusion model, Qwen3-4B text encoder, FLUX.2 VAE and pinned ComfyUI commit all pass verification.

The Python executor exits with code 1. Earlier Windows PowerShell 5.x invocation converted native Python stderr into a terminating `NativeCommandError`, truncating the traceback. A subsequent attempt still did not expose the useful executor exception in the pasted terminal tail; the visible ComfyUI log showed only normal startup.

No evidence currently supports classifying this as a FLUX.2 Klein model failure, OOM or CUDA failure.

## Diagnostic correction

Runner57 now launches the Python executor with `Start-Process` and separate file redirects for stdout and stderr. This removes PowerShell native-stderr interpretation entirely.

Files:

- `Z:\AI\Flux2Klein\edit_gate\flux2_klein_edit_gate_python_stdout.log`
- `Z:\AI\Flux2Klein\edit_gate\flux2_klein_edit_gate_python_stderr.log`
- `Z:\AI\Flux2Klein\edit_gate\flux2_klein_edit_gate_executor.log`

The runner prints Python stdout in full, Python stderr when non-empty, the Python exit code, and the ComfyUI stderr tail before failing.

The executor itself imports project adapter modules inside `main()` and has a top-level exception handler that prints `RUNNER57-PYTHON-FAIL: <type>: <message>` plus the full traceback to stdout.

## Capability status

Keep router status:

`active_static_t2i_proven_edit_pending`

Active:

- `text_to_image`
- `interactive_concept`

Pending until Runner57 technical + visual PASS:

- `single_reference_edit`
- `multi_reference_edit`
- `interactive_variant`

## Next action

Re-run the corrected Runner57 after `git pull --ff-only origin main`. No model downloads are required. Use the newly deterministic Python stdout/stderr block to classify and fix the underlying executor/graph failure before changing model family or checkpoint.
