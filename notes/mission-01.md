# Mission 01: Who Are You?

## Question

How do users and processes carry identity?

## Prediction

An ordinary program will inherit the invoking user's real and effective IDs. Running as Alice will change those credentials.

## Concept

Real IDs identify the originating user; effective IDs normally drive discretionary access checks. The filesystem UID can matter for Linux file checks. Authentication establishes identity; authorization evaluates a requested operation.

## Defense

Use separate unprivileged accounts and grant only required access.

## Verification

Compare id with identity.c under the student and Alice accounts.

## Reflection

A compromised process can exercise its credentials; shared accounts weaken attribution.

## Experiment

Run `python3 scripts/run_lab.py --missions 1` inside the prepared guest. See `missions/run.sh` for exact commands; missions 18 and 22 use the documented prerequisites.

## Observation

The generated report links actual mission logs and reports their verification status. Predictions above are not measurements.

## Handout questions

**Q1.** UID records the real user identity; EUID is the effective identity used for many access decisions. They can differ with setuid or deliberate credential changes. No setuid program is created here.

**Q2.** Authentication proves an identity (for example, possession of an SSH key). Authorization decides whether that identity may read a file or perform another action.

**Q3.** Unauthorized reading violates confidentiality. Network listeners and parsers handling untrusted files are two workstation attack surfaces.

