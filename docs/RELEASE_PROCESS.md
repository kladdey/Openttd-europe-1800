# Release process

## Public repository policy

The main repository can remain public without hosting a bundled game distribution.

- Prefer a scenario-only archive plus documentation and installation scripts.
- Do **not** attach the earlier full portable ZIP or 59.4 MiB public candidate to a public release.
- Treat [LICENSING.md](LICENSING.md) as a working checklist; it is not a legal clearance certificate.
- Never assume making a release draft, deleting a release, or creating a private repository resolves third-party license obligations.

## Candidate versioning

- Current development candidate: **Phase 7H**, 617 towns / 542 initial industries, unchanged AXIS 0.6.0 with GS v7/schema 6; **READY WITH CAVEATS for controlled playtesting**. See [readiness](PHASE_7H_READINESS.md) and the [exact local asset manifest](research/phase7h_candidate_delivery.json). Older schemas are not silently migrated.
- Preserve V12/V13 and all Phase 6/7 candidates as historical checkpoints; they are not interchangeable campaign saves.
- A repository merge publishes source and documentation; it does not publish a playable binary bundle or certify multiplayer readiness. Local scenarios, profiles and third-party assets are not automatically uploaded.
- Identify the multiplayer `.scn` by exact filename and SHA-256; it may differ from V12/V13 source files.
- Use an explicit pre-release label until clean-machine and multiplayer tests pass.

## Build checklist

1. Choose and hash the intended scenario.
2. Inventory every proposed archive file.
3. Confirm rights for every file, especially original heightmap/scenario provenance.
4. Include only cleared assets; direct users to official downloads for third-party dependencies.
5. Verify archive extraction, Windows install path, NewGRF discovery and scenario loading.
6. Run host/client tests and document outcomes in [MULTIPLAYER.md](MULTIPLAYER.md).
7. Publish a release with installation instructions, dependencies, known issues and checksums.

## Release visibility

GitHub does not provide private published releases inside a public repository. Draft releases are restricted to users with sufficient repository access. Deleting a release does not necessarily delete its tag or any previously downloaded copies.

## Scope

This documentation does not create a new license for third-party files and does not assert that all repository contents are cleared for redistribution.
