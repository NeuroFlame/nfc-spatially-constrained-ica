# Migration to computation-nvflare-boilerplate

This computation was migrated from the old, hand-written NVFlare
`Controller`/`Executor`/`Aggregator` architecture to the current
[`computation-nvflare-boilerplate`](https://github.com/NeuroFlame/computation-nvflare-boilerplate)
contract, where authors write only `app/code/computation/` and the
boilerplate's `framework/`/`runtime/` own all NVFlare integration. See
[computation_development.md's migration
guide](https://github.com/NeuroFlame/computation-nvflare-boilerplate/blob/main/docs/computation_development/migrating_computations.md)
for the general migration process, and
[nfc-label-noise-filtering](https://github.com/NeuroFlame/nfc-label-noise-filtering)
and
[nfc-multi-round-regression-freesurfer](https://github.com/NeuroFlame/nfc-multi-round-regression-freesurfer)
for sibling computations migrated the same way.

## Why a single local/remote pair, no `site_output_step`

Spatially constrained ICA is (and always was) a purely local computation:
each site runs GIFT independently and there is nothing to combine centrally
— the old `ScicaAggregator.aggregate()` was already a no-op. The boilerplate
still requires every `local_step` to be immediately followed by its
`remote_step`, so `app/code/computation/spec.py` pairs
`run_site_scica`/`load_site_inputs` with a `remote_step` that only logs which
sites finished (`remote_math.acknowledge_site_results`) — the same no-op the
old aggregator performed, just with real logging.

There's no `site_output_step` either. GIFT/nipype writes dozens of
heterogeneous files directly to disk during the run itself (`.mat`, `.nii`,
an HTML report + image folder, logs) — not values that fit returning through
a step payload. `run_site_scica` (`app/code/computation/local_math.py`)
requests the injected `output_dir` and writes there directly, which the
framework documents as the intended escape hatch for this case. A
`stepped_workflow` may legally end on a `remote_step`, so nothing further
was needed.

## `site_id_name_map` provisioning patch superseded, not ported

The commit immediately before this migration
(`58cafe1`, "Expose human-readable site names through provision input and
aggregator") hand-rolled a `users: [{id,name}]` → `site_id_name_map`
provisioning patch, plus aggregator-side lookup logic. That entire pattern is
now a **built-in feature** of the boilerplate's own provisioning code
(`system/provision/code`, migration-managed) and the framework's automatic
site-ID→display-name substitution on `site_results` dict keys — see
`remote_math.acknowledge_site_results`'s `Dict[str, SiteRunSummary]`
parameter, which already receives `site1`/`site2`/`site3` as keys with no
extra code. The hand-rolled version was dropped rather than ported forward.

## Dockerfiles: MATLAB Runtime + GIFT re-applied on `python:3.11-bookworm`

`Dockerfile-dev`/`Dockerfile-prod` are boilerplate-managed and get
wholesale-replaced by `migrate_computation.py`, so they're the only two
managed paths that still differ from a `--check` run — intentionally. The
generic template was regenerated first, then the MATLAB Runtime install,
GIFT toolbox fetch, `gift` repo clone, and environment variables were
manually re-applied on top of it, updating the one Python-version-specific
line (the vendored GIFT nipype interface's install path,
`.../site-packages/python3.8/...` → `.../python3.11/...`) for the
boilerplate's Python 3.8 → 3.11 bump. This was the highest-risk step in the
whole migration and is the one most directly verified below.

## Other intentional differences

- `nvflare` bumped 2.4.0 → 2.8.0, base Python image 3.8 → 3.11, per the
  boilerplate's current pins.
- The old `validate_run_input.py` returned `False` and wrote a bespoke
  `validation_log.txt` on bad input. `app/code/computation/inputs.py` now
  raises ordinary `ValueError`s instead, matching the framework's terminal-
  error contract (which already records the full exception/traceback in the
  computation log and an internal error marker) rather than duplicating that
  bookkeeping.
- Dropped the superseded `app/code/{controller,aggregator,executor,utils}`
  and root `debug.py` (replaced by the boilerplate's `debugger.py`, which is
  functionally identical — both wrap NVFlare's `SimulatorRunner`).
- `nipype` remains unpinned in `requirements.txt`, as it was before this
  migration (it's a target-only, computation-specific dependency the
  migration script preserves as-is). It currently resolves to `1.11.0`. This
  is a pre-existing risk, not one introduced here — worth pinning once a
  known-good version is confirmed.

## Verification performed

- **Numeric parity**: built Docker images for both the pre-migration
  (`master`) and migrated implementations, and ran each through the real
  GIFT/MATLAB pipeline via the NVFlare simulator against
  `test_data_five_subjects` (3 sites, 5 subjects each, default parameters).
  - Recursive per-site output file trees are identical, except the migrated
    version adds `<site>.log` (the framework's new structured per-site
    logging; nothing was removed or renamed).
  - `index.html` is **byte-identical** for all 3 sites, including the
    rewritten `<img src="gica_cmd_gica_results/*.png">` paths.
  - Every `.mat`/`.nii` output file matches in both name and byte size
    across all 3 sites.
  - `aggregator.remote.log` on the migrated side confirms `site_results` was
    correctly keyed by display name (`site1`/`site2`/`site3`), matching the
    intent of the superseded provisioning patch above.
- **`make lint-author` / `format-author` / `compile` / `test`**: all pass.
  (Repo-wide `make lint` also flags pre-existing, unrelated issues in
  `docs/non_federated_regression.py` — out of scope for this migration, not
  touched.)
- **Image validation**: `python scripts/publish_computation_image.py
  --no-push` builds `Dockerfile-prod` and confirms the image carries all
  required OCI/NeuroFLAME labels.
- **`migrate_computation.py --check`**: reports only `Dockerfile-dev` and
  `Dockerfile-prod` differing from the checked-out boilerplate release —
  expected, since those two carry the MATLAB Runtime/GIFT install this
  computation needs on top of the generic template.

**Not directly measured**: an actual local NeuroFLAME platform stack
(central API + edge sites), as opposed to the NVFlare simulator directly —
only the simulator flow was exercised.
