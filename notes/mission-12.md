# Mission 12: The Secret File

## Question

How do file and directory permissions combine?

## Prediction

Alice, as a securelab group member, can traverse secrets and read incident.txt. Bob cannot traverse it. Alice cannot overwrite the root-owned record.

## Concept

Directory execute controls traversal; read controls name listing; write plus execute controls entry changes. A file permission alone is insufficient.

## Defense

Use root:securelab, 0750 restricted directories and 0640 records; keep public data separate.

## Verification

Capture namei path components; test Alice read allowed, Bob read denied and Alice write denied.

## Reflection

World-readable content can still be hidden by a non-traversable directory, but relying on that alone is fragile when files are moved or copied.

## Experiment

Run `python3 scripts/run_lab.py --missions 12` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q35.** Each ancestor must allow traversal before a file can be opened; directory write/execute can also permit replacement or deletion even when the file itself is not writable.

**Q36.** Root and explicitly authorized securelab group members such as Alice; Bob has no business need.

**Q37.** If reachable through traversable directories, a world-readable incident file could disclose confidential data. Use restrictive file and directory permissions together.

