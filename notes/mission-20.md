# Mission 20: Secure Remote Access

## Question

What does a key-authenticated localhost SSH session prove?

## Prediction

A temporary key will authenticate to a guest-loopback-only sshd. The session will retain the student's non-root authorization.

## Concept

SSH authenticates the server host key and the client user's key possession. After login, Unix credentials and policy still determine access.

## Defense

Use pinned local host keys, key-only authentication, no root login and a loopback listener. Delete the temporary private key after use.

## Verification

Require LOCAL_SSH_SUCCESS, non-root id output, loopback bind and sshd effective settings; capture authentication journal.

## Reflection

The isolated listener uses port 2222 so the managed Lima transport remains available. A localhost test does not prove a public network deployment is secure.

## Experiment

Run `python3 scripts/run_lab.py --missions 20` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q62.** The client verifies server host identity and the server verifies the user's credential (here an Ed25519 key). Encryption protects transport once negotiation succeeds.

**Q63.** The user's UID/GID, groups, DAC/ACLs, MAC and sudo policy determine allowed actions after authentication.

**Q64.** Use journalctl for the specific sshd unit; the accepted key and session events support login evidence. Other Ubuntu setups may also route logs to auth.log.

