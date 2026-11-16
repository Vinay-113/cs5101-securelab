# Mission 13: Can We Trust the File?

## Question

Can a checksum detect modification?

## Prediction

The baseline check will pass, then fail after appending text.

## Concept

SHA-256 fingerprints bytes. Comparison with a trusted baseline detects drift; an unauthenticated checksum cannot identify the author or resist replacement of both data and baseline.

## Defense

Protect the baseline separately; use signatures or HMAC when authenticity is needed.

## Verification

Record both hashes and assert sha256sum -c changes from success to failure.

## Reflection

Hashing is not secure deletion. Unlink removes a name, and overwriting is unreliable on SSDs, snapshots and copy-on-write storage. Encryption-key management and platform-appropriate sanitization matter.

## Experiment

Run `python3 scripts/run_lab.py --missions 13` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q38.** Changing file bytes produces a different SHA-256 digest with overwhelming probability; consult the captured original and modified digests.

**Q39.** No. Anyone can hash bytes. A hash alone neither proves authorship nor protects an attacker-writable baseline.

**Q40.** Integrity asks whether bytes match a trusted reference; authenticity asks whether their claimed origin is trustworthy.

