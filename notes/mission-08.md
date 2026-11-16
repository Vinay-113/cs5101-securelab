# Mission 08: The Permission Maze

## Question

Can one named user receive a narrow exception?

## Prediction

A named Bob read ACL will permit reading without granting write or making the file world-readable.

## Concept

POSIX ACLs supplement owner/group/other with named entries. The ACL mask bounds effective permissions of named users and group-class entries.

## Defense

Grant u:bob:r, verify effective rights, then remove the temporary exception.

## Verification

Capture getfacl before and after, test read allowed/write denied, remove ACL and prove read denied again.

## Reflection

ls mode bits alone can obscure ACL intent: the group-class bits reflect the ACL mask, not simply the owning group entry.

## Experiment

Run `python3 scripts/run_lab.py --missions 8` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q22.** The named Bob entry grants read access subject to the mask; the owner remains Alice.

**Q23.** An ACL can identify Bob individually without granting the same permission to every member of the owning group or all other users.

**Q24.** Fine-grained least privilege is exercised. ACLs are still discretionary access controls and do not inherently stop an owner from changing policy.

