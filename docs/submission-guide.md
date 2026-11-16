# CS5101 submission guide

This repository contains the SECURELAB implementation, explanatory report, source code and original terminal evidence.

## Read first

1. [Final printable report](../output/pdf/securelab-report.pdf) - 43 pages covering the experiments, observations, explanations, diagrams, comparisons and practice security assessment.
2. [Editable report](../output/securelab-report.md) - the same report in Markdown.
3. [Complete submission archive](../output/securelab-submission.zip) - portable source, documentation, reports and evidence.
4. [Archive checksum](../output/securelab-submission.sha256) - SHA-256 digest of the ZIP.

The report does not include a student-details section, as requested.

## Implementation and evidence

- [C programs](../src/) and [mission runner](../missions/run.sh).
- [Bash/Python helpers](../scripts/) and [behavior tests](../tests/test_programs.py).
- [Mission notes](../notes/) and [design documentation](./).
- [Evidence manifest](../evidence/runs/20261116T101423Z/manifest.json), recording statuses, exit codes, UTC timestamps and attempts.
- [Evidence checksums](../evidence/runs/20261116T101423Z/SHA256SUMS).
- [Program-test results](../evidence/program-tests.log).
- [Provisioning and recovery evidence](../evidence/provisioning/).
- [Implementation validation notes](validation-notes.md).

The saved run verified all 22 mission scripts. Eight behavior tests passed. Earlier failed attempts are retained with the successful retests; observations are not replaced with predictions.

## Scope of the final assessment

Missions 1-21 implement the handout's core experiments. The environment is a headless Ubuntu 26.04 ARM64 VM on Apple Silicon using Lima/Apple virtualization, with 2 virtual CPUs, 4 GiB RAM and a 40 GiB sparse disk. This adaptation from the recommended Desktop/VirtualBox setup is documented in the report.

Mission 22 is a six-finding, controlled **practice** assessment. The instructor's separate Mission 22 document and prepared challenge VM were not supplied. This repository does not claim that the instructor-specific independent assessment has been completed. Personal reflection answers should be reviewed by the student.

## Reproduce and verify

See the [README](../README.md) for disposable-VM setup, execution, report generation and recovery. Do not run privileged lab scripts on a personal or production Linux machine.

Verify the saved evidence without running experiments:

```bash
python3 scripts/verify_delivery.py
```

Verify the archive from the output directory:

```bash
cd output
sha256sum -c securelab-submission.sha256
# macOS alternative: shasum -a 256 -c securelab-submission.sha256
```

Virtual disks, recovery disk copies, VM SSH private keys, downloaded tool binaries, caches and generated executables are local runtime files and are not submission artifacts. The repository includes the configuration and scripts needed to recreate the lab.
