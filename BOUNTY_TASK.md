# Bounty Objective: Reward card fields: class and for (2.0.0)
Target: lvisintini/imperial-assault-data Issue #51
URL: https://github.com/lvisintini/imperial-assault-data/issues/51

## Issue Description
Agreed design for 2.0.0 (built on `release/2.0.0`). Two new fields on `reward-cards`:
- **`class`**: `Regular`, `Boon` or `Bane`. Required from the start. Boon or Bane for the Return to Hoth cards (reward-cards 60–67), Regular for everything else.
- **`for`**: `Imperial player` or `Rebel players`. Added **nullable at first**, with every reward starting as null.
  - Values come from the wiki's Rebel/Imperial reward lists where products split them (e.g. Twin Shadows). The rest are pre-filled by name and confirmed by the maintainer through `ia propose` / `ia enter`.
  - The schema is tightened to required in the same PR that fills in the last value.

The 2018 pipeline's `empire` field never reached the data, so history doesn't help. Heroic and Legendary (Core Set) are still missing everywhere (#21).

Part of milestone 2.0.0.

🤖 Generated with [Claude Code](https://claude.com/claude-code)


## Instructions for Kuro (Autonomous Solver):
1. Use skills: `systematic-debugging` and `code-review-and-quality`.
2. Inspect the repository structure, locate relevant files, and understand the bug/feature.
3. Apply the minimal, robust fix or implementation.
4. Run any existing test suites or linters in the workspace.
5. Ensure the fix adheres to the project's existing code style.
6. When done, output a summary of files modified and verification results.
