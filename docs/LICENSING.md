# Licensing and distribution policy

This repository is a historical Europe scenario development project. **Do not assume a file is redistributable because it can be downloaded through OpenTTD's online content service.**

## Distribution rules

- The preferred public download contains **only project-authored scenario files, scripts, documentation and data for which redistribution rights have been confirmed**.
- Do not upload a portable OpenTTD installation, JGRPP binaries, OpenGFX2, third-party NewGRFs, DLLs or base sets as a public GitHub release until the exact version, license, copyright notices, source-code requirements and distribution rights have been checked.
- OpenTTD/JGRPP and many NewGRFs are GPL-licensed. GPL redistribution can be possible but requires compliance with the applicable license, notices, and corresponding-source obligations. Merely linking to upstream may not satisfy every distribution method.
- eGRVTS was identified as CC BY-NC-SA 3.0 in the earlier audit; attribution, noncommercial and share-alike conditions need review before bundling.
- UKRS2 1.05 and av8 2.21 were found in the uploaded archives with restrictive redistribution notices; **do not mirror these without permission**.
- Polish Train Set 3.0.3 has an unverified custom license; **do not mirror without permission or authoritative license evidence**.
- The exact rights to the source heightmap, any scenario-embedded content, third-party artwork, and project-authored materials also need review before declaring the *entire repository* or scenario package legally cleared. Do not add a blanket LICENSE covering third-party assets.

## NewGRFs used in the multiplayer build

| Component | Version | Earlier audit result | Public bundling decision |
| --- | --- | --- | --- |
| FIRS Industries 5 | 5.2.0 | GPL v2 | Hold until compliance package prepared |
| Sailing Ships community | 0.73 | GPL v2 | Hold until compliance package prepared |
| Polish Rolling Stock Pack | 0.19.11 | GPL v2 | Hold until compliance package prepared |
| Industrial Stations Renewal | 1.0.2 | GPL v2 | Hold until compliance package prepared |
| CHIPS Station Set 2 | 2.0.0 | GPL v2 | Hold until compliance package prepared |
| eGRVTS | v2.1 r240 | CC BY-NC-SA 3.0 | Hold until attribution/terms verified |
| UKRS2 | 1.05 | Restrictive archive notice | Do not bundle |
| av8 Aviators Aircraft Set | 2.21 | Restrictive archive notice | Do not bundle |
| Polish Train Set | 3.0.3 | Custom; rights not verified | Do not bundle |

This table is a **working audit**, not a legal opinion or a substitute for reviewing each exact upstream license. If any version differs, re-audit.

## Safer installation model

Distribute the project scenario and a text list of required add-ons. Players install [JGRPP](https://github.com/JGRennison/OpenTTD-patches/releases) and download required NewGRFs from the original publishers or the in-game **Online Content** service, using **Find missing content online** where available. If an exact version cannot be found, do not substitute a different version without testing.

## Release checklist

1. Verify ownership and provenance of the scenario, heightmap, and every asset in the proposed archive.
2. Generate a file inventory and SHA-256 manifest.
3. Review each included file's applicable license and source/attribution obligations.
4. Exclude assets with unverified or restrictive redistribution permissions.
5. Test a clean Windows install, map loading and multiplayer with matching JGRPP/NewGRF versions.
6. Mark untested builds as experimental; never label a package 'license cleared' without evidence.
7. Do not assume a draft/private GitHub release cures copyright restrictions.

See [INSTALLATION.md](INSTALLATION.md) and [MULTIPLAYER.md](MULTIPLAYER.md).
