# Stable receipt source paths: RC-RECEIPT-PATH-01

Review finding 4384864734 is reproduced at accepted parent `f0e671a`.
Thirty cases fail after a working-directory change; ten absolute-path controls
pass. Failures include fresh-process verification, downstream consumption, and
reopening genuine artifact/evidence drift or absence.

The guarded reader checked relative paths against the issuing cwd but the receipt
stored their relative spelling without that context. Its metadata hash remained
valid while later reads resolved a different location. No source bytes needed to
change to produce the failure.

The three-line repair is in the sole admitted caller of `record`, in
`lane_submission.py`: after all existing path checks and snapshot preservation,
copy candidate/evidence paths to absolute spellings. Then take the final trusted
clock and recheck authority before recording. `Path.absolute` does not resolve
symlinks. Forbidden parent and symlink inputs still fail before conversion. The
evaluator sees the original request spelling; caller models remain immutable.

The supervisor inspected that source order, the unchanged reader and receipt sink,
required assertions, retained failures, source identities and raw observations.
Fifty new pytest cases cover absolute/relative artifact and evidence combinations,
SEALED/DENIED receipts, fresh processes, consumption, drift recovery, six scope
denials, and exclusive grant/evidence expiry during either path conversion.
The isolated suite passes 465 cases with all prior 415 IDs retained; static gates
and the 27 existing verification unittest cases pass. The latter entrypoint does
not independently execute these new pytest cases.

Deleting binding reproduces the original thirty failures with ten controls still
passing. Moving binding after final admission fails all four new expiry cases.
The six-arm causal experiment records intact, deletion, restoration, sham and
alternate-context on/off. Restoring issuer cwd compensates a legacy-format read,
but the relative receipt still violates the new persistence contract. That arm
does not gain promotion or authority.

Only newly issued receipts acquire absolute paths. Historical relative receipts
are not rewritten and their original cwd cannot be inferred from a content hash.
Their original context must be established under the owning recovery process, or
they remain blocked. Absolute spellings are not filesystem immutability, a sandbox,
or protection from arbitrary concurrent filesystem/global-cwd mutation. Process
reconstruction here is not process-kill or power-loss durability qualification.

The custody-index change is separately accepted by comment 6433215377 at exact
parent `f0e671acd513be3bfdb72e546d422839fdfbbf2e`. This new path repair has its own
review packet in `evidence/receipt_path_case.json`; prior acceptance does not
automatically accept it. Requirements and all full-work-package qualifications
remain unchanged. Integration, merge and deployment remain unauthorized.
