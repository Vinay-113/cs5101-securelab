# Mission 07: Alice vs Bob

## Question

How does chmod change a second user's access?

## Prediction

Bob can read an Alice-owned 0644 file and is denied after it becomes 0600; Alice retains read access.

## Concept

DAC uses ownership, group membership and mode bits. The owner can change the policy, subject to filesystem and other controls.

## Defense

Restrict secret files to the smallest needed audience.

## Verification

Capture stat before/after and assert both denied Bob access and allowed Alice access.

## Reflection

File modes do not help if an ancestor directory or another copy exposes the same data.

## Experiment

Run `python3 scripts/run_lab.py --missions 7` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q19.** 0644 grants others read access; 0600 removes group and other permissions, leaving the owner read/write.

**Q20.** The file owner normally controls its discretionary mode and ACL, while privileged administrators may override ordinary DAC.

**Q21.** Removing Bob's unnecessary access illustrates least privilege. Owner, group and other are three distinct permission classes; each has r/w/x bits.

