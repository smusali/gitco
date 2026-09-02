# GitCo — Unified Technical, Product, Security & Strategic Assessment

**Subject:** `smusali/gitco` — *"A simple CLI tool for intelligent OSS fork management and contribution discovery."*
**Mirror referenced by package metadata:** `41technologies/gitco`
**Assessed commit:** `d71824a` (`fix: make fixes`) — tip of `main`
**Declared version in source:** `0.1.0`
**Declared status in metadata:** `Development Status :: 4 - Beta`
**Assessment date:** 2026-09-02
**Method:** full source read; AST import-graph resolution against real symbol tables; AST call-graph validation against real method sets; dependency-usage audit; `ruff --select ALL` statistics; live execution of the complete command tree inside a clean virtualenv against a real configuration after hand-repairing every import defect; git-history bisection and commit forensics; workflow and packaging analysis; PyPI namespace verification; competitive and ecosystem research.
**Stance:** adversarial, evidence-first. Every factual claim below was reproduced against the working tree at `d71824a`.

---

# PART 0 — MEASURED STATE OF THE PROJECT

## 0.1 Repository Vital Statistics

| Metric | Measured value |
|---|---|
| Python source files | 35 |
| Total source lines | 19,565 |
| Documentation lines (`docs/` + root Markdown) | ~5,252 across 17 files |
| Total commits on `main` | 80 |
| Git tags | **0** |
| GitHub releases | **0** |
| Published packages under this project's control | **0** |
| Stars / Forks / Watchers | **0 / 0 / 0** |
| Open pull requests | 15 (predominantly stale Dependabot) |
| Test files | **0** |
| Test lines | **0** |
| CI workflows that execute the package | **0** |
| CI workflows that run a test runner | **0** |
| Declared runtime dependencies | 11 (2 never imported) |
| `except Exception` occurrences | 199 |
| `subprocess.run` call sites | 7 (**0** with `check=True`) |
| `TODO` / `FIXME` / `XXX` / `HACK` comments | **0** |
| `# type: ignore` comments | 17 (all blanket, no error codes) |
| `global` statements | 12 |
| Bare `print()` calls bypassing the Rich console | 6 |
| `py.typed` marker (PEP 561) | **absent** — yet `Typing :: Typed` is claimed |
| `mypy` references anywhere in the repo | **0** |
| `.secrets.baseline` (referenced by two workflows) | **absent** |
| Total `ruff --select ALL` violations in `src/` | **2,874** |
| Largest single file | `src/gitco/libs/git_ops.py` — 3,178 lines |
| Longest single function | `src/gitco/cli/contributions.py:stats` — 164 lines |
| Time `main` has been unimportable | ~11 months (2025-09-29 → 2026-09-02) |
| Time the console entry point has been unreachable | ~12.5 months (2025-08-15 → 2026-09-02) |

## 0.2 Source Tree Inventory (measured line counts)

```
src/gitco/
├── __init__.py                       11    version/author/license constants only
├── cli.py                           138    ⚠️ UNREACHABLE — defines `main`, shadowed by cli/
├── cli/
│   ├── __init__.py                   21    imports 6 command modules; defines NO `main`
│   ├── core.py                      965    init, sync, analyze, discover, status, activity,
│   │                                       logs, performance, completion, validate-repo, help, version
│   ├── config.py                    329    config edit/export/import/show/validate
│   ├── contributions.py             581    stats/recommendations/trending/sync-history/export
│   ├── github.py                    519    connection-status, get-repo, get-issues(-multi), rate-limit-status
│   ├── backup.py                    327    create/list/restore/delete/validate/cleanup
│   └── upstream.py                  429    add/remove/update/validate/fetch/merge
├── libs/
│   ├── __init__.py                   54    ⚠️ eager re-exports incl. 4 nonexistent symbols
│   ├── git_ops.py                  3,178   GitAuthInfo, GitAuthDetector, BatchResult,
│   │                                       BatchPerformanceMetrics, BatchProcessor,
│   │                                       GitRepository (873–2167), GitRepositoryManager (2168–3178)
│   ├── github_client.py            1,275   SSHGitHubResponse, SSHGitHubClient, GitHubClient
│   ├── analyzer.py                 1,183   BaseAnalyzer, OpenAIAnalyzer, ChangeAnalyzer, ChangeAnalysis
│   ├── contribution_tracker.py     1,034   Contribution, ContributionStats, ContributionTracker
│   ├── config.py                     968   Repository, Settings, Config, ConfigValidator, ConfigManager
│   ├── discovery.py                  884   SkillMatch, IssueRecommendation, SkillMatcher, IssueDiscovery
│   ├── detector.py                   742   SecurityUpdate, Deprecation, BreakingChange, BaseDetector,
│   │                                       SecurityDeprecationDetector, BreakingChangeDetector
│   ├── backup.py                     709   BackupMetadata, BackupManager
│   ├── health_metrics.py             626   RepositoryHealthMetrics, HealthSummary, RepositoryHealthCalculator
│   ├── activity_dashboard.py         447   ActivityMetrics, ActivitySummary, ActivityDashboard
│   └── exporter.py                   343   ⚠️ FOUR module-level functions, ZERO classes
├── utils/
│   ├── __init__.py                    16    ⚠️ starred `__all__` splat; ruff PLE0604
│   ├── common.py                     918   console, logging setup, quiet mode, panels, global state
│   ├── retry.py                      672   RetryStrategy, Exponential/LinearBackoff, TimeoutAware, RetryConfig
│   ├── prompts.py                    544   interactive prompt helpers
│   ├── logging.py                    529   GitCoLogger, structured logging, rotation
│   ├── rate_limiter.py               351   RateLimitConfig, RateLimiter, RateLimitedAPIClient
│   ├── completion.py                 343   CompletionConfig, CompletionResult, CompletionManager
│   └── exception.py                  177   GitCoError hierarchy (17 typed exceptions)
├── patterns/
│   ├── __init__.py                    27
│   └── constants.py                  476   10 named regex pattern families
├── prompts/
│   ├── __init__.py                     5
│   └── templates.py                  258   ⚠️ line 7 = the import that bricks the package
└── templates/
    ├── __init__.py                    11
    └── shell_completion.py           475   CompletionConfig, CompletionTemplate, ShellCompletionGenerator
```

## 0.3 The Actual Registered Command Tree

Obtained only after manually repairing every import defect and loading the shadowed `cli.py` under an alias:

```
gitco
├── activity            ├── analyze          ├── completion       ├── discover
├── help                ├── init             ├── logs             ├── performance
├── status              ├── sync             ├── validate-repo    └── version
│
├── backup        → cleanup · create · delete · list · restore · validate
├── config        → edit · export · import · show · validate
├── contributions → export · recommendations · stats · sync-history · trending
├── github        → connection-status · get-issues · get-issues-multi · get-repo · rate-limit-status
└── upstream      → add · fetch · merge · remove · update · validate
```

**17 top-level command surfaces; 12 leaf commands at root; 5 command groups; 33 subcommands total.**

## 0.4 The Runtime Truth — Every Command, Executed

After fixing the stale absolute import, injecting alias shims for all ten phantom classes, and restructuring the entry point to defeat the package/module shadowing, the full command tree was executed inside a clean virtualenv with a valid `~/.gitco/config.yml`:

| Command | Result |
|---|---|
| `gitco --version` | ✅ prints `gitco, version 0.1.0` |
| `gitco backup list` | ✅ prints "No backups found" (empty local state; never touches the library) |
| `gitco contributions stats` | ✅ prints all zeros (empty local state; never touches the library) |
| `gitco github rate-limit-status` | ✅ prints "no rate limiters initialized" |
| `gitco status` | ❌ `TypeError: __init__() missing 1 required positional argument: 'github_client'` |
| `gitco sync --repo <name>` | ❌ `TypeError: __init__() takes 1 positional argument but 2 were given` |
| `gitco analyze --repo <name>` | ❌ `AttributeError: 'ChangeAnalyzer' object has no attribute 'analyze_repository'` |
| `gitco discover --skill python` | ❌ `ImportError: cannot import name 'DiscoveryEngine' from 'gitco.libs.discovery'` |
| `gitco activity` | ❌ `TypeError: __init__() missing 1 required positional argument: 'github_client'` |
| `gitco validate-repo --repo <name>` | ❌ `TypeError: __init__() takes 1 positional argument but 2 were given` |
| `gitco config validate` | ❌ `TypeError: get_validation_report() got an unexpected keyword argument 'strict'` |
| `gitco logs` | ❌ `AttributeError: 'GitCoLogger' object has no attribute 'get_recent_logs'` |
| `gitco performance` | ❌ `TypeError: PerformanceMetrics() takes no arguments` |
| `gitco completion bash` | ❌ `Error: Got unexpected extra argument (bash)` (implementation is `--shell`, docs say positional) |
| `gitco upstream fetch --repo <name>` | ❌ `ValidationError: Invalid repository path` — `--repo` is resolved as a CWD-relative filesystem path, not a configured repository name |

**Score, after a full manual repair of every import error: exactly one of seventeen command surfaces does anything meaningful, and it prints a version string.** The three "passing" commands succeed only because they operate on empty local state and never reach the library layer.

## 0.5 Forensic Timeline — How It Got Here

```
2025-08-15 13:13:36 -0700   cad42cf   "chore(test): get rid of tests for now"
                                       68 files changed, 90 insertions(+), 18,261 deletions(-)
                                       ↳ 36 test files            — 16,570 lines
                                       ↳ .github/workflows/ci.yml —    111 lines
                                       ↳ .github/workflows/test-ci.yml —  52 lines
                                       ↳ .github/workflows/pre-upload-test.yml — 311 lines
                                       ↳ .codecov.yml             —     39 lines
                                       ↳ scripts/dry-run-ci.sh    —    209 lines
                                       ↳ scripts/simulate-github-actions.sh — 270 lines
                                       ↳ scripts/validate-workflows.sh —   237 lines

              ⏱ NINE MINUTES LATER (author timestamp)

2025-08-15 13:22:38 -0700   451fd1b   "fix(cli): fix cli inconsistencies"
                                       30 files changed, 4,971 insertions(+), 6,080 deletions(-)
                                       ↳ shattered a monolithic cli.py into cli/{core,config,github,
                                         contributions,backup,upstream}.py
                                       ↳ moved every domain module into libs/
                                       ↳ rewrote all CLI→library glue against a REMEMBERED,
                                         IDEALIZED API rather than the actual one
                                       ↳ created the cli.py / cli/ shadowing collision
                                       ↳ introduced all ten phantom-class call sites

2025-09-28              d15a823   "rm(cost): no need for cost feature"   — cost tracking removed
2025-09-28              792b4bc   "style: fix style issues"
2025-09-28              cb5270c   "rm(cost): keep OpenAI only"           — multi-provider + local LLM removed
2025-09-29 02:14        c6727ee   "fix: fix potential bugs"              — 🔴 THE COMMIT THAT BRICKED IT
                                       4 files, +51/−4; added 47 lines of eager re-exports to
                                       libs/__init__.py, pulling the entire dependency chain into
                                       module-import time and detonating a latent stale import
2025-09-29 15:18        d71824a   "fix: make fixes"                      — added docs/QA.md (780 lines,
                                       a manual test plan for commands that do not exist)
```

**Bisection result — importability of `gitco.libs` by commit:**

| Commit | Date | Message | `import gitco.libs` |
|---|---|---|---|
| `451fd1b` | 2025-08-15 | fix(cli): fix cli inconsistencies | ✅ ok |
| `3792693` | 2025-09-17 | Merge PR #8 (dependabot) | ✅ ok |
| `d15a823` | 2025-09-28 | rm(cost): no need for cost feature | ✅ ok |
| `792b4bc` | 2025-09-28 | style: fix style issues | ✅ ok |
| `cb5270c` | 2025-09-28 | rm(cost): keep OpenAI only | ✅ ok |
| **`c6727ee`** | **2025-09-29** | **`fix: fix potential bugs`** | 🔴 **BROKEN** |
| `d71824a` | 2025-09-29 | fix: make fixes | 🔴 BROKEN |

**The commit that bricked the package is titled `fix: fix potential bugs`, and it has been the tip of `main` for eleven months.** The console entry point, separately, has been structurally unreachable since `451fd1b` — twelve and a half months.

The safety net was deleted and the trapeze act began nine minutes later. Every defect catalogued in this document is downstream of that single ordering decision.

## 0.6 Dimensional Scorecard

| Dimension | Score | Assessment |
|---|---|---|
| Problem selection | **8/10** | Maintaining OSS forks and finding worthwhile contributions are real, felt pains |
| Product thesis | **6/10** | Good pieces, insufficiently unified into one loop |
| Differentiation today | **3/10** | Basic sync and issue discovery are already commoditized |
| CLI breadth | **8/10** | Surprisingly substantial — 33 subcommands |
| UX / onboarding | **5/10** | Many commands, but too much manual YAML setup |
| Internal modularity | **6/10** | Logical module boundaries exist; several files are mini-applications |
| Git-operation safety | **4/10** | Good intent, zero test evidence for destructive/stateful operations |
| **Testing confidence** | **1/10** | **The critical weakness — zero tests exist** |
| CI quality gates | **2/10** | Significant automation; almost none of it gates correctness |
| AI architecture | **3/10** | OpenAI-only, stale default model, brittle regex output parsing |
| Discovery / recommendation | **4/10** | Explainable, but hand-authored additive heuristics |
| Repository-health analytics | **4/10** | Interesting, but bespoke metrics need validation/standardization |
| Security posture | **4/10** | Security tooling exists; every important check is explicitly non-blocking |
| Release engineering | **2/10** | Elaborate workflows built around a distribution name owned by another project |
| Documentation | **8/10** | One of the project's genuine strengths — in structure, not in accuracy |
| Community readiness | **5/10** | CONTRIBUTING, SECURITY, CoC, issue/PR templates all present |
| Community adoption | **1/10** | Essentially unvalidated — 0 stars, 0 forks, 0 releases, 0 users |
| Maintenance signal | **3/10** | Automated dependency activity exists; PR backlog is months stale |
| Long-term potential | **9/10** | If aggressively refocused around the real wedge |
| **Overall today** | **~4/10** | **Promising pre-alpha project, not yet a trustworthy OSS product** |
| **Potential after redesign** | **9+/10** | **Possible category-defining OSS contribution control plane** |

## 0.7 The One-Paragraph Verdict

GitCo is not a beta-quality tool with rough edges. **As shipped at the tip of `main`, it is a non-functional program.** The package cannot be imported at all (`ModuleNotFoundError: No module named 'gitco.detector'`); the `gitco` console script crashes on `--help`; and the declared entry point `gitco.cli:main` has been structurally unreachable since 2025-08-15 because a `cli/` package permanently shadows the `cli.py` module that defines `main`. Even after repairing every import defect and the entry-point shadowing by hand, sixteen of seventeen command surfaces still fail at runtime because the CLI layer calls constructors and methods that exist nowhere in the codebase. The README's headline instruction — `pip install gitco` — installs a completely different tool by a different author, because the `gitco` name on PyPI was claimed in November 2024, nine months before this repository's first commit. **However**, underneath the breakage sits roughly 12,000 lines of genuinely thoughtful library code: a competent `GitRepositoryManager` with stash-safety and merge-conflict recovery, a real skill-matching engine, a token-bucket rate limiter with separate GitHub and LLM budgets, a retry framework with jitter and recoverable-error classification, structured logging better than most production services have, and a deterministic no-LLM analysis fallback. **The problem is not that the ideas are bad. The problem is that the wiring between a real library and a fictional CLI was never once executed — not by CI, not by a test, not even manually by its author.** That is a two-day repair to a working tool, a two-month program to a credible one, and a six-month program to something with a genuine, defensible reason to exist.

---

# PART 1 — THE UNIFIED SEVERITY LEDGER

| # | Finding | Severity | Verification |
|---|---|---|---|
| **F-01** | Package does not import; every CLI invocation crashes, including `--help` and `--version` | 🔴 **P0 — Catastrophic** | Reproduced by execution |
| **F-02** | `cli.py` / `cli/` name collision makes the console entry point permanently unreachable | 🔴 **P0 — Catastrophic** | Reproduced by execution |
| **F-03** | CLI layer calls ~14 classes/methods that exist nowhere in the codebase | 🔴 **P0 — Catastrophic** | AST audit + execution |
| **F-04** | `pip install gitco` installs a different, unrelated project by a different author | 🔴 **P0 — Catastrophic** | PyPI namespace verification |
| **F-05** | 16,570 lines of tests + all CI deliberately deleted; zero automated verification exists | 🔴 **P0 — Catastrophic** | Git history forensics |
| **F-06** | `libs/__init__.py` eagerly re-exports four nonexistent symbols, poisoning package import | 🔴 **P0 — Catastrophic** | Reproduced by execution |
| **F-07** | GitHub tokens and base64'd `username:password` passed as `curl` argv → process-table leak (CWE-214) | 🟠 **P1 — High** | Source read |
| **F-08** | `SSHGitHubClient` response parser reads `curl -w` output from the wrong end of stdout — every request it makes fails unconditionally | 🟠 **P1 — High** | Verified against live `curl` semantics |
| **F-09** | CI "secret scanning" gate is a silent no-op (`grep` without `-E`) | 🟠 **P1 — High** | Reproduced |
| **F-10** | `except ImportError` around command registration converts hard failure into a warning with exit code 0 | 🟠 **P1 — High** | Reproduced |
| **F-11** | Every security tool in every workflow is suffixed `\|\| true`; none can fail a build | 🟠 **P1 — High** | Workflow read |
| **F-12** | `.secrets.baseline` is referenced by two workflows and does not exist | 🟠 **P1 — High** | Confirmed absent |
| **F-13** | Backup restoration writes archive-derived paths with no traversal guard (Zip Slip / CWE-22) | 🟠 **P1 — High** | Source read |
| **F-14** | 199 `except Exception` blocks; 161 flagged blind-except; 2 `except Exception: pass` | 🟠 **P1 — High** | `ruff` + grep |
| **F-15** | `.git` treated as a directory → valid linked worktrees rejected as non-repositories | 🟠 **P1 — High** | Source read |
| **F-16** | Prompt-injection surface: attacker-controlled upstream diffs and commit messages flow into LLM prompts with no delimiting, hardening, or output validation | 🟠 **P1 — High** | Source read |
| **F-17** | LLM output parsed by regex against free-form text; model self-reports its own confidence | 🟡 **P2 — Medium** | Source read |
| **F-18** | Default analysis model is `gpt-3.5-turbo`; provider support reduced to OpenAI-only | 🟡 **P2 — Medium** | Source read |
| **F-19** | Two declared dependencies (`gitpython`, `tiktoken`) are never imported | 🟡 **P2 — Medium** | grep |
| **F-20** | Three parallel HTTP stacks (`requests`, `PyGithub`, shelled-out `curl`) | 🟡 **P2 — Medium** | Source read |
| **F-21** | `Typing :: Typed` classifier claimed; no `py.typed`, no `mypy`, no type CI | 🟡 **P2 — Medium** | Confirmed |
| **F-22** | Documentation describes ~15 commands/flags that do not exist | 🟡 **P2 — Medium** | Diffed against live command tree |
| **F-23** | `SECURITY.md` retains unedited GitHub template boilerplate; claims 1.0.x support at v0.1.0 | 🟡 **P2 — Medium** | Confirmed |
| **F-24** | 240-line `.github/security/config.yml` is read by nothing — pure theater | 🟡 **P2 — Medium** | Repo-wide grep |
| **F-25** | Identity split across `smusali/` and `41technologies/`; all metadata URLs point away from the canonical repo | 🟡 **P2 — Medium** | Confirmed |
| **F-26** | `git_ops.py` is 3,178 lines holding four unrelated responsibilities | 🟡 **P2 — Medium** | Source read |
| **F-27** | `Development Status :: 4 - Beta` on a program that does not start | 🟡 **P2 — Medium** | Confirmed |
| **F-28** | `release.yml` uses `actions/create-release@v1`, archived by GitHub since 2021 | 🟡 **P2 — Medium** | Workflow read |
| **F-29** | PyPI publishing uses a long-lived `PYPI_API_TOKEN`; no OIDC, no `id-token: write`, no attestations | 🟡 **P2 — Medium** | Workflow read |
| **F-30** | Dependabot `reviewers`/`assignees` point at `41technologies` while the repo lives under `smusali` | 🟡 **P2 — Medium** | Confirmed |
| **F-31** | Scoring systems (`collaboration`, `recognition`, `influence`, `sustainability`, opportunity fit) are arbitrary additive constants presented as measurements | 🟡 **P2 — Medium** | Source read |
| **F-32** | 15 open PRs, predominantly stale Dependabot; automated PR creation is not dependency maintenance | 🟡 **P2 — Medium** | Confirmed |
| **F-33** | 54 function-level imports (`PLC0415`) hide failures until the exact command runs | 🟡 **P2 — Medium** | `ruff` |
| **F-34** | Config at `~/.gitco/config.yml` violates the XDG Base Directory specification | 🔵 **P3 — Low** | Source read |
| **F-35** | 202 f-string logging calls (`G004`) break structured logging and lazy formatting | 🔵 **P3 — Low** | `ruff` |
| **F-36** | 23 naive `datetime.now()` calls (`DTZ005`) → timezone-ambiguous timestamps in exports and backups | 🔵 **P3 — Low** | `ruff` |
| **F-37** | 48 `logging.error` in `except` blocks where `.exception` belongs (`TRY400`) → stack traces lost | 🔵 **P3 — Low** | `ruff` |
| **F-38** | 7 `subprocess.run` calls, **zero** with `check=True` — non-zero exits silently ignored | 🔵 **P3 — Low** | grep |
| **F-39** | `$EDITOR` from environment invoked via `subprocess.run` with no validation and no `check=` | 🔵 **P3 — Low** | Source read |
| **F-40** | Formatting toolchain a generation behind: `black` 23.12.1, archived `mirrors-prettier`, `ruff-format` deliberately disabled | 🔵 **P3 — Low** | Config read |
| **F-41** | `.pre-commit-config.yaml` is not enforced in any workflow | 🔵 **P3 — Low** | Workflow read |
| **F-42** | Zero `TODO`/`FIXME` markers in 19,565 lines — no contributor entry points, no acknowledged gaps | 🔵 **P3 — Low** | grep |
| **F-43** | `CONTRIBUTING.md` contains zero mentions of tests or how to run them | 🔵 **P3 — Low** | grep |
| **F-44** | 25 bare `pass` bodies; 16 flagged `PIE790` unnecessary-placeholder | 🔵 **P3 — Low** | `ruff` |
| **F-45** | `utils/__init__.py` builds `__all__` from starred splats (`PLE0604`) — unverifiable and fragile | 🔵 **P3 — Low** | `ruff` |
| **F-46** | Version constant duplicated in `gitco/__init__.py` and `gitco/libs/__init__.py`; drift is inevitable | 🔵 **P3 — Low** | Source read |
| **F-47** | No `LICENSE` headers, no SBOM, no provenance, no lockfile, no `CITATION.cff`, no `.editorconfig` | 🔵 **P3 — Low** | Confirmed |
| **F-48** | `MANIFEST.in` ships `*.pyi` recursively but the package has none; `package-data` is empty | 🔵 **P3 — Low** | Confirmed |
| **F-49** | No `--dry-run`, no plan-first mode, no transaction journal, no `undo` on any mutating command | 🔵 **P3 — Low** | Command-tree audit |
| **F-50** | No `gitco doctor`; no environment/credential/config preflight of any kind | 🔵 **P3 — Low** | Command-tree audit |

---

# PART 2 — THE CATASTROPHIC FINDINGS (P0)

These are not "bugs." They are the difference between a program and a directory of Python files.

## F-01 — The Package Does Not Import

**Reproduction:**

```bash
python -m build --wheel
pip install dist/gitco-0.1.0-py3-none-any.whl
gitco --help
```

**Actual output:**

```
Traceback (most recent call last):
  File "/venv/bin/gitco", line 3, in <module>
    from gitco.cli import main
  File ".../gitco/cli/__init__.py", line 7, in <module>
    from .backup import backup_commands
  File ".../gitco/cli/backup.py", line 11, in <module>
    from ..libs.backup import (
  File ".../gitco/libs/__init__.py", line 13, in <module>
    from .analyzer import ChangeAnalysis, ChangeAnalyzer
  File ".../gitco/libs/analyzer.py", line 12, in <module>
    from ..prompts import PromptManager
  File ".../gitco/prompts/__init__.py", line 3, in <module>
    from .templates import PromptManager
  File ".../gitco/prompts/templates.py", line 7, in <module>
    from gitco.detector import BreakingChange, Deprecation, SecurityUpdate
ModuleNotFoundError: No module named 'gitco.detector'
```

**Root cause.** `src/gitco/prompts/templates.py:7` contains a stale absolute import left over from the `451fd1b` refactor that moved `detector.py` into `libs/`:

```python
from gitco.detector import BreakingChange, Deprecation, SecurityUpdate   # ❌ module moved
#    ^^^^^^^^^^^^^^ must be ..libs.detector
```

**Why this is worse than it looks.** This is not an edge case reachable only by an exotic command. `libs/__init__.py` eagerly imports `analyzer`, which imports `prompts`, which executes this line at module-import time. Therefore `import gitco.libs` fails, `import gitco.cli` fails, and **every single CLI invocation fails — including `gitco --version` and `gitco --help`.** There is no code path that avoids it.

**The fix (one line):**

```diff
- from gitco.detector import BreakingChange, Deprecation, SecurityUpdate
+ from ..libs.detector import BreakingChange, Deprecation, SecurityUpdate
```

**Two sibling defects of the same class**, in `src/gitco/utils/completion.py` at lines 158 and 175:

```python
from ..config import get_config_manager    # ❌ gitco.config does not exist; it is gitco.libs.config
```

Both are wrapped in `try: ... except Exception: pass`, so they fail **silently** — shell completion for repository names and skill names simply returns an empty list forever, and no user or log will ever say why. These are simultaneously an instance of F-01 (stale module path) and of F-14 (blind except concealing a defect).

**The fix:**

```diff
- from ..config import get_config_manager
+ from ..libs.config import get_config_manager
```

and replace `except Exception: pass` with a logged, typed handler.

## F-02 — The Console Entry Point Has Been Structurally Unreachable Since August 2025

This is the single most important structural finding in this document, and it is invisible to code review, to `ruff`, to `black`, and to `bandit`.

The package contains **both**:

```
src/gitco/cli.py          ← 138 lines; defines `main`, the Click group. THE DECLARED ENTRY POINT.
src/gitco/cli/__init__.py ← 21 lines;  imports six command modules; does NOT define `main`.
src/gitco/cli/{core,config,github,contributions,backup,upstream}.py
```

`pyproject.toml` declares the entry point twice, in both the modern and legacy forms:

```toml
[project.scripts]
gitco = "gitco.cli:main"

[project.entry-points."console_scripts"]
gitco = "gitco.cli:main"
```

**In Python's import system, a package always shadows a same-named module in the same parent package.** `gitco/cli/` wins unconditionally. `gitco/cli.py` is therefore **permanently unreachable dead code**, and `from gitco.cli import main` resolves to `gitco/cli/__init__.py`, which has no `main`.

**Proof (executed):**

```python
>>> import gitco.cli as c
>>> c.__file__
'.../src/gitco/cli/__init__.py'      # ← the package, not cli.py
>>> hasattr(c, 'main')
False
>>> from gitco.cli import main
ImportError: cannot import name 'main' from 'gitco.cli'
```

And `cli.py` cannot be loaded standalone either, because its relative imports (`from . import __version__`, `from .utils.common import ...`) have no parent-package context:

```
ImportError: attempted relative import with no known parent package
```

**Consequences, all of them load-bearing:**

1. **The `gitco` command has never worked, not once, since 2025-08-15.** Not since `c6727ee` broke the import — since `451fd1b`, twelve and a half months ago.
2. **Every global option defined in `cli.py` has never been wired to anything.** All eleven — `--verbose`, `--quiet`, `--debug`, `--log-file`, `--detailed-log`, `--max-log-size`, `--log-backups`, `--config`, `--log-level`, `--output-format`, `--no-color` — are documented across the docs set. **None are reachable.**
3. **The 138 lines of `cli.py` never execute.** That includes `setup_logging()`, `set_quiet_mode()`, and the entire `ctx.obj` population block. Every subcommand reads configuration via `ctx.obj.get("config")`. Because `ctx.obj` is never populated by the group callback, **`ConfigManager(ctx.obj.get("config"))` would receive `None` even if every import were fixed.** The advertised "quiet mode for CI/CD integration" is likewise inert.
4. **No static tool catches this.** `ruff`, `black`, and `bandit` do not import the package. Only executing it — or a single `tests/test_imports.py` — catches it. Such a file **existed** (22 lines) and **was deleted** in `cad42cf`.

**The fix.** Delete `src/gitco/cli.py`. Move `main` into `src/gitco/cli/__init__.py` (or into `src/gitco/cli/_main.py` re-exported from `__init__.py`), and call `register_*_commands(main)` there. Add `src/gitco/__main__.py` containing `from .cli import main; main()` so `python -m gitco` works. Assert in CI that `from <pkg>.cli import main` resolves and that the resolved `__file__` is the intended one.

## F-03 — The CLI Was Written Against an API That Was Never Implemented

This is the deepest and most expensive finding. **The CLI layer and the library layer are two independently-written halves of a program that have never been connected.**

An AST auditor resolving every intra-package import against the target module's real symbol table found **17 broken imports**. Ten of them are in `cli/core.py`, and every one is a **function-level import inside a Click command body** — invisible until that exact command is run.

| Location | Symbol imported | Definitions in codebase | Command destroyed |
|---|---|---|---|
| `cli/core.py:271` | `libs.git_ops.GitOperations` | ❌ **0** | `gitco sync` |
| `cli/core.py:281` | `libs.analyzer.Analyzer` | ❌ **0** | `gitco sync --analyze` |
| `cli/core.py:296` | `libs.analyzer.Analyzer` | ❌ **0** | `gitco sync --batch --analyze` |
| `cli/core.py:359` | `libs.analyzer.Analyzer` | ❌ **0** | `gitco analyze` |
| `cli/core.py:448` | `libs.discovery.DiscoveryEngine` | ❌ **0** | `gitco discover` |
| `cli/core.py:528` | `libs.health_metrics.HealthMetrics` | ❌ **0** | `gitco status` |
| `cli/core.py:744` | `utils.logging.LogManager` | ❌ **0** | `gitco logs` |
| `cli/core.py:782` | `libs.health_metrics.PerformanceMetrics` | ❌ **0** | `gitco performance` |
| `cli/core.py:857` | `templates.shell_completion.ShellCompletion` | ❌ **0** | `gitco completion` |
| `cli/core.py:910` | `libs.git_ops.RepositoryValidator` | ❌ **0** | `gitco validate-repo` |
| `libs/__init__.py:18` | `libs.discovery.ContributionDiscovery` | ❌ **0** | *package import* |
| `libs/__init__.py:19` | `libs.exporter.DataExporter` | ❌ **0** | *package import* |
| `libs/__init__.py:20` | `libs.git_ops.GitOperations` | ❌ **0** | *package import* |
| `libs/__init__.py:22` | `libs.health_metrics.HealthMetrics` | ❌ **0** | *package import* |

Repository-wide search for each: `grep -rn "^class <Name>" src/` → **zero results** for all ten of `GitOperations`, `Analyzer`, `DiscoveryEngine`, `HealthMetrics`, `PerformanceMetrics`, `LogManager`, `ShellCompletion`, `RepositoryValidator`, `DataExporter`, `ContributionDiscovery`.

**`libs/exporter.py` contains no classes at all** — only four module-level functions (`export_sync_results`, `export_discovery_results`, `export_contribution_data_to_csv`, `export_health_data`) — yet `DataExporter` is re-exported from it in `libs/__init__.py`.

**The four headline features on the README are `sync`, `analyze`, `discover`, and `status`. All four are on this list.**

### The Anatomy of the Mismatch

`cli/core.py:248–305` (`sync`) against what actually exists:

```python
# ── WHAT THE CLI CALLS ──────────────────  # ── WHAT ACTUALLY EXISTS ─────────────────────────
git_ops = GitOperations(config)             # GitRepositoryManager.__init__(self)  ← takes NO arguments
git_ops.sync_repository(repo,               # .sync_repository(self, path: str)    ← takes a PATH; no kwargs
                        stash=stash,
                        force=force)
git_ops.batch_sync(repos, ...)              # .batch_sync_repositories(...)        ← different name
git_ops.sync_all_repositories(...)          # ✗ does not exist at all
config.repositories.keys()                  # Config.repositories: Optional[list[Repository]]
                                            #   ← a LIST has no .keys(); guaranteed AttributeError
analyzer = Analyzer(config)                 # ChangeAnalyzer(config)               ← different name
analyzer.analyze_repository(repo)           # .analyze_repository_changes(...)     ← different name AND signature
```

**Every single line is wrong.** `config.repositories.keys()` on a `list[Repository]` is an `AttributeError` waiting on line 288. This code has provably never been executed once — not by CI, not by a test, not manually by its author.

### Additional Phantom Method Calls (AST call-graph audit)

Beyond the imports, four more calls target methods that do not exist on classes that do:

```
cli/core.py:663      ActivityDashboard.get_repository_activity()       ✗
cli/core.py:669      ActivityDashboard.get_all_repositories_activity() ✗
cli/upstream.py:393  GitRepository.get_default_branch_name()           ✗  (real: get_default_branch)
cli/upstream.py:396  GitRepository.merge_upstream()                    ✗  (real: merge_upstream_branch)
```

### The Real APIs That Exist and Are Being Ignored

`GitRepositoryManager` (lines 2168–3178) exposes **33 public methods** that the CLI never calls correctly:

```
batch_sync_repositories · batch_fetch_repositories · batch_validate_repositories
detect_repositories · validate_repository_path · get_repository_info · validate_repository_config
check_repository_sync_status · setup_upstream_remote · remove_upstream_remote
update_upstream_remote · validate_upstream_remote · safe_stash_changes · restore_stash
drop_stash · list_stashes · has_uncommitted_changes · safe_stash_and_restore
fetch_upstream · merge_upstream_branch · abort_merge · resolve_conflicts · get_merge_status
sync_repository_with_upstream · sync_repository · fetch_repository · validate_repository · get_repository
```

`GitRepository` (lines 873–2167) exposes another 32 including `create_stash`, `apply_stash`, `get_commit_diff_analysis`, `get_recent_changes`, and `_detect_merge_conflicts`.

`ChangeAnalyzer` exposes `analyze_repository_changes`, `analyze_specific_commit`, `get_commit_summary`, `_categorize_commits`, and `get_analyzer`.

**The library is not the problem. The library is good. The glue is fiction.**

### The Diagnosis

On 2025-08-15, `451fd1b` shattered a 5,364-line monolithic `cli.py` into six modules **and rewrote the glue code from scratch against a remembered, idealized version of the library API rather than the actual one.** With 16,570 lines of tests deleted nine minutes earlier and every CI workflow removed in the same stroke, **no mechanism remained that could notice.**

## F-04 — `pip install gitco` Installs Somebody Else's Software

The README's first actionable instruction, repeated in `docs/quick-start.md`, `docs/faq.md`, `docs/tutorials.md`, and `docs/usage.md`, is:

```bash
pip install gitco
```

**The `gitco` name on PyPI belongs to a different project.** `pypi.org/project/gitco` resolves to:

- **Author:** Emmanuel Létremble (published under the account Valkea) — not FortyOne Technologies
- **Version:** 0.0.6
- **Released:** 2024-11-11 — **nine months before this repository's first commit**
- **Description:** *"A simple command to generate git commit messages from the current diff file"*
- **Function:** an Azure-OpenAI-backed commit-message generator. Entirely unrelated to fork management.

**This is the most commercially and reputationally damaging finding in this document, because unlike every other one it is not fixable by writing better code:**

1. Every user who follows the documentation installs an unrelated tool.
2. The unrelated tool **also installs a `gitco` console script**, so `$PATH` collides even for users who install both.
3. `pyproject.toml` declares `name = "gitco"`. The `pypi-publish.yml` workflow will `twine upload` under that name and **fail with HTTP 403 — permanently, for any version, forever.**
4. **The workflow's own availability guard is broken in a way that masks this.** `pypi-publish.yml:152` runs:
   ```bash
   if pip index versions gitco | grep -q "$VERSION"; then
   ```
   This queries the **foreign** project's version list. Since `0.1.0` is not among the other author's releases, the workflow prints `✅ Version 0.1.0 is available for publishing` and proceeds confidently to a guaranteed 403.
5. Search results for "GitCo" become permanently ambiguous; dependency manifests naming `gitco` refer to the wrong project; security reporting becomes confusing; and **no trustworthy supply-chain provenance can be established while the distribution identity is contested.**

**Required action — blocking, before another line of feature code is written.**

Choose an uncontested distribution identifier, register it on PyPI immediately as an empty `0.0.0` placeholder to claim the namespace, then update in lockstep: `pyproject.toml` `name`, both entry-point tables, the console-script name if it changes, the README, all five documentation files that repeat the install command, both release workflows, and the `pip index versions` guard.

A workable split is:

```
Repository brand:     GitCo
Python distribution:  <unique, unambiguous package name>
CLI executable:       gitco
```

A cleaner long-term option is one unique name everywhere — and note that the **GitCo brand itself** deserves reconsideration, because multiple unrelated projects have used the name over time. Candidate distribution names: `gitco-cli`, `gitcosync`, `forkco`, `upco`, `gitco-oss`.

**Corollary — the identity is also split at the repository level.** `Homepage`, `Documentation`, `Repository`, `Source Code`, `Bug Tracker`, `Feature Requests`, `Security`, `Changelog`, `Releases`, and `CI/CD` in `pyproject.toml` **all point to `github.com/41technologies/gitco`**, while the canonical repository under assessment is `github.com/smusali/gitco`. Both exist. `__url__` in both `gitco/__init__.py` and `gitco/libs/__init__.py` also points at `41technologies`. Dependabot assigns reviewers to `41technologies`. **A project whose own package metadata points somewhere else is a project users cannot file a bug against.** Pick one canonical home and make every URL, every reviewer assignment, and every `__url__` constant agree.

## F-05 — The Tests and CI Were Deliberately Deleted, and Nothing Replaced Them

Commit `cad42cf`, 2025-08-15 13:13:36 -0700, titled **"`chore(test): get rid of tests for now`"**:

```
68 files changed, 90 insertions(+), 18,261 deletions(-)
```

**What was destroyed:**

| Artifact | Lines |
|---|---|
| 36 test files under `tests/` | **16,570** |
| `.github/workflows/ci.yml` | 111 |
| `.github/workflows/pre-upload-test.yml` | 311 |
| `.github/workflows/test-ci.yml` | 52 |
| `.github/workflows/release.yml` (partial) | 124 |
| `.github/workflows/pypi-publish.yml` (partial) | 89 |
| `.codecov.yml` | 39 |
| `scripts/simulate-github-actions.sh` | 270 |
| `scripts/validate-workflows.sh` | 237 |
| `scripts/dry-run-ci.sh` | 209 |

Among the casualties, with grim irony:

- **`tests/test_imports.py` (22 lines)** — this file alone would have caught F-01, F-02, and F-06 on the very next push.
- `tests/test_git_ops.py` (1,541 lines) — the destructive-operation safety net
- `tests/test_analyzer.py` (1,521 lines)
- `tests/test_detector.py` (1,295 lines)
- `tests/test_config.py` (1,232 lines)
- `tests/test_github_client.py` (1,232 lines)
- `tests/utils/test_rate_limiter.py` (514 lines)
- `tests/utils/test_retry.py` (450 lines)
- `tests/utils/test_logging.py` (394 lines)
- `tests/utils/test_prompts.py` (165 lines)
- **`tests/test_cli.py` (712 lines)** — would have caught **all ten** phantom-class failures in F-03

**"For now" has now lasted 12.5 months.**

**What remains as "QA":** `docs/QA.md`, a 780-line **manual** test plan added in the final commit (`d71824a`). It is not automation, it is gated by nothing, it is referenced by no workflow, and — as Part 6 demonstrates — it documents at least a dozen commands and flags that do not exist and specifies a configuration path the code does not use. Its two stated prerequisites, `gitco --version` and `gitco config validate`, **both crash on the very commit that introduced the file.** It cannot have been executed even once. **Adding a manual QA document as the last act of a project whose automated tests were deleted is documentation produced in place of verification.**

**Current CI reality.** Three workflows exist:

- **`pr-checks.yml`** — runs (a) a conventional-commit PR-title check, (b) a broken-link scan whose entire pipeline is suffixed `|| true`, (c) a YAML parse check, (d) `pip list --outdated`, (e) `pip-audit ... || true`. **It contains no `pytest`, no `ruff check`, no `black --check`, no build, and no import of the package.**
- **`release.yml`** and **`pypi-publish.yml`** — fire only on `push: tags: v*`. **The repository has zero tags. Neither workflow has ever executed.** Several hundred lines of release automation are entirely unverified.

**In effect: GitCo has no CI. A green checkmark on a PR means the title was formatted correctly.**

The `pypi-publish.yml` `verify` step does `pip install gitco==$VERSION`, `python -c "import gitco"`, `gitco --help`. **That step would have caught F-01 and F-02 instantly.** It has never run, because there are no tags — and when it does run it will install the *foreign* package (F-04).

## F-06 — `libs/__init__.py` Eagerly Re-exports Four Symbols That Do Not Exist

Even with F-01's stale import repaired, `import gitco.libs` still fails:

```
File ".../gitco/libs/__init__.py", line 18, in <module>
    from .discovery import ContributionDiscovery
ImportError: cannot import name 'ContributionDiscovery' from 'gitco.libs.discovery'
```

`libs/__init__.py` — introduced wholesale by `c6727ee`, the commit titled *"fix: fix potential bugs"* — eagerly imports eleven modules and re-exports 24 names, four of which (`ContributionDiscovery`, `DataExporter`, `GitOperations`, `HealthMetrics`) have no definition anywhere.

This has two compounding effects beyond the immediate `ImportError`:

1. **It converts every latent module-level defect in the entire `libs/` tree into a hard package-import failure.** Before `c6727ee`, `libs/__init__.py` contained only five string constants and the stale import in `prompts/templates.py` lay dormant. The eager re-export chain is what detonated it.
2. **It makes `import gitco` transitively load the OpenAI SDK, PyGithub, Jinja2, psutil, requests, and urllib3** on every invocation, including `--help`. Startup cost is paid unconditionally for functionality most invocations never touch.

**The fix.** Remove the four phantom re-exports. Then decide deliberately whether `libs/__init__.py` should re-export anything at all — a lazy `__getattr__` (PEP 562) or an empty `__init__.py` with explicit submodule imports at each call site is materially safer and faster. Whatever is chosen, `tests/test_imports.py` must assert that every name in `__all__` is actually resolvable.

---

# PART 3 — SECURITY

## F-07 — GitHub Credentials Are Leaked to the Process Table (CWE-214) 🟠 HIGH

`src/gitco/libs/github_client.py`, inside `SSHGitHubClient._make_ssh_request` (lines 94–201):

```python
curl_cmd = ["curl", "-s", "-w", "%{http_code}\\n%{header_json}\\n", "-X", method, url]
curl_cmd.extend(["-H", "Accept: application/vnd.github.v3+json"])
curl_cmd.extend(["-H", "User-Agent: GitCo/1.0"])

if self.auth_info.token:
    curl_cmd.extend(["-H", f"Authorization: token {self.auth_info.token}"])
elif self.auth_info.username and self.auth_info.password:
    import base64
    credentials = base64.b64encode(
        f"{self.auth_info.username}:{self.auth_info.password}".encode()
    ).decode()
    curl_cmd.extend(["-H", f"Authorization: Basic {credentials}"])

result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
```

**Every API call through this client spawns a `curl` process with the bearer token — or the base64'd `username:password` — as a command-line argument.**

On Linux, `/proc/<pid>/cmdline` is world-readable by default. On macOS and BSD, `ps aux` shows full argv. **Any unprivileged local user, any co-tenant container sharing a PID namespace in a CI runner, any process-monitoring or EDR agent, and any crash/telemetry reporter can read the user's GitHub credential for the lifetime of the request.** Base64 is an encoding, not encryption; the `Basic` branch leaks a **plaintext password** to anyone who runs `base64 -d`.

This is textbook **CWE-214: Invocation of Process Using Visible Sensitive Information.** It is entirely avoidable: `requests` and `PyGithub` are **already declared dependencies of this project**, and both keep the credential in-process.

**Aggravating factors:**

- **`bandit` does not flag it.** Bandit flags `B603` for untrusted subprocess input, not for credential placement in argv. The project's own security scanning gives false assurance on exactly the finding it should catch.
- **The method is named `_make_ssh_request` but performs HTTPS via `curl`.** The naming actively misleads a reviewer into believing SSH key auth is in play. `SSHGitHubClient` is likewise a misnomer for an HTTPS client.
- **`S607` (start-process-with-partial-path)** applies: `curl` and `git` are resolved via `$PATH`. Three occurrences flagged in `git_ops.py`.
- **No `check=` on the `subprocess.run`**; only `returncode != 0` is inspected manually, and the whole body is wrapped in `except Exception` that re-raises a generic `APIError`, discarding the distinction between a network failure, a parse failure, and an auth failure.

**The fix (P1, this week).** Delete `SSHGitHubClient` and `_make_ssh_request` entirely. Route all GitHub traffic through a single `requests.Session` (or `httpx.Client`) with `session.headers["Authorization"]` set in-process. If credential discovery via `gh`/git-credential is wanted, capture the token in-process and pass it as a header — **never through argv, never through an environment variable inherited by a child process that does not need it.**

## F-08 — The `curl` Response Parser Reads From the Wrong End of Stdout 🟠 HIGH

A defect not previously catalogued. `_make_ssh_request` parses the response as:

```python
lines = result.stdout.strip().split("\n")
if len(lines) < 2:
    raise APIError("Invalid response format from GitHub API")

status_code = int(lines[0])                                    # ← expects status on line 0
headers_json = lines[1]                                        # ← expects headers on line 1
response_data = "\n".join(lines[2:]) if len(lines) > 2 else "{}"
```

**`curl` writes the response body to stdout first, and appends the `-w` write-out string afterwards.** Verified empirically against a live endpoint: with `-w '%{http_code}\n%{header_json}\n'`, stdout is `<body>\n<http_code>\n<header_json>\n`. The status code and headers land at the **end**, not the beginning.

Therefore `lines[0]` is the first line of the JSON body — typically the single character `{`. `int("{")` raises `ValueError`, which is swallowed by the trailing `except Exception as e: raise APIError(...)`.

**Consequence: every request made through `SSHGitHubClient` fails unconditionally, with a misleading `APIError: SSH request failed: invalid literal for int() with base 10: '{'`, regardless of network, auth, or endpoint validity.** The body is never parsed; the headers are never parsed; the status is never known.

**Mitigating context, stated precisely:** `SSHGitHubClient` and its factory `create_ssh_github_client` are defined in `github_client.py` but are **constructed by nothing else in the codebase** — the CLI paths reach `GitHubClient` (the `requests`-based client) instead. So this code is currently dead weight shipped inside the wheel. That does not make it safe: it is a live credential-leak vector plus a guaranteed-broken parser sitting in the distributed artifact, one import away from being wired in by a future contributor who reasonably assumes it works.

**The fix.** Delete it. Do not repair it. If SSH-transport GitHub API access is ever genuinely needed, it does not exist as a concept — GitHub's REST API is HTTPS-only; SSH is a Git *transport*, not an API transport. The entire abstraction rests on a category error, and **the authentication section below explains the correct separation.**

## F-09 — The CI Secret-Scanning Gate Is a Silent No-Op 🟠 HIGH

`.github/workflows/pypi-publish.yml:70`:

```yaml
if grep -r "sk-|pk_|ghp_|gho_|ghu_|ghs_|ghr_" src/; then
  echo "❌ Potential secrets found in code"
  exit 1
fi
```

**`grep` without `-E` treats `|` as a literal pipe character.** This searches for the single literal string `sk-|pk_|ghp_|gho_|ghu_|ghs_|ghr_`, which will never appear in source code.

**Proof:**

```bash
$ echo 'TOKEN="ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"' > src/leak.py
$ grep -r "sk-|pk_|ghp_|gho_|ghu_|ghs_|ghr_" src/;  echo "exit=$?"
exit=1                                            # ← NO MATCH. Gate passes.
$ grep -rE "sk-|ghp_" src/;                        echo "exit=$?"
src/leak.py:TOKEN="ghp_AAAA..."
exit=0                                            # ← correct behavior
```

A real leaked GitHub PAT sails straight through the gate that exists specifically to catch it.

**The fix.** `grep -rE` is the one-character repair. The better fix is to delete the hand-rolled grep entirely and rely on `gitleaks` or a correctly-configured `detect-secrets` with a committed baseline, run as a **blocking** step.

## F-11 / F-12 — Every Security Tool Is Advisory; the Baseline They Depend On Does Not Exist 🟠 HIGH

Every security invocation across all three workflows:

```yaml
# pr-checks.yml
done || true                                             # broken-link scan — line 56
pip-audit --format json --output pip-audit-report.json || true    # line 84

# release.yml
pip-audit --format json --output pip-audit.json || true           # line 62
bandit -r src/ -f json -o bandit-report.json || true              # line 65
detect-secrets scan --baseline .secrets.baseline . > ... || true  # line 68
pip-audit --format json --output pip-audit.json || true           # line 156

# pypi-publish.yml
detect-secrets scan --baseline .secrets.baseline . > ... || true  # line 54
bandit -r src/ -f json -o bandit-report.json || true              # line 58
pip-audit --format json --output pip-audit-report.json || true    # line 62
safety check --json --output safety-report.json || true           # line 66
pip-audit --format json --output pip-audit.json || true           # line 207
```

**Nine security tool invocations. All nine suffixed `|| true`. Not one can fail a build.** They generate JSON artifacts that nobody reads and that gate nothing.

Compounding it: **`.secrets.baseline` does not exist in the repository.** `detect-secrets scan --baseline .secrets.baseline` errors immediately; the error is swallowed by `|| true`; the workflow reports success and uploads an artifact containing the error text.

The documentation-link checker has the same shape — an entire `while read url; do ... exit 1; done` pipeline terminated by `|| true`, so a broken link exits the subshell and the step still passes.

**This is the precise definition of security theater: the visual appearance of a strong gate, providing zero enforcement.**

**The fix.** Remove every `|| true` from security steps. Commit a real `.secrets.baseline`. Make `pip-audit` fail on findings above a documented severity floor, with an explicit, reviewed, time-boxed ignore list for accepted risks. Where a scanner is genuinely intended to be advisory, say so in the step name (`Advisory: bandit report`) so a reader cannot mistake it for a gate — and make at least one blocking gate exist alongside it.

## F-13 — Backup Restoration Has No Path-Traversal Guard (Zip Slip, CWE-22) 🟠 HIGH

`src/gitco/libs/backup.py`, `_restore_repository` (lines ~458–481):

```python
os.makedirs(target_path, exist_ok=True)
repo_prefix = f"repositories/{repo_name}/"

for file_info in zip_file.filelist:
    if file_info.filename.startswith(repo_prefix):
        relative_path = file_info.filename[len(repo_prefix):]
        if relative_path:
            target_file_path = os.path.join(target_path, relative_path)   # ← unvalidated
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            with (zip_file.open(file_info.filename) as source,
                  open(target_file_path, "wb") as target):
                target.write(source.read())
```

The archive-supplied `relative_path` is joined to the destination with **no normalization and no containment check**. Two distinct escapes are available:

1. **Traversal** — an entry named `repositories/<name>/../../../../.ssh/authorized_keys` resolves outside `target_path` and is written there.
2. **Absolute-path override** — `os.path.join(base, "/etc/cron.d/x")` in Python returns `/etc/cron.d/x`, discarding the base entirely. An archive entry whose suffix begins with `/` writes to an absolute location.

GitCo normally creates its own archives, but `gitco backup restore --backup-id <id>` accepts any file in the backup directory, and backups are exactly the kind of artifact users copy between machines, restore from shared storage, and receive from colleagues. **An archive-restoration routine must defend against its own input regardless of provenance.**

**The fix:**

```python
base = Path(target_path).resolve()
candidate = (base / relative_path).resolve()
candidate.relative_to(base)          # raises ValueError if the entry escapes
```

Reject — do not silently skip — any entry that fails. Additionally:

- Reject `ZipInfo` entries whose `external_attr` marks them as **symlinks**; a symlink entry followed by a write through it escapes even a correct path check.
- Reject **duplicate** entries and **conflicting file/directory** entries.
- Handle the case where `os.path.dirname(target_file_path)` is empty (a top-level file), which currently calls `os.makedirs("")` and raises.
- Note that **`overwrite_existing` is accepted as a parameter but never consulted in this loop** — restoration overwrites unconditionally, contradicting the `--overwrite` flag's documented semantics.

**Longer term, backups should carry:** per-entry checksums, a signed manifest, an explicit format version, restore verification, and optional encryption. Property-based tests should assert the invariant *"no archive entry, however constructed, can produce a write outside the destination root."*

## F-10 / F-14 — Blind Exception Handling as a Design Pattern 🟠 HIGH

**199 `except Exception` blocks** across 19,565 lines. `ruff` flags **161** as `BLE001` blind-except. Two are `except Exception: pass` (`utils/completion.py:167` and `:188`, both flagged `S110` by bandit as well) — and those two are precisely what makes F-01's sibling defects invisible.

The single worst instance is `cli.py:114–129`:

```python
try:
    from .cli.backup import register_backup_commands
    from .cli.config import register_config_commands
    from .cli.contributions import register_contributions_commands
    from .cli.core import register_core_commands
    from .cli.github import register_github_commands
    from .cli.upstream import register_upstream_commands

    register_core_commands(main)
    register_config_commands(main)
    register_upstream_commands(main)
    register_github_commands(main)
    register_contributions_commands(main)
    register_backup_commands(main)

except ImportError as e:
    console.print(f"[red]Warning: Could not load all command modules: {e}[/red]")
    console.print("[yellow]Some commands may not be available.[/yellow]")
```

**Observed behavior when triggered:** the CLI starts successfully with **zero commands registered** and **exit code 0**, printing a yellow warning that a scripted consumer will never see. A tool that explicitly advertises "Quiet mode … for CI/CD integration" and **exits 0 while doing nothing** is strictly worse than one that crashes. This pattern actively conceals F-01, F-03, and F-06 from any automation consuming GitCo.

Note also that this handler catches `ImportError` specifically — but F-03's phantom classes surface at *call* time, not import time, so this handler does not even cover the failure mode it appears designed for. It only masks the registration half.

**The fix.**

1. **Delete the `try/except` entirely.** A missing command module is a broken install; it must be a hard, loud, non-zero failure.
2. Enable `BLE001` in `ruff` configuration. Ratchet the 161 occurrences down: every `except Exception` must either re-raise a typed `GitCoError` from the existing 17-exception hierarchy in `utils/exception.py`, or carry an inline comment justifying why swallowing is correct.
3. Fix `TRY400` (48 occurrences) — use `logger.exception(...)` inside `except` blocks so stack traces survive.
4. Establish the rule: **the only acceptable blanket handler is the outermost CLI boundary, which logs the traceback and exits non-zero with a machine-readable code.**

## F-15 — `.git` Assumed to Be a Directory; Valid Worktrees Rejected 🟠 HIGH

`src/gitco/libs/git_ops.py:890–906`:

```python
def is_git_repository(self) -> bool:
    try:
        git_dir = self.path / ".git"
        if not git_dir.exists() or not git_dir.is_dir():
            return False
        result = self._run_git_command(["status"], capture_output=True)
        return result.returncode == 0
    except Exception as e:
        ...
        return False
```

**In a linked Git worktree, `.git` is a *file* containing a `gitdir:` pointer, not a directory.** `is_dir()` returns `False`, and GitCo declares a perfectly valid repository invalid — before it ever asks Git.

The same filesystem-inference error appears at three more sites:

```python
git_ops.py:206   cmd.extend(["--git-dir", os.path.join(repo_path, ".git")])
git_ops.py:226   if not os.path.exists(os.path.join(repo_path, ".git")):
git_ops.py:2531  if ".git" in dirs:                    # repository auto-detection walk
```

Each breaks on worktrees, and `--git-dir` construction additionally breaks on submodules (where `.git` is also a file), on repositories with `GIT_DIR` set, and on bare repositories.

**The correct design: never infer Git internals from filesystem layout. Ask Git.**

```bash
git -C "$repo" rev-parse --is-inside-work-tree      # is this a work tree at all?
git -C "$repo" rev-parse --git-dir                  # where is the git dir for THIS worktree?
git -C "$repo" rev-parse --git-common-dir           # where is the shared git dir?
git -C "$repo" rev-parse --show-toplevel            # where is the work-tree root?
```

**This should be more than a bug fix — it should become a flagship capability.** Worktrees are a nearly perfect mechanism for parallel OSS contribution work: they let a contributor work an issue without disturbing the branch they are currently on. A future `gitco contribute owner/repo#1234` should provision:

```
~/.gitco/worktrees/owner/repo/issue-1234/
```

automatically, leaving the user's current checkout untouched. Turning the current defect into the differentiator is one of the highest-leverage moves available.

## F-16 — Prompt Injection Is an Unaddressed First-Class Threat 🟠 HIGH

GitCo's entire value proposition is feeding **untrusted, attacker-controlled upstream content** — diffs, commit messages, issue bodies, PR comments, READMEs, `CONTRIBUTING.md` — into an LLM. `prompts/templates.py` interpolates this content into prompts; `libs/analyzer.py` sends it to OpenAI.

**There is currently no delimiting of untrusted content, no instruction-hierarchy hardening, no output validation, and no redaction.**

The concrete attack: a malicious upstream commit contains text engineered to manipulate the analysis output — causing a genuine breaking change to be reported as safe, **in a tool whose sole purpose is to warn users about breaking changes.** Or, once contribution automation exists, causing the model to emit instructions that a downstream agent executes.

**The governing rule must be architectural, not advisory:**

```
Repository content  →  DATA
Repository content  →  NEVER system authority
```

**Required controls:**

- Delimit untrusted content unambiguously (fenced, tagged, length-capped) and instruct the model explicitly to treat everything inside as inert data.
- **Validate structured output against a schema** (Pydantic) and reject-and-retry on non-conformance, rather than falling back to the 144-line `_parse_text_response` regex heuristic parser.
- **No LLM output may ever drive a Git mutation** (merge, push, branch delete, PR open) without a deterministic check and an explicit human confirmation.
- **No LLM → shell execution path**, ever. Explicit tool schemas, command allowlists, `argv` execution rather than shell interpolation, working-directory restrictions, path normalization.
- **Secret-scan and redact before every outbound LLM call.** Show the user what will be sent:
  ```
  This request will send:
    - 312 lines of upstream diff
    - repository name
    - affected file paths
  Provider: OpenAI
  Potential secrets: none detected
  Continue? [y/N]
  ```
- Command provenance, dry-run rendering, and an audit log for every mutation.
- **Never automatically execute repository-provided setup commands.** A contribution planner may *read* `CONTRIBUTING.md`; it must never auto-run `curl ... | sh`, `npm postinstall`, or `make bootstrap` without explicit policy, confirmation, and isolation. Long term, offer `host` / `container` / `devcontainer` / `sandbox` execution modes.
- Beware **Git hooks and malicious submodules** — operating on untrusted repositories can execute code through hook configuration and submodule URLs.

One point in GitCo's favor: **its current Git command execution does not use `shell=True`**, which is directionally correct and should be preserved as an invariant.

## Authentication Is Too Clever (contributing cause of F-07 and F-08)

The README claims:

> "GitHub authentication is automatic using your existing Git credentials!"

Internally, `GitAuthDetector` (in `git_ops.py`, 11 public methods) inspects SSH agents, looks for SSH key files, invokes Git credential helpers, parses credential output, recognizes token prefixes, reads Git environment variables, and distinguishes SSH/basic/token modes. It is inventive. **Authentication is precisely the domain where cleverness reduces reliability** — and here it produced F-07's credential leak and F-08's category error.

**Better UX — a short, explicit, documented precedence chain:**

```
1. GH_TOKEN / GITHUB_TOKEN environment variable
2. `gh auth token`  (the GitHub CLI's own documented mechanism for exposing the active token)
3. an explicitly configured fine-grained PAT
4. a GitHub App installation token, where appropriate
5. unauthenticated read-only mode, clearly announced
```

Users who already use the GitHub CLI should not need GitCo to reverse-engineer their credential state. And the two concerns must stay separated:

```
SSH            → Git transport (clone, fetch, push)
Token / App    → REST / GraphQL API authentication
```

Also required: **minimal token permissions documented explicitly**, GitHub App support as an alternative to personal tokens, and clear, documented handling of private repositories.

## Other Security Observations

| Issue | Location | Severity |
|---|---|---|
| `subprocess.run([editor, str(config_path)])` — `$EDITOR` taken from the environment, no validation, no `check=` | `cli/config.py:232` | Low |
| **7 `subprocess.run` call sites, zero with `check=True`** (`PLW1510`) — non-zero exits silently ignored | `git_ops.py`, `github_client.py`, `cli/config.py` | Low–Medium |
| 3× `S607` start-process-with-partial-path — relies on `$PATH` resolution of `git` and `curl` | `git_ops.py:115,150,329` | Low |
| 2× `except Exception: pass` (`S110`) — swallows everything, including F-01's siblings | `utils/completion.py:167,188` | Low |
| 2× `random.uniform` for retry jitter (`S311`) | `utils/retry.py:103,266` | Informational — acceptable; add `# nosec` with rationale |
| 17× blanket `# type: ignore` with no error code (`PGH003`) suppressing a type checker that is never run | various | Low |
| No threat model, no data-flow diagram, no documented trust boundaries | — | Medium |
| No explicit disclosure of what leaves the machine and reaches OpenAI | — | Medium |
| No guaranteed offline mode; no optional pre-LLM redaction | — | Medium |
| No locking against concurrent runs on the same repository | — | Medium |
| No documented retention or deletion behavior for reports, exports, logs, and backups | — | Low |

## F-23 — `SECURITY.md` Is Unedited Boilerplate Making a False Claim

```markdown
## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported |
| 1.0.x   | ✅        |
| 0.1.x   | ✅        |
| < 0.1   | ❌        |
```

The instructional placeholder sentence from GitHub's template was never removed. More seriously, **the table claims `1.0.x` is supported. There is no `1.0.x`. There are no releases at all.** A security policy that misstates its own supported version set is a liability, not an asset — it tells a would-be reporter that the maintainer has not read their own security policy.

## F-24 — `.github/security/config.yml` Is Read by Nothing

A **240-line** YAML file declares token-rotation policy, 29 enumerated bandit rule IDs, severity thresholds, package-size limits, forbidden file patterns, alerting thresholds, notification channels (`github_issues`, `email`, `slack`), and compliance with `OWASP_TOP_10` and the `NIST_CYBERSECURITY_FRAMEWORK`.

**A repository-wide grep confirms: no workflow references it, no script parses it, no tool consumes it.** It is an inert document that *looks like* a security posture. Its existence is worse than its absence, because it creates a false impression of rigor for anyone auditing the project — including its own maintainer, since the actual gates (F-09, F-11, F-12) are broken.

**Either implement it or delete it.** Implementing it means: a real `bandit.yaml` carrying those rule IDs, CI that fails on them, `pip-audit` without `|| true`, a committed `.secrets.baseline`, and Dependabot security updates enabled.

## Security & Trust Requirements — The Bar for Asking Maintainers to Run This

Before any maintainer should be asked to point GitCo at a repository they care about, the following must exist. This is the acceptance checklist, not a wish list:

- A written **threat model** and **data-flow diagram** (`docs/security/threat-model.md`), enumerating at minimum: malicious repository, malicious issue text, malicious PR comment, prompt injection, credential theft, archive traversal, symlink attacks, command injection, unsafe Git hooks, malicious submodules, dependency compromise, AI data exfiltration, LLM-generated destructive instructions, and compromised GitCo release.
- **Explicit disclosure of exactly what is sent to OpenAI** (or any provider), per command.
- A **guaranteed offline mode** that is tested, not aspirational.
- **Optional redaction before LLM calls**, on by default for anything resembling a credential.
- **No secrets in prompts, logs, exports, or backups** — asserted by test.
- **Minimal GitHub token permissions**, documented per command.
- **GitHub App support** as an alternative to personal access tokens.
- **No automatic writes by default.**
- **A `--dry-run` on every mutating command.**
- **Transaction-like rollback behavior.**
- **Idempotency guarantees**, asserted by test.
- **Locking against concurrent runs.**
- **Signed releases or Trusted Publishing.**
- **Dependency scanning and CI actions pinned to commit SHAs.**
- **Reproducible analysis** where the underlying operation is deterministic.
- **Machine-readable exit codes.**
- **Audit logs for every mutation.**
- **Clear handling of private repositories.**
- **Explicit retention and deletion behavior for reports.**

> **Do not say "safe" without explaining what safety means.**

---

# PART 4 — ARCHITECTURE

## 4.1 The Layering Is Sound; The Contract Between Layers Is Absent

The intended architecture is good and should be kept:

```
cli.py                       → global options, logging setup, group registration
cli/{core,config,github,
     contributions,backup,
     upstream}.py            → Click command definitions, presentation
libs/{git_ops,github_client,
      analyzer,detector,
      discovery,health_metrics,
      contribution_tracker,
      backup,exporter,
      activity_dashboard,
      config}.py             → domain logic
utils/{common,logging,retry,
       rate_limiter,exception,
       prompts,completion}.py → cross-cutting concerns
patterns/constants.py        → detection heuristics
prompts/templates.py         → LLM prompt templates
templates/shell_completion.py → generated shell integration
```

Separating command definitions from domain logic is correct. Isolating prompts from the analyzer is correct — it makes prompts reviewable and swappable. Centralizing detection heuristics in one file is correct.

**What is missing is a contract.** Nothing — no `Protocol`, no ABC, no type checker, no test — pins the interface between `cli/` and `libs/`. The layering is a *convention*, and **conventions are exactly what a 6,000-line refactor destroys silently.** F-03 is the direct consequence.

**Recommendation.** Define `libs/protocols.py` with `typing.Protocol` classes for each service, have the CLI depend only on those, and run `mypy --strict` in CI:

```python
class SyncService(Protocol):
    def sync_one(self, repo: Repository, *, stash: bool, force: bool) -> SyncResult: ...
    def sync_many(self, repos: Sequence[Repository], *, max_workers: int) -> list[SyncResult]: ...

class AnalysisService(Protocol):
    def analyze(self, repo: Repository, *, max_commits: int, use_llm: bool) -> ChangeAnalysis: ...

class DiscoveryService(Protocol):
    def recommend(self, *, skills: Sequence[str], labels: Sequence[str],
                  limit: int) -> list[IssueRecommendation]: ...

class HealthService(Protocol):
    def health(self, repo: Repository) -> RepositoryHealthMetrics: ...
```

**This makes the entire F-03 class a compile-time error rather than a runtime surprise discovered a year later.**

## 4.2 `git_ops.py` Is 3,178 Lines Holding Four Unrelated Responsibilities

`libs/git_ops.py` (109 KB, 16% of all source) contains:

| Concern | Symbols | Lines |
|---|---|---|
| Auth detection | `GitAuthInfo`, `GitAuthDetector`, `get_auth_detector`, `detect_github_auth`, `test_github_auth` | 56–~360 |
| Batch orchestration | `BatchResult`, `BatchPerformanceMetrics`, `BatchProcessor` | ~360–873 |
| Single-repo git operations | `GitRepository` (32 methods) | 873–2167 |
| Multi-repo management | `GitRepositoryManager` (33 public methods) | 2168–3178 |

**Auth detection does not belong in git operations** — it is consumed by `github_client.py`, creating a circular conceptual dependency. **Batch/parallelism is orchestration, not git.** `BatchProcessor` sizes its worker pool from `psutil.virtual_memory()` and `psutil.cpu_count()` — thoughtful, but wholly unrelated to Git.

**Split into `git_ops.py` / `git_auth.py` / `batch.py`.** This is not an aesthetic preference: **a 3,178-line file is the single strongest predictor of the class of drift that produced F-03**, because no reviewer holds it in their head, and because a file that large produces enormous merge conflicts, poor test isolation, unclear ownership, hidden coupling, complex mocking, and a hostile onboarding experience.

`analyzer.py` (1,183), `github_client.py` (1,275), `contribution_tracker.py` (1,034), `config.py` (968), `cli/core.py` (965), and `discovery.py` (884) have the same problem in lesser degree. **The repository is modular at the filename level; several files are effectively mini-applications.**

## 4.3 Three Parallel HTTP Stacks

`libs/github_client.py` reaches GitHub via **three different mechanisms**:

1. **`requests`** — declared, imported across 4 files (`retry.py`, `git_ops.py`, `github_client.py`, `analyzer.py`), used with a retry-configured `Session`
2. **`PyGithub`** — `from github import Github` at line 10; constructed at four call sites (lines 578, 582, 588, 592)
3. **Shelling out to `curl` via `subprocess.run`** — `SSHGitHubClient._make_ssh_request`, with hand-rolled response parsing

This triples the surface area for auth bugs, proxy bugs, TLS bugs, timeout bugs, and rate-limit bugs, and it is the direct cause of both F-07 (credential leak) and F-08 (broken parser).

**Pick one.** The right answer is a single thin `GitHubTransport` class over `httpx` or `requests`. `PyGithub` is a heavyweight ORM-style wrapper being used for a handful of calls; drop it. `curl` must go entirely.

## 4.4 Dead Dependencies

| Dependency | Declared | Actually imported | Verdict |
|---|---|---|---|
| `click>=8.0.0` | ✅ | ✅ | Keep |
| `pyyaml>=6.0` | ✅ | ✅ | Keep |
| **`gitpython>=3.1.0`** | ✅ | ❌ **never** (`import git` appears nowhere) | **Remove** |
| `requests>=2.28.0` | ✅ | ✅ (4 files) | Keep — consolidate on it |
| `rich>=13.0.0` | ✅ | ✅ | Keep |
| `openai>=1.0.0` | ✅ | ✅ | Keep — but make optional |
| **`tiktoken>=0.5.0`** | ✅ | ❌ **never** | **Remove** |
| `pygithub>=1.59.0` | ✅ | ✅ (1 import, 4 constructions) | **Remove** — consolidate on `requests` |
| `psutil>=5.9.0` | ✅ | ✅ (worker-pool sizing) | Keep or make optional |
| `jinja2>=3.0.0` | ✅ | ✅ (prompt templating) | Keep |
| `urllib3>=1.26.0` | ✅ | ✅ (`Retry` in `utils/retry.py`) | Keep — transitively implied by `requests` |

`tiktoken` is a compiled Rust extension that pulls `regex`; `gitpython` pulls `gitdb` and `smmap`. **Removing both cuts install size and wheel-availability risk for zero functional loss.** The presence of `gitpython` alongside a codebase that shells out to `git` via `subprocess` throughout indicates it was declared aspirationally and never adopted — and `tiktoken` is a fossil of the removed cost-tracking feature (`d15a823`).

Note also that `requirements.txt` and `pyproject.toml` declare the same set with **divergent version floors** (`jinja2>=3.1.0` vs `jinja2>=3.0.0`). One of the two must become the single source of truth.

## 4.5 Silent Degradation as a Design Pattern

Covered in F-14. Restated architecturally: **GitCo systematically converts defects into shrugs.** 199 `except Exception` blocks, an `except ImportError` that yields exit code 0 with no commands, two `except Exception: pass` bodies hiding broken imports, nine `|| true` security gates, and a `try/except` around every subprocess result whose return code is never checked. The cumulative effect is a program **architecturally incapable of telling anyone that it is broken** — which is exactly the state it has been in for eleven months.

## 4.6 Configuration Design

`Config` is a clean dataclass tree — `Config` → `Optional[list[Repository]]` + `Settings` — with `Repository` carrying 8 fields and `Settings` carrying **23 flat fields**. The typing and defaults are sensible. Three problems:

1. **The path violates the XDG Base Directory specification.** `libs/config.py:597` hardcodes `~/.gitco/config.yml`. It should be `${XDG_CONFIG_HOME:-~/.config}/gitco/config.yml`, with a one-time migration shim for the legacy location. Notably, `docs/QA.md` **already documents the XDG path** (`~/.config/gitco/config.yaml`) while the code uses the dotfile path — a documentation/implementation split that is itself proof `QA.md` was never executed.

2. **`Settings` has 23 flat fields** spanning five unrelated concerns:
   ```
   LLM:          llm_provider · llm_openai_api_url · max_tokens_per_request · analysis_enabled
   GitHub API:   github_api_url · github_timeout · github_max_retries · github_use_git_auth
                 github_token_env · github_username_env · github_password_env
   Rate limits:  github_rate_limit_per_minute · github_rate_limit_per_hour · github_burst_limit
                 llm_rate_limit_per_minute · llm_rate_limit_per_hour · llm_burst_limit
                 min_request_interval · rate_limit_delay
   Git:          default_path · git_timeout · max_repos_per_batch
   Logging:      log_level
   ```
   **Nest them** (`settings.github.*`, `settings.llm.*`, `settings.rate_limits.*`, `settings.git.*`, `settings.logging.*`) **before the surface hardens.** With zero users, this costs nothing today and becomes a breaking migration the moment someone installs it.

3. **Configuration is being asked to hold operational state.** See §4.8.

## 4.7 Manual YAML Onboarding Is the Wrong Primary Path

The README requires the user to hand-author `~/.gitco/config.yml`:

```yaml
repositories:
  - name: django
    fork: username/django
    upstream: django/django
    local_path: ~/code/django
    skills: [python, web, orm]
```

**This should be advanced configuration, not the onboarding path.** GitCo has — or can obtain — everything in that block automatically. The primary path should be:

```bash
gitco init --from-github
```

which discovers: repositories owned by the authenticated user that are forks; their upstream parents; local clones on disk; configured remotes; default branches; divergence; active PRs; abandoned branches; dirty state; unpushed work. Manual `skills` configuration should likewise become optional enrichment on top of an **inferred contributor skill graph** (§8.3), not the required source of truth.

## 4.8 Introduce SQLite for Operational State

A mature GitCo should not repeatedly recompute or refetch everything. Introduce a local database at the platform-appropriate application-data location (e.g. `~/.local/share/gitco/gitco.db`) holding:

```
repositories · upstream mappings · GitHub repository metadata · issues · PRs
contribution history · recommendation outcomes · cached health metrics
ETags · API timestamps · skill graph · embeddings · sync operations
backup records · agent runs · audit trail
```

**The distinction that matters:**

```
config.toml / config.yml  =  user intent          (human-editable, version-controllable)
SQLite                    =  application state    (machine-owned, never hand-edited)
Git                       =  repository truth
Forge API                 =  remote truth
```

Configuration should remain human-editable. Operational state should not live in it.

## 4.9 Build a Transaction Journal for Git Operations

Backup is useful, but mature Git tooling should know **exactly what it changed**. Before every mutation, record and display:

```
Transaction #89

Repository:     ~/src/django
HEAD            3e21b51
Branch          feature/foo
Dirty files     3
Stash           none
origin/main     6ac8231
upstream/main   8ff8137

Planned:
  stash working tree
  fetch upstream
  merge upstream/main
  restore stash
```

After:

```
Result: SUCCESS
New HEAD        8ff8137
Created stash   gitco/txn-89
Restored        yes
Conflicts       none
```

Then:

```bash
gitco undo 89
```

wherever semantically possible. **This is substantially more useful than a generic ZIP backup alone**, and the primitives already exist — `GitRepositoryManager` has `safe_stash_changes`, `restore_stash`, `drop_stash`, `abort_merge`, `resolve_conflicts`, and `get_merge_status`.

## 4.10 Build Ports and Adapters Before Adding a Second Forge

GitCo will eventually benefit from GitLab, Forgejo, Gitea, and possibly Bitbucket support. **Do not implement each directly across existing classes.** First define domain ports:

```python
class Forge(Protocol):
    def repository(self, full_name: str) -> ForgeRepository: ...
    def issues(self, full_name: str, **filters: Any) -> list[ForgeIssue]: ...
    def pull_requests(self, full_name: str, **filters: Any) -> list[ForgePullRequest]: ...
    def user_contributions(self, username: str) -> list[Contribution]: ...
    def comments(self, full_name: str, number: int) -> list[Comment]: ...
    def rate_limit(self) -> RateLimitStatus: ...

class GitBackend(Protocol):
    def status(self, path: Path) -> RepositoryStatus: ...
    def fetch(self, path: Path, remote: str) -> FetchResult: ...
    def merge(self, path: Path, ref: str, *, strategy: str) -> MergeResult: ...
    def worktree(self, path: Path, ref: str, target: Path) -> WorktreeResult: ...
    def diff(self, path: Path, a: str, b: str) -> Diff: ...
```

GitHub then becomes **one adapter**, and `github_client.py` becomes `forge/github/`. This prevents GitHub-specific assumptions from becoming permanent architecture. OSS maintainers are actively migrating off GitHub; a fork tool that only speaks GitHub has a hard ceiling.

## 4.11 Target Architecture

```
src/gitco/
├── domain/                  # pure data types, no I/O
│   ├── repository.py
│   ├── contribution.py
│   ├── issue.py
│   ├── change.py
│   └── health.py
│
├── application/             # orchestration; depends only on Protocols
│   ├── sync_service.py
│   ├── analysis_service.py
│   ├── discovery_service.py
│   ├── contribution_service.py
│   └── portfolio_service.py
│
├── git/                     # the split of today's git_ops.py
│   ├── command.py           # single argv-based subprocess boundary, check=True
│   ├── repository.py
│   ├── worktree.py
│   ├── remote.py
│   ├── status.py
│   ├── sync.py
│   ├── conflict.py
│   └── transaction.py       # the journal from §4.9
│
├── forge/
│   ├── base.py              # the Forge Protocol
│   ├── github/
│   │   ├── client.py
│   │   ├── auth.py
│   │   ├── issues.py
│   │   ├── pulls.py
│   │   └── graphql.py
│   └── gitlab/
│
├── intelligence/
│   ├── providers/           # openai · anthropic · gemini · ollama · llama.cpp · none
│   ├── change_analysis/
│   ├── issue_analysis/
│   ├── matching/
│   └── embeddings/
│
├── scoring/
│   ├── issue_fit.py
│   ├── maintainer.py
│   ├── repository.py
│   └── contribution.py
│
├── storage/
│   ├── sqlite.py
│   ├── migrations/
│   └── cache.py
│
├── security/
│   ├── secrets.py
│   ├── redaction.py
│   └── prompt_security.py
│
├── cli/                     # thin: parse → call service → render
├── render/                  # all Rich presentation, testable on result objects
└── tui/
```

**Eventual package topology** — not necessarily separate repositories, but separate boundaries, so third parties can use the engine without shelling out:

```
gitco-core · gitco-cli · gitco-mcp · gitco-gh-extension · gitco-tui
```

---

# PART 5 — CODE QUALITY & ENGINEERING PRACTICE

## 5.1 Static Analysis — What `ruff --select ALL` Actually Reports

The project configures `ruff` with 7 rule families (`E`, `W`, `F`, `I`, `B`, `C4`, `UP`) and ignores `E501`, `B008`, and `C901`. **Under that configuration, `ruff check src/` reports "All checks passed!"** Under the full ruleset it reports **2,874 violations**. The gap between those two numbers is the measure of what the current lint configuration is not looking at.

| Count | Rule | Meaning | Verdict |
|---|---|---|---|
| **461** | `COM812` | missing trailing comma | Cosmetic; `ruff format` fixes all |
| **354** | `D413` | missing blank line after last docstring section | Cosmetic |
| **340** | `FA100` | missing `from __future__ import annotations` | Real for a `py39` target |
| **202** | `G004` | f-string in logging call | **Real** — breaks structured logging, log aggregation, and lazy formatting |
| **176** | `TID252` | relative imports | Stylistic — but note F-01 and F-03 are *absolute*-import bugs |
| **161** | `BLE001` | blind `except` | **Real** — the defect-concealment engine (F-14) |
| **100** | `FBT001` | boolean positional argument in signature | Real API-design smell |
| **93** | `PLR2004` | magic value in comparison | Real |
| **90** | `E501` | line too long | Ignored by config; `black` handles most |
| **66** | `TRY003` | long message in `raise` | Minor |
| **54** | `PLC0415` | import not at top of file | **Directly enabled F-03** |
| **48** | `TRY400` | `logging.error` where `.exception` belongs | **Real** — loses stack traces |
| **46** | `EM102` | f-string in exception constructor | Minor |
| **45** | `TRY300` | `try` should use `else` | Minor |
| **39** | `FBT002` | boolean default in positional argument | Real |
| **34** | `PTH123` | `open()` instead of `Path.open()` | Minor |
| **32** | `ANN401` | `Any` in annotation | Real for a typed package |
| **31** | `ANN204` | missing return type on special method | Real |
| **31** | `PLR0913` | too many arguments | Real |
| **31** | `PLR0917` | too many positional arguments | Real |
| **25** | `C901` | complex structure | Ignored by config |
| **23** | `DTZ005` | naive `datetime.now()` | **Real** — timestamps in exports and backups are timezone-ambiguous |
| **22** | `ARG001` | unused function argument | Real (includes `overwrite_existing` in F-13) |
| **19** | `PTH110` | `os.path.exists` instead of `Path.exists` | Minor |
| **18** | `ANN201` | missing return annotation on public function | Real |
| **17** | `PGH003` | blanket `# type: ignore` | **Real** — suppressing a checker that is never run |
| **16** | `PIE790` | unnecessary placeholder (`pass`) | Minor |
| **10** | `PLW0603` | `global` statement | Real — global mutable state in `utils/common.py` and `rate_limiter.py` |
| **9** | `PLR0912` | too many branches | Real |
| **7** | `PLW1510` | `subprocess.run` without `check` | **Real** |
| **7** | `A002` | builtin argument shadowing | Minor |
| **6** | `T201` | bare `print()` | Inconsistent with the Rich console abstraction |
| **6** | `SLF001` | private-member access across modules | Real encapsulation break |
| **5** | `S603` | subprocess without `shell=True` check | Informational — the absence of `shell=True` is correct |
| **3** | `S607` | start process with partial path | Low |
| **2** | `S110` | `try`/`except`/`pass` | **Real** — hides F-01's siblings |
| **2** | `S311` | non-cryptographic random | Informational — acceptable for jitter |
| **1** | `PLE0604` | invalid object in `__all__` (starred splat) | **Real** — `utils/__init__.py` |
| **1** | `N818` | exception name not suffixed `Error` | Minor |

**The 54 `PLC0415` violations deserve special emphasis.** Ten of them **are** F-03. Moving those imports to module top level would have converted every phantom-class bug into an immediate, unmissable `ImportError` on first import — a bug that gets fixed in the same session it is written, instead of one that lives at the tip of `main` for a year.

**`bandit`:** 17 Low, 1 Medium, 0 High across 15,421 counted lines of code. Clean — but see F-07 for what `bandit` structurally cannot catch.

## 5.2 The Typing Claim Is False

`pyproject.toml` declares:

```toml
classifiers = [ ..., "Typing :: Typed" ]
```

**There is no `py.typed` marker file anywhere in the repository.** Per PEP 561, without `py.typed` inside the package directory, **downstream consumers get zero type information** regardless of how many annotations the source contains. The classifier is a false advertisement. Compounding it, `[tool.setuptools.package-data]` declares `gitco = []`, so even if the file were added it would not be packaged without also updating that entry, and `MANIFEST.in` ships `recursive-include src *.pyi` for `.pyi` stubs that do not exist.

Worse: **`mypy` appears nowhere.** Not in `pyproject.toml`, not in `requirements-dev.txt`, not in `.pre-commit-config.yaml`, not in any workflow — a repository-wide grep returns zero matches. Yet the source carries **17 blanket `# type: ignore` comments** suppressing errors from a type checker that is never run, alongside 340 `FA100`, 32 `ANN401`, 31 `ANN204`, and 18 `ANN201`.

**This is the single highest-leverage tooling gap in the project.** `mypy` at default settings, run once, would have found **every one of the seventeen broken imports in F-03 in under two seconds.** The tool that would have prevented the catastrophe was never installed.

## 5.3 Formatting Toolchain Is a Generation Behind

`.pre-commit-config.yaml` pins:

| Hook | Pinned version | Status |
|---|---|---|
| `ruff-pre-commit` | v0.12.5 | Current-ish |
| `black` | **23.12.1** | ~2.5 years stale |
| `commitizen` | v3.13.0 | Stale |
| `mirrors-prettier` | v3.1.0 | **The `mirrors-prettier` repo is archived/deprecated upstream** |
| `pre-commit-hooks` | v4.5.0 | Stale |
| `yamllint` | v1.35.1 | Current |

And `ruff-format` is explicitly commented out with `# Disabled to avoid conflicts with black`.

**Recommendation.** Drop `black` entirely and use `ruff format` — a `black`-compatible formatter, dramatically faster, one tool instead of two, and no version-skew conflict to design around. Replace `mirrors-prettier` with a maintained YAML formatter, or drop it in favor of `yamllint` alone, which is already present. Bump every remaining hook.

**Also: `.pre-commit-config.yaml` is not enforced in CI.** `pre-commit run --all-files` appears in no workflow, so the hooks apply only to contributors who remembered to run `pre-commit install` locally. A pre-commit configuration that CI does not verify is a suggestion, not a standard.

## 5.4 Function Length & Complexity

Measured by AST over the whole tree:

```
164 lines  cli/contributions.py:stats
158 lines  cli/core.py:init
150 lines  libs/github_client.py:get_issues
144 lines  libs/analyzer.py:_parse_text_response
139 lines  libs/discovery.py:print_issue_recommendation
119 lines  prompts/templates.py:get_analysis_prompt
119 lines  cli/core.py:status
118 lines  cli/github.py:get_issues_multi
112 lines  libs/exporter.py:export_contribution_data_to_csv
108 lines  libs/github_client.py:_make_ssh_request
108 lines  cli/config.py:validate
105 lines  libs/analyzer.py:analyze_changes_without_llm
```

`C901` complexity is explicitly **ignored** in `pyproject.toml`; **25 functions would fail it**, and 9 exceed the branch limit (`PLR0912`), 3 the statement limit (`PLR0915`), 5 the return-statement limit (`PLR0911`).

A 164-line Click callback that mixes config loading, data fetching, aggregation, and Rich rendering is **untestable by construction** — you cannot assert on it without capturing stdout.

**The rule to adopt: every CLI callback ≤ 30 lines — parse args → call one service function → render.** The service function is what gets tested. All rendering moves into a `render/` module that takes a result object and returns a renderable, so presentation becomes independently testable and independently replaceable (text, JSON, CSV, TUI).

## 5.5 Dead Code & Missing Signposts

- **`src/gitco/cli.py` — 138 lines, permanently unreachable** (F-02).
- **`SSHGitHubClient` + `create_ssh_github_client` — ~350 lines, constructed by nothing** (F-08).
- **`libs/exporter.py`'s `DataExporter`** — re-exported from a module containing no classes (F-03).
- **25 bare `pass` statement bodies**; 16 flagged `PIE790`.
- **Zero `TODO` / `FIXME` / `XXX` / `HACK` comments in 19,565 lines.** In a codebase with this many known gaps, zero TODOs is not a sign of completeness — it is a sign that gaps were never acknowledged in code. It also removes the primary signal a new contributor uses to find a starting point.
- **`CONTRIBUTING.md` contains zero mentions of tests or how to run them** — a 7.7 KB contributor guide with no testing section, in a repository with no tests.
- **Version constant is defined twice** — `gitco/__init__.py:5` and `gitco/libs/__init__.py:5` both declare `__version__ = "0.1.0"`, along with duplicated `__author__`, `__email__`, `__license__`, and `__url__`. `pyproject.toml` reads `{attr = "gitco.__version__"}`. Drift is a matter of time.
- **`utils/__init__.py` builds `__all__` by splatting submodule `__all__` lists** (`*common.__all__, *exception.__all__, ...`), which `ruff` flags `PLE0604` because it cannot be statically verified — and which silently omits `rate_limiter` and `completion` while importing the former.

## 5.6 Release Engineering Is Configured but Has Never Run

- **0 git tags.** `release.yml` and `pypi-publish.yml` trigger only on `push: tags: v*`. **Neither has ever executed.** Several hundred lines of release automation are entirely unverified.
- `CHANGELOG.md` exists (3.4 KB) with `.conventional-changelog.json` configuration, but no release corresponds to it.
- **`release.yml:206` uses `actions/create-release@v1`, archived and deprecated by GitHub since 2021.** Replace with `softprops/action-gh-release` or `gh release create`.
- **PyPI publishing uses a long-lived `PYPI_API_TOKEN` secret** (`TWINE_USERNAME=__token__`, `TWINE_PASSWORD=${{ secrets.PYPI_API_TOKEN }}`). The current standard is **PyPI Trusted Publishing (OIDC)** — no stored secret, short-lived credentials, and automatic publish attestations. The workflow lacks `id-token: write` permissions and does not use a GitHub Environment with required reviewers.
- **No build provenance, no SBOM, no SLSA attestation, no sigstore signing, no artifact checksums, no lockfile.**
- **GitHub Actions are pinned to floating tags, not commit SHAs.**
- **Dependabot `reviewers`/`assignees` are set to `41technologies`** while the repository lives under `smusali` — reviewer assignment will fail or misroute.
- **Two overlapping release pipelines.** `release.yml` and `pypi-publish.yml` duplicate build, validation, security scanning, and publishing logic. Consolidate to one secure path.
- **The release automation is dramatically overengineered relative to product readiness.** The correct priority hierarchy is:
  ```
  correctness → tests → safety → product value → adoption → release sophistication
  ```
  The current ordering is inverted.

## 5.7 The Missing Test Architecture

Zero tests exist. Restoring the 16,570 deleted lines from `git show cad42cf^:tests/...` recovers weeks of already-paid-for work, but the suite must go further than what was deleted, because **a Git-mutating tool needs extraordinary confidence in exactly the operations that were never tested.**

### The standard

> **If GitCo says it will preserve a repository state, there should be an automated test reproducing that state and proving it.**

### Required integration fixtures

Programmatically generate temporary repositories covering every one of these, with explicit before/after assertions:

```
clean repository                dirty tracked files            dirty untracked files
staged changes                  unpushed commits               local branch ahead
local branch behind             diverged local/upstream        merge conflict
rebase conflict                 deleted upstream branch        renamed default branch
detached HEAD                   shallow clone                  submodules
Git LFS                         multiple remotes               missing origin
missing upstream                HTTPS origin                   SSH origin
GitHub Enterprise origin        worktree                       nested repository
symlink                         empty repository               orphan branch
path containing spaces          path containing Unicode        interrupted operation
network failure mid-fetch       rate-limit exhaustion          credential failure
```

Ship this as a reusable fixture generator so every future contributor inherits it:

```bash
python -m tests.fixtures.git_factory --dirty --diverged --submodules --conflict --worktree
```

### Required failure-injection tests

```
process killed after stash        process killed after fetch
process killed mid-backup         network timeout
GitHub 403 / 404 / 429 / 500      rate-limit exhaustion
disk full                         permission denied
corrupted ZIP                     invalid Git config
expired token                     upstream repository deleted
repository moved/renamed
```

For each, prove three things: **no work lost · state understandable · recovery actionable.**

### Required property-based tests

```
score values always remain within [0,1]
config serialize → deserialize is lossless
no archive entry, however constructed, escapes the destination root
every valid Git ref survives parse → render → parse
every operation plan is renderable
running any command twice produces the same end state (idempotence)
```

### Required unit/CLI tests

- **`tests/test_imports.py`** — import every module; instantiate the Click group; assert every expected command and subcommand is registered; assert every name in every `__all__` resolves. ~40 lines. **This one file prevents F-01, F-02, F-06, and the registration half of F-03 forever.**
- Click `CliRunner` invocation of every command against fixture repositories, asserting exit codes and JSON output shape.
- Snapshot tests over the `render/` layer.

## 5.8 The Required CI Pipeline

Every PR must gate on:

```
lint · format · typing · unit tests · integration tests · CLI tests
package build · package install-from-wheel · docs build · broken-link check
dependency-audit policy · security-scan policy · secret scan
```

At minimum:

```bash
ruff check .
ruff format --check .
mypy src/            # or pyright
pytest --cov
python -m build
twine check dist/*
```

Then install the produced wheel into a clean environment and run:

```bash
gitco --version
gitco --help
gitco doctor
```

**Matrix:** Ubuntu × all supported Python versions; macOS × primary versions; Windows × primary versions. Make it a required status check on `main`.

**Never verify a release by installing an identically-named package from PyPI until the distribution identity in F-04 is fixed** — the current `pypi-publish.yml` verify step would install and smoke-test a stranger's software and report success.

---

# PART 6 — DOCUMENTATION TRUTHFULNESS

The documentation is voluminous (17 files, ~5,252 lines), well-organized, and **substantially describes a program that does not exist.** For a project whose entire acquisition funnel is its README, this is a first-order problem.

## 6.1 Commands & Flags Documented but Absent

Extracted from `docs/QA.md` and `docs/cli/*.md`, then diffed against the live command tree obtained by introspection:

| Documented | Reality |
|---|---|
| `gitco config add-repo --name … --fork … --upstream …` | ❌ **Does not exist.** This is the *only* documented way to add a repository non-interactively. |
| `gitco config config-status` | ❌ Does not exist |
| `gitco config validate-detailed` | ❌ Does not exist (real: `config validate --detailed`) |
| `gitco config list` | ❌ Does not exist |
| `gitco backup list-backups` | ❌ Does not exist (real: `backup list`) |
| `gitco backup validate-backup` | ❌ Does not exist (real: `backup validate`) |
| `gitco upstream validate-upstream` | ❌ Does not exist (real: `upstream validate`) |
| `gitco sync --all` | ❌ Flag does not exist (real: `--batch`) |
| `gitco status --all` | ❌ Flag does not exist |
| `gitco analyze --all` | ❌ Flag does not exist (real: `--repos`) |
| `gitco activity --all` | ❌ Flag does not exist |
| `gitco discover --repo <name>` | ❌ Flag does not exist (real: `--repos`) |
| `gitco completion --shell bash` / `gitco completion bash` | ⚠️ Implementation accepts `--shell`; the positional form documented in `QA.md` is rejected with `Error: Got unexpected extra argument (bash)` |

**Verified as genuinely present** (contrary to some claims of absence): `discover --personalized`, `discover --show-history`, `discover --min-confidence`, `discover --label`, `discover --limit`, `discover --skill`, `discover --export`, `discover --quiet`.

**The full, actual flag surface** for the four headline commands:

```
sync      --repo --batch --analyze --stash --force --max-repos --max-workers
          --export --quiet --log --detailed-log --max-log-size --log-backups
status    --repo --detailed --overview --activity --filter --sort --export --quiet
analyze   --repo --repos --detailed --max-commits --model --provider --prompt
          --no-llm --export --quiet
discover  --skill --label --limit --min-confidence --personalized --show-history
          --repos --export --quiet
```

## 6.2 Contradictions Within the Documentation Set

| Claim | Source | Reality |
|---|---|---|
| Config at `~/.gitco/config.yml` | `README.md` | ✅ matches `libs/config.py:597` |
| Config at `~/.config/gitco/config.yaml` | `docs/QA.md` | ❌ contradicts both the README **and** the code |
| `pip install gitco` | `README.md` + 4 docs files | ❌ installs a different project entirely (F-04) |
| "Supported: 1.0.x" | `SECURITY.md` | ❌ no 1.0.x exists; no release exists |
| "Development Status :: 4 - Beta" | `pyproject.toml` | ❌ Beta implies it runs. `1 - Planning` or `2 - Pre-Alpha` is accurate. |
| `Typing :: Typed` | `pyproject.toml` | ❌ no `py.typed` (F-21) |
| `--repo` selects a configured repository by name | `docs/cli/upstream.md`, and the flag's own help text `"Repository name"` | ❌ every `upstream` subcommand passes it directly to `validate_repository_path()`, resolving it as a **CWD-relative filesystem path** |
| "GitHub authentication is automatic using your existing Git credentials!" | `README.md` | ⚠️ Implemented — by leaking the token to argv (F-07) |
| "Quiet mode … for CI/CD integration" | `README.md` | ⚠️ The `--quiet` global option lives in the unreachable `cli.py` (F-02) |
| Eleven documented global options | `docs/cli.md` | ❌ All eleven live in unreachable code and have never been wired |
| Repository URLs point to `41technologies/gitco` | `pyproject.toml`, `__init__.py` ×2 | ❌ canonical repo is `smusali/gitco` |
| `jinja2>=3.1.0` | `requirements.txt` | ⚠️ `pyproject.toml` says `>=3.0.0` — two sources of truth, divergent floors |

## 6.3 `docs/QA.md` — A Test Plan for an Imagined Program

Added in the **final commit** (`d71824a`), 780 lines, presented as the project's quality-assurance procedure. It:

- documents at least a dozen commands and flags that do not exist (§6.1),
- specifies a configuration path the code does not use (§6.2),
- instructs the tester to run `gitco --version` and `gitco config validate` as prerequisites — **both of which crash on the very commit that introduced this file**,
- is referenced by no workflow and gated on nothing.

**It cannot have been executed even once.** Adding a manual QA document as the last act of a project whose automated tests were deleted is the clearest possible signal of the underlying process failure: **documentation was produced in place of verification.**

## 6.4 The Meta-Pattern

Across `pyproject.toml`, `SECURITY.md`, `.github/security/config.yml`, `docs/QA.md`, and the README, the same pattern recurs: **artifacts that assert quality rather than produce it.**

```
a Typing :: Typed classifier without py.typed
a 240-line security policy that nothing reads
a Beta status on a program that does not start
a 780-line QA plan that has never been run
nine security tools, all suffixed || true
a secret-scanning gate that cannot match
a .secrets.baseline referenced by two workflows and present in neither
a CONTRIBUTING.md with no testing section, in a repo with no tests
```

This is not dishonesty — it is a specific, common, and entirely correctable failure mode in which the **artifacts** of engineering rigor are produced faster than the **substance**.

> **The single most valuable change this project can make is to invert that ratio: fewer claims, all of them mechanically enforced.**

## 6.5 Required Documentation Remediation

1. **Generate `docs/cli/*.md` from Click introspection** (`sphinx-click`, `mkdocs-click`, or a small custom generator run in CI). This makes drift **structurally impossible** rather than merely discouraged, and it is the single highest-ROI documentation change available.
2. **Delete `docs/QA.md`, or convert every step in it into an executable integration test.** A manual QA document is a liability once CI exists.
3. **Rewrite every install instruction** against the new distribution identity (F-04), across the README and all five docs files.
4. **Add a pre-alpha banner to the README** until Phase 1 exits.
5. **Write `ARCHITECTURE.md`** — a map of the layers and the Protocol boundaries. The single highest-ROI document for a new contributor.
6. **Add a testing section to `CONTRIBUTING.md`** — how to run the suite, how to add a fixture, what the coverage floor is.
7. **Restructure the docs tree** to separate reference from explanation:
   ```
   docs/
   ├── getting-started/
   ├── concepts/          portfolio · fork-debt · opportunity-score · contribution-lifecycle
   ├── guides/
   ├── cli/               ← generated, never hand-edited
   ├── integrations/
   ├── architecture/
   ├── adr/               ← architecture decision records
   ├── security/          threat-model.md · data-flow.md · redaction.md
   ├── scoring/           GITCO-SCORE-SPEC.md
   ├── evaluation/
   ├── contributing/
   └── reference/
   ```
8. **Publish Architecture Decision Records** so sophisticated external contributors can participate:
   ```
   0001-local-first.md
   0002-sqlite-state.md
   0003-provider-abstraction.md
   0004-git-transaction-model.md
   0005-no-llm-for-destructive-actions.md
   0006-ranking-evaluation.md
   0007-distribution-identity.md
   ```

## 6.6 README Rewrite Direction

The current README tells the user what GitCo does but never makes the pain visceral, and it leads with "AI-powered," which in 2026 is table stakes rather than differentiation.

**The first viewport must answer four questions:**

```
What hurts?
Why does GitCo exist?
What happens when I run it?
Why isn't `gh repo sync` enough?
```

**Opening direction:**

> **GitCo keeps your fork aligned with upstream without losing your local patch layer.** It previews upstream changes, identifies conflicts, and gives you a recoverable sync plan from the command line.

Then **one** workflow, shown end to end:

```bash
<install command>
gitco init
gitco sync --dry-run
gitco sync --apply
```

Then, explicitly and in this order: **what GitCo changes · what it never changes automatically · how to recover · what credentials it needs · whether source code leaves your machine · what is experimental.**

Then a **real terminal recording** (asciinema), not a hypothetical code block. **One compelling 30-second demo outperforms 5,252 lines of documentation.**

**Move AI analysis, contribution discovery, health metrics, and backups below the core workflow under "Optional capabilities" — or remove them from the README entirely until they are proven.**

**Add a "Why not `gh repo sync`?" table**, because the first question any informed reader asks is exactly that:

| Capability | `gh repo sync` | GitCo target |
|---|---|---|
| Sync one fork | ✅ | ✅ |
| Manage a portfolio of forks | Limited | ✅ |
| Detect fork debt | — | ✅ |
| Explain upstream changes | — | ✅ |
| Detect effect on active branches | — | ✅ |
| Rank contribution opportunities | — | ✅ |
| Developer skill graph | — | ✅ |
| Maintainer responsiveness | — | ✅ |
| Prepare an isolated contribution worktree | — | ✅ |
| Track contribution lifecycle | — | ✅ |
| Contribution inbox | — | ✅ |
| Works on private / self-hosted / air-gapped repos | ✅ | ✅ |
| Works without sending code to a third party | ✅ | ✅ |

---

# PART 7 — THE AI/INTELLIGENCE LAYER

## 7.1 The Current Implementation Is Already Obsolete in Spirit

`libs/analyzer.py` gets the abstraction right in outline — `BaseAnalyzer` (an ABC at line 64), `OpenAIAnalyzer` (line 423), `ChangeAnalyzer` (line 545) as the orchestrator — but the implementation underneath is brittle in ways that will break silently on every provider or model upgrade.

**Default model:** `gpt-3.5-turbo`, hardcoded at `analyzer.py:429` and again at `:578`.

**Output parsing:** free-form completion text scraped with regular expressions. `_parse_text_response` is **144 lines** of pattern matching, including:

```python
json_match          = re.search(r"\{.*\}", response, re.DOTALL)     # line 290
summary_match       = re.search(...)                                 # line 316
breaking_match      = re.search(...)                                 # line 325
features_match      = re.search(...)                                 # line 339
bugs_match          = re.search(...)                                 # line 353
security_match      = re.search(...)                                 # line 367
deprecations_match  = re.search(...)                                 # line 381
recommendations_match = re.search(...)                               # line 395
confidence_match    = re.search(r"Confidence:\s*(\d+\.?\d*)", ...)   # line 409
```

**The deeper problems, in order of severity:**

1. **Schema adherence is not enforced.** A model that formats its answer differently silently degrades to partial or empty results, with no error.
2. **Confidence is self-reported by the model.** `Confidence: 0.93` is a token sequence, not a calibrated probability.
3. **Model-specific behavior leaks into core logic.** The parser is coupled to one model family's formatting habits.
4. **Provider support is effectively narrow.** `cb5270c` ("rm(cost): keep OpenAI only") removed multi-provider and local-model support, leaving one vendor.
5. **Reproducibility is impossible.** No seeding, no caching, no record of what prompt produced what output.
6. **Testing requires mocking unconstrained text** rather than asserting against a schema.
7. **Provider or model upgrades can silently break the parsers** with no CI signal — and there is no CI.

## 7.2 Replace Free-Form Parsing With Typed Structured Results

Define the contract, and make the model conform to it:

```python
class Evidence(BaseModel):
    kind: Literal["commit", "diff_hunk", "release_note", "static_reference"]
    locator: str                    # e.g. "src/auth/client.py:184" or a commit SHA
    excerpt: str

class BreakingChange(BaseModel):
    symbol: str
    file: str
    line: Optional[int]
    before: str
    after: str
    evidence: list[Evidence]

class ChangeAnalysis(BaseModel):
    summary: str
    breaking_changes: list[BreakingChange]
    security_changes: list[SecurityChange]
    deprecations: list[Deprecation]
    relevant_files: list[str]
    impact: Literal["none", "low", "medium", "high", "critical"]
    recommendations: list[Recommendation]
    evidence: list[Evidence]
```

Request structured output; validate against the schema; **reject and retry on non-conformance** rather than falling back to the 144-line heuristic parser.

**The most important rule:**

> **Every model claim must point to evidence.**

A change-analysis system should never say:

```
Breaking change detected.
```

It should say:

```
Breaking change

src/auth/client.py:184
`Client.authenticate(token)` became `Client.authenticate(credentials)`

Evidence:
  upstream commit 9a81c42
  signature changed from str → Credentials

Your impact:
  branch oauth-refresh calls the old signature at src/foo.py:72
```

**That converts "AI summary" into engineering intelligence.**

## 7.3 Never Let the Model Invent Confidence

Compute confidence from **evidence quality**, not from the model's self-assessment:

```
+ AST-confirmed signature change
+ same symbol exists in the local branch
+ failing static reference found
+ upstream release note confirms the deprecation
− no migration guide found
────────────────────────────────
confidence = HIGH
```

That is a defensible number. `Confidence: 0.93` from a language model is not.

## 7.4 Make LLMs Optional, Not Foundational

GitCo must remain extremely useful with:

```bash
gitco --no-ai
```

**The division of labour must be explicit and enforced:**

| Deterministic systems own | AI adds |
|---|---|
| Git operations | Summarization |
| Branch state | Semantic classification |
| Diff calculation | Issue explanation |
| Dependency changes | Relevance reasoning |
| AST changes | Migration suggestions |
| Semantic versioning | Contribution planning |
| Issue metadata | |
| Repository metrics | |
| PR state | |
| Health checks | |
| Security scanner output | |

> **Never use an LLM to decide whether a Git operation is safe.**

`analyze_changes_without_llm` (105 lines) already exists and is a genuine differentiator over every "AI-first" competitor. **Elevate it from fallback to first-class path.**

## 7.5 Make Providers Pluggable

```python
class IntelligenceProvider(Protocol):
    async def analyze_changes(self, request: AnalysisRequest) -> ChangeAnalysis: ...
    async def explain_issue(self, issue: Issue, context: RepoContext) -> IssueExplanation: ...
    async def rank_semantic_fit(self, profile: SkillGraph,
                                candidates: Sequence[Issue]) -> list[RankedIssue]: ...
    async def build_contribution_plan(self, issue: Issue,
                                      repo: RepoContext) -> ContributionPlan: ...
```

Adapters: **OpenAI · Anthropic · Gemini · any OpenAI-compatible endpoint · Ollama · llama.cpp · LM Studio · Bedrock · Vertex · custom enterprise endpoint · a deterministic no-AI provider.**

**The `BaseAnalyzer` ABC already exists at `analyzer.py:64`. The abstraction is built; only the implementations were deleted in `cb5270c`.** Restoring multi-provider support is smaller work than it appears.

**Local models matter disproportionately here**, because GitCo's differentiated audience — maintainers of private, corporate, self-hosted, and air-gapped forks — structurally cannot send proprietary diffs to a third party. Reducing to OpenAI-only was a positioning error for a tool whose users are OSS maintainers, a population with strong and well-founded opinions about vendor lock-in.

## 7.6 Local-First as a Core Product Principle

GitCo already lives on the developer's machine. Exploit that.

**Default policy:**

```
Git metadata       local
repository source  local
contribution DB    local
embeddings         local where possible
tokens             OS keychain
telemetry          off
```

**Then show the user exactly what leaves the machine, every time:**

```
This request will send:
  - 312 lines of upstream diff
  - repository name
  - affected file paths

Provider:
  OpenAI

Potential secrets:
  none detected

Continue? [y/N]
```

Automated mode configures a policy instead of prompting. **This is a trust feature, and trust is the product.**

## 7.7 Cost, Caching, and Scope Control

- **Cache analyses by commit SHA.** The same upstream commit never needs analyzing twice.
- **Restore a lightweight cost/token preview before large analyses.** Cost tracking was removed in `d15a823`; the feature was right even if the implementation was heavy.
- **Bound what is sent.** Feed the model only the intersection computed by patch-impact analysis (§8.1), not whole diffs — an order-of-magnitude token reduction and a precision increase simultaneously.
- **Make prompts visible.** `--show-prompt` should print exactly what would be sent.

## 7.8 Integrate Coding Agents; Do Not Become One

GitCo should not try to become another generic coding agent. The correct division:

```
GitCo decides WHAT contribution is suitable
GitCo establishes repository CONTEXT
GitCo establishes a SAFE workspace
GitCo supplies CONTRIBUTION RULES
   ↓
A coding agent helps implement
   ↓
GitCo validates OUTPUT
GitCo manages contribution LIFECYCLE
```

Expose an **MCP server** so any agent can ask GitCo for context:

```
gitco.get_portfolio          gitco.get_issue           gitco.recommend
gitco.prepare_contribution   gitco.get_contributing_rules
gitco.run_preflight          gitco.get_upstream_changes
gitco.get_pr_feedback
```

Integrations: Claude Code, Codex, Gemini CLI, Cursor, GitHub Copilot, OpenCode, generic MCP clients. **This is strategically far stronger than embedding one proprietary agent** — it makes GitCo infrastructure rather than a competitor.

## 7.9 An Agent-Safe Contribution Manifest

```bash
gitco contribute owner/repo#123 --prepare
```

produces `.gitco/contribution.json`:

```json
{
  "schema_version": "1",
  "repository": "owner/repo",
  "issue": 123,
  "base_branch": "main",
  "branch": "gitco/issue-123",
  "worktree": "~/.gitco/worktrees/owner/repo/issue-123",
  "allowed_scope": ["src/foo/**", "tests/foo/**"],
  "required_checks": ["uv run pytest tests/foo", "uv run ruff check ."],
  "contribution_rules": [],
  "linked_context": [],
  "security_constraints": []
}
```

Any coding agent — and any human — consumes the same contract. **This could become an open standard**, and the project that authors it gains a durable position.

---

# PART 8 — THE PRODUCT: WHAT GITCO SHOULD ACTUALLY BE

## 8.1 The Competitive Field Is Crowded, and Parts of GitCo Are Already Commoditized

| Capability | Incumbent | Status |
|---|---|---|
| Sync one fork | **`gh repo sync`** — official GitHub CLI, built in | Free, universal, zero-config |
| Sync one fork via UI | GitHub's native "Sync fork" button | Free, zero-install |
| Sync many forks automatically | **`wei/pull`** — ~7,200 stars, GitHub App | Free, zero-install; merge/squash/rebase/hard-reset; auto-assigns reviewers on conflict; GHES-compatible |
| Sync forks in CI | Fork Sync Action, Sync-Fork-Action (Marketplace) | Free |
| Batch sync many forks from CLI | `hexh250786313/gh-repo-sync` (a `gh` extension) | Free |
| Find good first issues | goodfirstissue.dev · goodfirstissue.org · up-for-grabs.net · CodeTriage · `MunGell/awesome-for-beginners` · DeepSource's Good First Issue | Free, web-based, curated |
| Personalized repo/issue discovery | **Repo Radar** — local-first, preference profile from stars/saves/portfolio, transparent relevance/activity/quality/novelty signals, documented offline NDCG/Precision/Recall/MRR evaluation | Free, actively developed |
| Good-first-issues in repos you care about | `yakub268/good-first-issue` | Free |
| Contribution lifecycle automation | **`oss-autopilot`** — issue discovery, PR tracking, maintainer response, contribution velocity; Claude Code plugin, MCP server, standalone CLI | Free, actively developed |
| AI change analysis | Every LLM CLI; `git log \| llm` | Trivially replicable |

**The unpleasant truth: roughly 60% of GitCo's advertised surface area is already solved, for free, by tools with four orders of magnitude more adoption.** `wei/pull` alone has ~7,200 stars to GitCo's 0, requires **zero installation**, and handles the multi-fork sync case as a hosted GitHub App.

**Therefore GitCo's competitive stance cannot be:**

```
We use AI to recommend GitHub issues.       ← becoming generic
We keep your fork synchronized.             ← GitHub already does this
```

## 8.2 Where GitCo Actually Has a Defensible Wedge

There *is* a real, unoccupied position. It is narrower and sharper than "intelligent fork management":

> **GitCo is the local-first tool that tells a maintainer of many forks what changed upstream that will break *their* patches — and what to do about it.**

The five differentiators incumbents structurally cannot match:

1. **Local-first; works on private, self-hosted, and air-gapped repositories.** `wei/pull` is a hosted GitHub App; it cannot touch your local working tree or a corporate GitLab. GitCo runs on your machine. **This is the strongest moat, and it is free — it is a consequence of the form factor already chosen.**
2. **Semantic impact analysis, not merge mechanics.** Nobody answers *"upstream deprecated the API my patch depends on."* `wei/pull` opens a PR; it does not tell you why you should care. `libs/detector.py` (742 lines) and `patterns/constants.py` (476 lines) already aim at exactly this. **This is the crown jewel and it is buried under a broken CLI.**
3. **Cross-repository, whole-portfolio view.** One command answering *"across my 14 forks, what needs my attention this week?"* No incumbent does this.
4. **Skill-graph-driven discovery grounded in what you actually maintain and have shipped.** goodfirstissue.dev shows the same list to everyone. GitCo already reads your configured repos and skills — issue recommendations weighted by *your demonstrated code history* is genuinely novel.
5. **Deterministic, no-API-key fallback.** `analyze_changes_without_llm` already exists. Being genuinely useful without an LLM is a real advantage over every "AI-powered" competitor.

**The strategic recommendation is uncomfortable but clear: stop competing on `sync`.** Make `sync` a thin, reliable, boring wrapper — and seriously consider making it `gh repo sync`-aware rather than reimplementing Git plumbing in 3,178 lines. **Put the entire differentiation budget into #2, #3, and #4**, where roughly 1,200 lines of already-written detector and discovery logic are sitting unused.

## 8.3 The Reframe — An OSS Contribution Control Plane

The current tagline undersells and misdirects:

> "A simple CLI tool for intelligent OSS fork management and contribution discovery."

"Simple CLI" conflicts with a 33-subcommand codebase. "Fork management" sounds like plumbing. "Contribution discovery" places GitCo in an increasingly crowded recommendation category.

**A substantially stronger thesis:**

> **GitCo is a local-first control plane for open-source contribution: keep every fork healthy, understand what changed upstream, find the contribution you're most likely to land, and carry it from discovery to merge.**

Compactly: **Know what changed. Know what to contribute. Ship it.**

The system then has four coherent loops that compound rather than four features that coexist:

```
┌───────────────────────────────┐
│      Contributor Profile      │
│ skills · history · interests  │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│      Repository Portfolio     │
│ forks · upstreams · PRs       │
└──────────────┬────────────────┘
     ┌─────────┼─────────┐
     ▼         ▼         ▼
   Sync     Analyze    Discover
     └─────────┼─────────┘
               ▼
┌───────────────────────────────┐
│      Contribution Engine      │
│ choose → worktree → plan      │
│ code → test → PR → follow-up  │
└──────────────┬────────────────┘
               ▼
┌───────────────────────────────┐
│    Contribution Intelligence  │
│ outcomes improve ranking      │
└───────────────────────────────┘
```

**This creates a flywheel rather than a collection of commands.**

**The complete contributor workflow GitCo is uniquely positioned to own end to end:**

```
discover project → understand repository → find contribution → understand issue
→ prepare local fork → synchronize upstream → understand changes since last work
→ implement → test → open PR → respond to maintainer → keep branch current → merge → repeat
```

Most tools solve one slice. GitCo already contains enough adjacent machinery to own the whole loop.

## 8.4 A Narrower Alternative Framing — And Why It Deserves Serious Weight

There is a second, more conservative product thesis that should be weighed honestly against §8.3, because it is likely the faster path to a tool anyone actually trusts:

> **A transparent, recoverable, local-first fork synchronization and upstream-change explanation tool.**

**The winning product is probably *smaller* than the current one.**

### GitCo Core — a deterministic fork-maintenance engine

```bash
gitco init
gitco doctor
gitco sync --dry-run
gitco sync --plan plan.json
gitco sync --apply plan.json
gitco status
gitco diff-upstream
```

The core detects upstream divergence, classifies local and upstream commits, produces a sync plan, identifies likely conflicts, shows affected files, preserves local work, creates a recoverable branch, optionally opens a pull request, and emits a complete machine-readable report.

### GitCo Explain — bounded, evidence-first, optional

Only *after* deterministic analysis:

```bash
gitco explain upstream-commit <sha>
gitco explain conflict <id>
gitco explain patch <path>
```

**The model explains evidence. It never silently decides what to merge.**

### GitCo Discover — later, or never

Keep contribution discovery separate until users prove they want it. It can become a plugin or a companion project.

**The biggest risk to this project is not that GitCo lacks intelligence. It is that GitCo performs too many consequential operations behind a broad promise of intelligence, without enough tests, usage evidence, or a sharply defined user.**

**Reconciling §8.3 and §8.4:** they are not in conflict — §8.4 is the first two phases of §8.3, executed properly. Build Core until five independent maintainers trust it; then, and only then, let Explain, Discover, and the contribution lifecycle grow on top of earned trust. Building §8.3's full surface before §8.4's core is trustworthy reproduces exactly the failure mode that produced this assessment.

---

# PART 9 — THE INTELLIGENCE MOAT: WHAT TO BUILD

## 9.1 Patch-Impact Analysis — The Killer Feature

Nobody in the market does this. GitCo is ~70% of the way there and does not know it.

> **"Upstream changed `Model.save()`'s signature. You have 3 commits touching that function in your fork. Here is the specific conflict, and here is a suggested resolution."**

**Implementation sketch:**

1. Compute the fork's divergence set: `git log upstream/main..HEAD`.
2. Extract the set of symbols (functions, classes, methods) that the divergence touches — via `ast` for Python, tree-sitter for everything else.
3. Extract the symbol set touched by incoming upstream commits.
4. **Intersect.** The intersection is the blast radius.
5. Feed **only that intersection** to the LLM — small, precise, cheap prompts instead of whole diffs.
6. Rank by severity; surface as `gitco impact`.

**This turns the LLM from a summarizer (commoditized) into a targeted reasoner over a precisely-scoped context (defensible), and cuts token cost by an order of magnitude simultaneously.**

## 9.2 Predictive Conflict Detection

Run `git merge --no-commit --no-ff` as a dry run against upstream **before** the user syncs; report which of their patches will conflict, ranked by severity. `GitRepositoryManager` already has `abort_merge`, `get_merge_status`, `resolve_conflicts`, and `_detect_merge_conflicts` — **the primitives exist.**

## 9.3 Upstream Situational Awareness

A contributor rarely cares that "37 commits arrived upstream." They care: **do any of those changes matter to me?**

```
django/django
Upstream: +127 commits since your last sync

Important to you
  HIGH     ORM query compiler changed in 4 files you previously modified
  HIGH     Deprecation introduced for API used by your open PR #18612
  MEDIUM   PostgreSQL backend changed around connection pooling
  LOW      72 documentation/test-only commits

Your work
  PR #18612 likely conflicts with upstream commit e21c19a
  Branch feature/async-orm touches 3 files changed upstream

Recommended
  Rebase PR #18612
  Review deprecation 5.2 → 6.0
  No action required on feature/async-orm
```

**That is upstream situational awareness, not synchronization.** It is the single most valuable thing GitCo can deliver.

## 9.4 Fork Debt — A Metric Only GitCo Can Compute

GitCo is uniquely positioned to define a metric that no contribution-discovery product can replicate, because it requires the local working tree.

**A fork accumulates debt from:** upstream divergence · unmerged local commits · stale branches · local branches touching files heavily changed upstream · unresolved conflicts · outdated dependency locks · abandoned PR branches · deleted upstream branches · PRs based on obsolete revisions.

```
Fork debt: HIGH

127 upstream commits behind
  4 stale local branches
  2 open PRs behind base
  1 likely conflict
  3 branches whose upstream branch was deleted
```

```bash
gitco debt
```

is a genuinely memorable command, and the concept is nameable, teachable, and citable — which matters for adoption far more than another dashboard.

## 9.5 Build a Real Contributor Skill Graph

The README currently asks the user to hand-declare `skills: [python, web, orm]`. **This should become optional enrichment, not the source of truth.** GitCo already has the developer's repositories; it can infer actual capability.

**Inputs:**

**Code ownership** — measured from actual code, not profile text:

```
Python        ████████████████████
FastAPI       ███████████████
PostgreSQL    █████████████
Terraform     █████████
React         ██████
Rust          ██
```

**Symbol-level experience:** authentication · GraphQL · caching · pagination · rate limiting · database migration · distributed queues · Kubernetes · observability.

**Contribution outcomes:** a merged PR must count far more than merely touching a technology.

**Recency decay:** something used last week outweighs something used eight years ago.

**Depth tiers:** `encountered` → `used` → `frequent` → `expert` → `maintainer-level`.

**Artifact types:** implementation · tests · docs · CI/CD · infrastructure · API design · performance work · security work.

**This becomes one of GitCo's most valuable local assets, and it cannot be scraped or copied.**

## 9.6 Code-Context Matching Is the Real Recommendation Moat

Keyword matching should become **candidate generation only**. For each issue:

1. extract likely affected files/modules/symbols;
2. inspect labels, body, and discussion;
3. inspect recent related commits;
4. inspect linked PRs;
5. inspect code ownership and history;
6. build an issue representation;
7. compare it against the contributor graph.

Then GitCo can discover that:

> An issue never mentions "FastAPI," but it modifies `APIRouter`, dependency injection, and Pydantic request models — which strongly matches this developer.

**That is materially better than text matching, and it is not replicable without the local code.**

## 9.7 Maintainer Receptiveness

Issue difficulty is not enough. **A trivial issue in an unresponsive repository is worse than a complex issue in a highly responsive one.** Compute a transparent Maintainer Receptiveness Profile from:

```
median first response to first-time contributors
median PR review latency          median merge latency
PR merge rate                     first-time contributor merge rate
stale PR percentage               issue-to-PR conversion rate
open issue age distribution       recent maintainer activity
review comment turnaround         release recency
contributor retention
```

```
Maintainer receptiveness: Excellent

First response         7h median
First-time PR merge    71%
PR review              1.4d median
Recent activity        Very high
```

**This could be one of GitCo's killer differentiators** — it answers a question every contributor asks and no directory answers.

## 9.8 Issue Claimability

A common failure mode of contribution directories is recommending an issue that is technically open but functionally unavailable. Detect: assigned user · linked pull request · "working on this" / "I'll take this" comments · draft PR · recent branch reference · maintainer reservation · duplicate issue · stale-but-effectively-solved.

Then classify:

```
AVAILABLE · LIKELY_AVAILABLE · POSSIBLY_CLAIMED · CLAIMED · PR_IN_PROGRESS · STALE · BLOCKED
```

**This makes recommendations substantially more actionable, and it is cheap to compute.**

## 9.9 Contribution Readiness — Repository-Level

More relevant to GitCo than generic "repository health":

```
Contribution Readiness: 91/100

CONTRIBUTING.md        ✓     setup instructions     ✓
tests documented       ✓     issue templates        ✓
PR template            ✓     good-first-issues      ✓
CI healthy             ✓     maintainers active     ✓
devcontainer           ✓
```

**Detect and use the repository's own environment declarations** rather than guessing: `.devcontainer/` · `flake.nix` · `devbox.json` · `mise.toml` · `.tool-versions` · `uv.lock` · `poetry.lock` · `Cargo.lock` · `go.mod` · any package-manager lockfile.

```
Repository provides a devcontainer.
Use it for isolated contribution setup? [Y/n]
```

**This converts setup from guesswork into structured intelligence.**

## 9.10 The Current Scoring Is Too Hand-Wavy — Fix It Before It Hardens

`libs/discovery.py` computes recommendations from hardcoded additive constants: exact skill matches (`0.8`), partial matches (`0.6`, gated at `> 0.3`), related/synonym matches (`0.4`, gated at `> 0.2`), repository-language matches (`0.3`, gated at `> 0.1`), skill-diversity bonus (`min(n * 0.1, 0.3)`), high-confidence bonus (`0.1` per match above `0.8`), good-first-issue bonus (`0.2`), recency bonus (a **hardcoded `0.1`**, with the comment `# Could be enhanced with actual date logic`), familiarity bonus (`min(n * 0.08, 0.25)`), and per-skill usage bonus (`min(count * 0.03, 0.15)`).

`libs/contribution_tracker.py` does the same for four "advanced metrics":

```python
collaboration_score  = mean over contributions of:
                         0.3 if assignees
                       + min(comments  * 0.05, 0.4)
                       + min(reactions * 0.1,  0.3)

recognition_score    = mean of: min(reactions * 0.2, 0.6) + min(comments * 0.1, 0.4)

influence_score      = average_impact * 0.4 + collaboration * 0.3 + recognition * 0.3

sustainability_score = max(0, 1 - (mean_days_between_contributions / 30))
```

**These are fine as v0.1 experiments. They must not become the permanent system, and they must not be presented as measurements.**

Arbitrary additive constants create **fake mathematical precision**. A score of `0.87` is not an 87% probability of anything; it is an internal number. And several of the implied claims are simply false:

- *"Lower average time between contributions = greater sustainability"* — a developer contributing one exceptional PR every two months may be far more sustainable than one making cosmetic weekly changes.
- *more comments ≠ more collaboration quality*
- *more reactions ≠ more recognition quality*

**Two remedies, in order:**

**Immediate (cheap, honest):** rename them. Until validated, call them **activity signals**, not `collaboration_score` / `influence_score` / `sustainability_score`. Naming a heuristic after a virtue makes it unfalsifiable.

**Structural (the real fix):** decompose into separately-computed, separately-explained components:

```
retrieval score · relevance score · contribution-readiness score
maintainer-receptiveness score · developer-fit score
difficulty score · risk score · novelty score
```

and always expose the evidence:

```
92 / 100 — Excellent match

Why
  + Python/FastAPI directly matches 28% of your recent code
  + Issue touches OAuth flow; you modified auth systems in 7 repositories
  + Repository merged 74% of first-time contributor PRs in the past 90 days
  + Median maintainer first response is 13 hours
  + Setup is reproducible and CI currently passes
  + Issue is unassigned with no competing PR

Risks
  − Issue is 39 days old
  − Scope touches 8 files
```

**The score is useful because the evidence is visible.** Keep explainability — it is the current implementation's genuine virtue — while replacing the magic constants.

## 9.11 The Ultimate Metric

The category-defining version of GitCo should eventually estimate:

```
P(this developer makes a worthwhile, accepted contribution to this issue)
```

rather than:

```
keyword_overlap(issue, skills)
```

Signals: skill similarity · code-context similarity · repository familiarity · issue clarity · issue scope · issue age · maintainer responsiveness · first-time-contributor history · CI health · setup complexity · absence of a linked PR · claimability · developer availability preference · historical contribution outcomes.

**The score must remain explainable at every step.**

## 9.12 Feedback Learning

```bash
gitco recommend
gitco dismiss owner/repo#123 --reason="too-large"
gitco save owner/repo#456
gitco contribute owner/repo#789
```

Reasons carry the signal: `not interested` · `wrong language` · `too difficult` · `too easy` · `repository uninteresting` · `maintainers inactive` · `issue unclear` · `already claimed` · `setup painful`.

**GitCo then learns far more than any stars-based profile can express.**

## 9.13 A Recommendation Evaluation Harness

A recommendation engine without an evaluation harness is an opinion. Build:

```
evaluation/
├── repositories/    ├── issues/      ├── judgments/
├── profiles/        ├── baselines/   └── reports/
```

Measure: **NDCG@5 · NDCG@10 · Precision@5 · Recall@10 · MRR · HitRate@5 · diversity · novelty · popularity bias · cold-start quality · repository concentration.**

Then measure what actually matters:

```
recommendation → investigation
recommendation → issue claimed
recommendation → PR opened
recommendation → PR merged
```

**Make scoring changes benchmark-gated.** Every PR that touches ranking logic must produce:

```
Before          After
NDCG@5    .712  .739 (+3.8%)
MRR       .641  .655 (+2.2%)
Diversity .583  .601 (+3.1%)
Popularity bias unchanged
```

**That is how GitCo becomes scientifically credible rather than merely "AI-powered."** Note that a competing project in this space already publishes exactly this kind of offline evaluation and explicitly refuses to claim ranking quality before its corpus is judged — that is the bar.

## 9.14 Open the Scoring Specification

Publish `GITCO-SCORE-SPEC.md`. Define each signal, its data source, its time window, its calculation, and its limitations. Let contributors propose weights. Run benchmarks on every scoring PR. Eventually **GitCo Score v2 becomes an open specification rather than a magic number.**

## 9.15 Repository Health: Aggregate Standards, Don't Invent an Island

`libs/health_metrics.py` computes bespoke health metrics. The temptation will be to ship a proprietary "GitCo Health Score." **Avoid building an opaque score nobody trusts.**

**OpenSSF Scorecard** already exists to assess security-related characteristics of open-source projects automatically. **CHAOSS/GrimoireLab** already provides an ecosystem for software-development analytics and metrics. **GitCo should become an aggregator and interpreter of respected signals, not a competing island.**

```
Repository Health: 82 / 100

Maintenance          91      Contributor UX       87
Security             74      Release discipline   80
Responsiveness       89      Build health         78

External
  OpenSSF Scorecard  8.1/10
  License            Apache-2.0
  Last release       12 days ago
  Default CI         passing

GitCo-specific
  first-contributor merge rate   73%
  median PR response             11h
  setup reproducibility          high
```

**Every metric must carry: definition · data source · time window · calculation · limitations.**

## 9.16 Surface Trust as a Product Feature

Instead of merely running security scanners in CI, show trust to the user at the moment of decision.

Before contributing:

```
Repository trust

OpenSSF Scorecard          8.6
Branch protection          yes
Pinned CI dependencies     partial
Security policy            yes
Recent suspicious changes  none
```

Before sending a diff to an LLM:

```
Secret scan:
  0 credentials
  0 high-entropy tokens
  1 potentially sensitive URL
Redacted automatically.
```

**GitCo could become the safest way to use AI in an OSS contribution workflow** — which is a positioning nobody currently occupies.

---

# PART 10 — CLI, UX, AND INTERFACE DESIGN

## 10.1 Proposed Command Information Architecture

```
gitco
├── init                 ← --from-github autodiscovery, not manual YAML
├── doctor               ← mandatory; see §10.3
├── status               ← the portfolio dashboard
├── next                 ← the hero command; see §10.5
├── inbox                ← the retention loop; see §10.6
│
├── repo
│   ├── list · add · remove · inspect · health
│
├── sync
│   ├── plan · apply · status · undo
│
├── upstream
│   ├── changes · impact · digest
│
├── discover
│   ├── issues · repos
│
├── contribute
│   ├── start · status · preflight · finish
│
├── pr
│   ├── list · feedback · sync · open
│
├── profile
│   ├── show · skills · feedback
│
├── backup
├── config
└── completion
```

**Hero aliases stay short:**

```bash
gitco next
gitco contribute owner/repo#123
gitco sync
gitco inbox
```

**Rarely-used commands live under namespaces.** The current flat surface — `activity`, `logs`, `performance`, `validate-repo` all at root — spends top-level namespace on diagnostics.

## 10.2 Sync Must Be Plan-First

**Never surprise the user.** `gitco sync` should default to producing a plan for any non-trivial operation:

```
Sync plan

django
  upstream/main +32
  local main clean
  operation: fast-forward

pydantic
  upstream/main +18
  branch main has 2 local commits
  operation: merge required

ruff
  working tree dirty
  operation: stash → sync → restore

Apply 3 operations? [y/N]
```

Automation opts out explicitly:

```bash
gitco sync --apply --non-interactive
gitco sync --plan plan.json      # emit
gitco sync --apply plan.json     # execute a previously reviewed plan
```

**This is a trust feature, not a convenience feature.** Every mutating command needs `--dry-run`.

## 10.3 `gitco doctor` Is Mandatory

```
GitCo Doctor

Git                  ✓ 2.52.1
GitHub CLI           ✓ authenticated as <user>
GitHub API           ✓ 4,812 / 5,000 requests remaining
GitCo database       ✓
Configuration        ✓
Default repository   ✓
OpenAI               ✓ optional
Local model          — not configured
Filesystem           ✓
Backup directory     ✓
Shell completion     ✓ zsh
Version              0.4.0

Warnings
  ! 2 configured repository paths no longer exist
  ! GitHub token expires in 11 days
```

**This eliminates enormous amounts of support friction** and gives every bug report a standard first attachment.

## 10.4 Make Every Operation Idempotent

```bash
gitco sync; gitco sync                 # second run must be a no-op, not a surprise
gitco init --from-github               # must reconcile, not duplicate
gitco backup create                    # must have predictable snapshot semantics
```

**Idempotence needs automated tests, not intentions.**

## 10.5 `gitco next` Should Become the Hero Command

A great tool needs one command people remember.

```bash
gitco next
```

```
Your best next OSS contribution

astral-sh/ruff #18342
Support X configuration in formatter

Fit                      94/100
Estimated effort         2–4h
Maintainer receptiveness Excellent
Claimability             Available
Repository health        Excellent

Why you
  • Python appears in 71% of your recent work
  • You've worked on AST transformations in 4 projects
  • You previously contributed to Ruff
  • Issue touches parser code similar to files in your history

Why now
  • opened 9h ago
  • explicitly marked help wanted
  • unassigned
  • no linked PR
  • maintainer active today

Start:
  gitco contribute astral-sh/ruff#18342
```

**If GitCo can make that command feel reliably magical, the rest follows.**

## 10.6 `gitco inbox` Is the Retention Loop

**Discovery gets installation. Follow-up gets retention.**

```
2 maintainer responses
1 PR needs rebase
1 CI failure
3 upstream changes affecting active work
1 merged contribution

Needs you

pydantic/pydantic #12411
  Maintainer requested changes 42m ago
  "Can you add coverage for nested generics?"

rust-lang/rust #141223
  Your branch is 18 commits behind
  Conflict probability: low

Merged

astral-sh/ruff #18342
  Merged 4h ago 🎉
```

**This turns GitCo from a periodic utility into something contributors open every day.**

## 10.7 `gitco contribute` — The Full Loop

```bash
gitco contribute pydantic/pydantic#12431
```

should:

1. validate the issue is still open;
2. detect whether somebody is already assigned;
3. detect comments claiming the issue;
4. detect linked PRs;
5. inspect `CONTRIBUTING.md`;
6. inspect development setup;
7. inspect test instructions;
8. inspect relevant code;
9. synchronize the fork;
10. create a branch/worktree;
11. create a contribution plan;
12. show affected symbols and files;
13. run environment checks;
14. optionally hand the plan to a coding agent;
15. run project-prescribed tests;
16. run repository lint/type checks;
17. prepare the commit;
18. draft the PR body according to the repository's template;
19. open the PR **after confirmation**;
20. track review;
21. surface maintainer comments;
22. synchronize the branch when upstream changes;
23. record the outcome;
24. improve future recommendation quality.

**That is much harder to commoditize than "find good first issues."**

## 10.8 A Reproducible Contribution Plan

```bash
gitco plan owner/repo#123
```

```markdown
# Contribution Plan

## Issue
owner/repo#123

## Goal
…

## Relevant Files
- src/parser.py
- tests/test_parser.py

## Repository Rules
- Python 3.11+
- Ruff formatting
- mypy required
- conventional commits

## Setup
…

## Validation
1. uv sync
2. uv run pytest tests/test_parser.py
3. uv run ruff check .
4. uv run mypy src

## Expected Scope
2–4 files

## Risks
…
```

**This artifact can be handed to any coding agent or any human, unchanged.**

## 10.9 `gitco preflight`

Deterministic, before any PR:

```
✓ required tests
✓ formatter
✓ type checker
✓ repository contribution rules
✓ branch synchronized
✓ no secrets
✓ scope consistent with issue

Ready to submit.
```

## 10.10 A Stable Machine API

The existing text/JSON/CSV output support is valuable. **Formalize it.**

```bash
gitco next --json
```

```json
{
  "schema_version": "1",
  "recommendations": []
}
```

**Never silently break automation because a table column changed.** Document the JSON schemas, version them, and treat schema changes as breaking changes. This turns GitCo into infrastructure other OSS tools can build on. Pair it with **stable, machine-readable exit codes.**

## 10.11 A Local TUI

Rich is already a dependency and the presentation layer is already terminal-oriented.

```bash
gitco dashboard
```

Views: **Repositories · Opportunities · Active Contributions · Inbox · Upstream Changes · Health · History.**

**Do not replace the CLI.** The invariant:

> Every TUI action corresponds to a scriptable command or API operation.

## 10.12 Offline Mode

```bash
gitco --offline status
gitco --offline next
```

must work from cached data, and must show the data's age:

```
GitHub metadata cached 2h 11m ago
```

**This reinforces the local-first architecture and is a hard requirement for the air-gapped audience that constitutes GitCo's differentiated user base.**

## 10.13 Cache Semantics

Respect **ETags · pagination · rate-limit headers · sensible TTLs · conditional requests · GraphQL batching where advantageous.** GitCo already has solid rate-limiting abstractions; the world-class behavior built on top of them is:

> **Do not call the network unless freshness requires it.**

## 10.14 UX Principle — Every Error Must Tell the User What to Do

Bad:

```
GitHub API error: 403
```

Great:

```
GitHub rejected the request.

Your token can read repositories but cannot inspect private issues.

Fix:
  gh auth refresh -h github.com -s repo

Or continue with public repositories:
  gitco discover --public-only
```

**Every error must contain four things: what failed · why GitCo thinks it failed · whether anything changed · how to recover.**

GitCo's Rich error panels are already well-formatted; the content needs to catch up to the presentation.

## 10.15 UX Principle — Never Hide Repository Mutation

```
Before:      What GitCo will change
After:       What GitCo changed
On failure:  What GitCo changed before failing
```

**This should be treated as inviolable.**

## 10.16 UX Principle — Progressive Disclosure

First-time user:

```bash
gitco next
```

Power user:

```bash
gitco discover issues \
  --language python \
  --min-maintainer-score 80 \
  --max-effort 4h \
  --unassigned \
  --no-linked-pr \
  --json
```

**Simple path first. Power underneath.**

## 10.17 Performance Design and Targets

Benchmark explicitly at **1 / 10 / 100 / 1,000 repositories** and **100 / 10,000 / 100,000 candidate issues**, measuring **cold start · warm start · API calls · GraphQL points · memory · disk cache · LLM tokens · cost.**

Targets:

```
gitco status       100 repos, warm cache      < 1s
gitco next         warm cache                 < 2s before optional semantic rerank
gitco sync --plan  100 local repos            < 5s excluding network
```

## 10.18 Reliability SLOs

```
0 known data-loss bugs
100% of destructive operations covered by tests
>99.9% transaction-recovery success across the fixture matrix
0 silent destructive fallbacks
100% of mutating commands support --dry-run / plan where meaningful
```

> **A Git tool earns loyalty by being safe enough that users stop thinking about safety.**

---

# PART 11 — DISTRIBUTION, RELEASE, AND SUPPLY CHAIN

## 11.1 Fix Distribution Identity First — It Blocks Everything

Restated because it gates every other item in this part: **`pip install gitco` installs a stranger's package.** Until a unique distribution name is chosen and registered, no release can succeed, no provenance can be trusted, and no install instruction can be written truthfully.

## 11.2 Ship as a GitHub CLI Extension

This is potentially the single best distribution decision available. GitHub officially supports third-party `gh` extensions as custom commands, installed from repositories with a `gh-` prefix.

```bash
gh extension install <owner>/gh-gitco
gh gitco status
gh gitco next
gh gitco contribute owner/repo#123
```

**Advantages:** authentication already exists · the developer audience already exists · GitHub context is native · installation is familiar · PyPI namespace collision becomes far less central · GitHub-side discovery improves · the CLI feels like part of an existing workflow rather than a new tool to adopt.

**This meets millions of users where they already are, and it is a few days of work.**

## 11.3 The Full Distribution Stack

```
uv tool install <package>      ← the modern default for Python CLI tools
pipx install <package>
Homebrew
Scoop
GitHub CLI extension
GitHub Releases standalone binaries (PyInstaller / Nuitka) for the no-Python audience
```

**A user should never be told to install a developer CLI globally with raw `pip` as the sole recommended path.**

## 11.4 Replace Long-Lived Tokens With Trusted Publishing

Current:

```yaml
TWINE_USERNAME=__token__
TWINE_PASSWORD=${{ secrets.PYPI_API_TOKEN }}
```

Target — PyPI Trusted Publishing (OIDC), which issues short-lived credentials instead of storing a long-lived API token, and whose official publishing action generates publish attestations automatically:

```
Git tag → CI validation → reproducible build → OIDC → PyPI Trusted Publishing
       → attestation → GitHub Release
```

Add `permissions: id-token: write`, use a GitHub Environment with required reviewers, and delete `PYPI_API_TOKEN`.

## 11.5 Supply-Chain Provenance

For a tool that manipulates source repositories, supply-chain trust matters disproportionately. Target:

```
SBOM (CycloneDX)                      build provenance (actions/attest-build-provenance, SLSA)
artifact checksums                    signed / attested releases
dependency review                     OpenSSF Scorecard action (target ≥ 7.0)
CodeQL                                secret scanning
every GitHub Action pinned to a full commit SHA
reproducible or strongly controlled builds
```

**Adopting the OpenSSF Scorecard action is unusually high-leverage here: it will mechanically enforce most of the Phase 0–2 items in Part 12, and it publishes a badge that substitutes for a reputation the project does not yet have.** Also apply for an OpenSSF Best Practices badge.

## 11.6 Replace the Archived Release Action

`release.yml:206` uses `actions/create-release@v1`, **archived and deprecated by GitHub since 2021.** Replace with `softprops/action-gh-release` or `gh release create`.

## 11.7 Dependency Maintenance Discipline

**15 open pull requests, predominantly stale Dependabot updates.** Automated PR creation is not dependency maintenance. Establish a routine:

```
weekly:
  merge safe dependency updates
  investigate breaking majors
  close obsolete PRs
  refresh lock files
```

**If Dependabot generates noise for months, contributors learn to ignore the PR tab — and then they ignore the real PRs too.**

Also fix the Dependabot `reviewers`/`assignees` mismatch (`41technologies` vs `smusali`).

## 11.8 Adopt a Lockfile

Keep flexible dependency constraints where library compatibility requires them, but adopt `uv.lock` (or equivalent) for **development · CI · release tooling · docs**. This eliminates "works on the maintainer's machine" drift and makes CI failures reproducible locally.

## 11.9 Missing Repository Hygiene Artifacts

```
py.typed                 ← PEP 561 (and add it to package-data)
.editorconfig
CITATION.cff
SUPPORT.md
ARCHITECTURE.md
docs/adr/
docs/security/threat-model.md
.secrets.baseline
SPDX license headers / REUSE compliance
a lockfile
GitHub Discussions (enable)
```

---

# PART 12 — THE ROADMAP

## Phase 0 — Stop the Bleeding (Days 1–2)

**Nothing else matters until the program runs. Do these in order.**

| # | Action | Effort |
|---|---|---|
| 0.1 | **Archive or clearly mark `main` as broken.** A README banner: "⚠️ Pre-alpha, currently non-functional, under repair." Honesty costs nothing at 0 stars and buys enormous credibility. | 5 min |
| 0.2 | **Rename the PyPI package.** Pick a free name, register it on PyPI immediately as `0.0.0`, update `pyproject.toml` (both entry-point tables), the console script, the README, and all five docs files. **Blocking — do it first.** | 1 hr |
| 0.3 | **Fix the stale absolute import** at `prompts/templates.py:7` → `from ..libs.detector import ...` | 5 min |
| 0.4 | **Fix the two silently-swallowed broken imports** at `utils/completion.py:158,175` → `from ..libs.config import get_config_manager`, and replace `except Exception: pass` with a logged handler. | 10 min |
| 0.5 | **Remove the four phantom re-exports** from `libs/__init__.py` (`ContributionDiscovery`, `DataExporter`, `GitOperations`, `HealthMetrics`) and stop eagerly importing the world. | 15 min |
| 0.6 | **Delete `src/gitco/cli.py`; move `main` into `cli/__init__.py`.** Add `src/gitco/__main__.py`. Verify `from <pkg>.cli import main` resolves and `python -m <pkg>` works. | 1 hr |
| 0.7 | **Delete the `try/except ImportError` around command registration.** Make it fail loudly with a non-zero exit. | 5 min |
| 0.8 | **Write `tests/test_imports.py`** — import every module, instantiate the Click group, assert every expected command is registered, assert every `__all__` name resolves. ~40 lines. **This one file prevents F-01, F-02, F-06, and the registration half of F-03 forever.** | 1 hr |
| 0.9 | **Add `.github/workflows/ci.yml`** — matrix over supported Pythons × {ubuntu, macos, windows}: install, `pytest`, `ruff check`, `ruff format --check`, `mypy`, `python -m build`, install-from-wheel, `gitco --help`. Make it a required check on `main`. | 2 hrs |
| 0.10 | **Add `mypy` to dev deps, pre-commit, and CI.** Start permissive; ratchet later. Add `src/<pkg>/py.typed` and register it in `package-data`. | 1 hr |
| 0.11 | **Fix the secret gate to `grep -rE`**, remove every `\|\| true` from security steps, and commit a real `.secrets.baseline`. | 30 min |
| 0.12 | Change `Development Status :: 4 - Beta` → `2 - Pre-Alpha`. Fix `SECURITY.md` boilerplate and the version table. | 15 min |
| 0.13 | Remove `gitpython` and `tiktoken` from `pyproject.toml` and `requirements.txt`; reconcile the two files' divergent version floors. | 15 min |
| 0.14 | Unify all metadata URLs on one canonical org. Fix Dependabot reviewers/assignees. De-duplicate the version constant. | 20 min |
| 0.15 | Delete `SSHGitHubClient` and `_make_ssh_request` (F-07, F-08). | 30 min |

**Exit criterion:** `pip install -e . && gitco --help` succeeds on a clean machine, and CI is green and enforced on `main`.

## Phase 1 — Reconnect the Two Halves (Weeks 1–2)

**This is the real repair.** For each of the 17 command surfaces, one at a time:

1. **Define the contract first** — add the Protocol to `libs/protocols.py`.
2. **Write the integration test before the fix** — invoke the command via Click's `CliRunner` against a fixture Git repository with a real upstream. Watch it fail.
3. **Implement a thin service adapter** in `libs/` satisfying the Protocol, wrapping the existing (good) `GitRepositoryManager` / `ChangeAnalyzer` / `IssueDiscovery` / `RepositoryHealthCalculator` / `ActivityDashboard`.
4. **Rewrite the Click callback to ≤ 30 lines:** parse → call service → render. All rendering moves to a `render/` module taking a result object.
5. **Move every import to module top level.** Delete all 54 `PLC0415` violations. This makes the next F-03 structurally impossible.

**Priority order — the four README commands first:** `sync` → `status` → `analyze` → `discover` → then `activity`, `upstream merge`, `config validate`, `logs`, `performance`, `validate-repo`, `completion`.

**Specific defects to fix along the way:**

- `config.repositories.keys()` on a `list[Repository]` (`cli/core.py:288`)
- `--repo` treated as a CWD-relative filesystem path instead of a configured-repository lookup (all six `upstream` subcommands, `validate-repo`)
- `ctx.obj` never populated → `ConfigManager(None)` everywhere
- `ActivityDashboard.get_repository_activity` / `.get_all_repositories_activity` (`cli/core.py:663,669`)
- `GitRepository.get_default_branch_name` → `get_default_branch` (`cli/upstream.py:393`)
- `GitRepository.merge_upstream` → `merge_upstream_branch` (`cli/upstream.py:396`)
- `ConfigManager.get_validation_report(strict=…)` — the parameter does not exist
- `GitCoLogger.get_recent_logs` — the method does not exist
- `completion` positional-vs-`--shell` mismatch
- `.git` treated as a directory → replace with `git rev-parse` introspection (F-15)
- Zip Slip in `_restore_repository`, and the ignored `overwrite_existing` parameter (F-13)

**Exit criterion:** every documented command executes successfully against a real fork, verified by an integration test running in CI.

## Phase 2 — Restore Trust (Weeks 3–4)

| # | Action |
|---|---|
| 2.1 | **Recover the deleted tests.** `git show cad42cf^:tests/…` — all 16,570 lines are still in history. Most need adaptation to the `libs/` layout, but this is **weeks of work already paid for.** Restore, adapt, and re-enable incrementally. |
| 2.2 | **Build the fixture matrix and failure-injection suite** from §5.7. This is the part that did not exist even before the deletion. |
| 2.3 | **Set a coverage floor and ratchet it.** Restore `.codecov.yml`. Start wherever the restored suite lands; never let it drop. |
| 2.4 | **Reduce the 199 `except Exception` blocks.** Every one must either re-raise a typed `GitCoError` or carry a justifying comment. Enable `BLE001`. |
| 2.5 | **Fix 202 `G004` logging f-strings** → `logger.info("synced %s", name)`. Enables structured log aggregation. |
| 2.6 | **Fix 48 `TRY400`** → `logger.exception` inside `except` blocks, to preserve stack traces. |
| 2.7 | **Fix 23 `DTZ005`** → timezone-aware `datetime.now(timezone.utc)` everywhere a timestamp enters an export, backup, or log. |
| 2.8 | **Add `check=True` to all 7 `subprocess.run` call sites**, or explicitly handle the return code with a typed error. |
| 2.9 | **Split `git_ops.py`** into `git_ops.py` / `git_auth.py` / `batch.py`; begin the `git/` package from §4.11. |
| 2.10 | **Collapse the three HTTP stacks to one.** Remove `PyGithub`. One `requests.Session` / `httpx.Client` behind a `GitHubTransport`. |
| 2.11 | **Rewrite all documentation against actual `--help` output.** Generate `docs/cli/*.md` from Click introspection so drift becomes structurally impossible. |
| 2.12 | **Delete `docs/QA.md`** or convert it into executable integration tests. |
| 2.13 | **Enable `mypy --strict` incrementally**, module by module, via `[[tool.mypy.overrides]]`. Delete the 17 blanket `# type: ignore`s. |
| 2.14 | **Adopt XDG config paths** with a migration shim for `~/.gitco/`. |
| 2.15 | **Nest the 23 flat `Settings` fields** into `github` / `llm` / `rate_limits` / `git` / `logging` groups. |
| 2.16 | **Replace `black` with `ruff format`;** bump every pre-commit hook; replace the archived `mirrors-prettier`; run `pre-commit run --all-files` in CI. |
| 2.17 | **Add `--dry-run` and plan-first behavior** to every mutating command; add the transaction journal and `gitco undo`. |
| 2.18 | **Add `gitco doctor`.** |
| 2.19 | **Write the threat model** (`docs/security/threat-model.md`) and the data-flow diagram. |
| 2.20 | **Add `TODO` comments and `good first issue` labels.** Zero TODOs in 19,565 lines means zero entry points for contributors. |

## Phase 3 — Ship a Real Release (Month 2)

| # | Action |
|---|---|
| 3.1 | **PyPI Trusted Publishing (OIDC).** Delete `PYPI_API_TOKEN`. Add `permissions: id-token: write` and a GitHub Environment with required reviewers. |
| 3.2 | **Replace `actions/create-release@v1`** with `softprops/action-gh-release`. |
| 3.3 | **Pin every GitHub Action to a full commit SHA.** Keep Dependabot for Actions to bump them. |
| 3.4 | **Generate an SBOM** (CycloneDX) and **attach build provenance** (`actions/attest-build-provenance`, SLSA). |
| 3.5 | **Add the OpenSSF Scorecard action** and publish the badge. Target ≥ 7.0. |
| 3.6 | **Apply for an OpenSSF Best Practices badge.** |
| 3.7 | **Consolidate `release.yml` and `pypi-publish.yml`** into one secure path. |
| 3.8 | **Tag `v0.1.0` and actually release it.** Verify the release workflow end to end — it has never run. |
| 3.9 | **Publish to Homebrew, `uv tool`, `pipx`**, and provide standalone binaries via PyInstaller/Nuitka. |
| 3.10 | **Ship a `gh` extension wrapper** (`gh gitco …`). The single highest-leverage distribution move available. |
| 3.11 | Add `CITATION.cff`, `.editorconfig`, SPDX headers, REUSE compliance, `SUPPORT.md`, and a lockfile. |

## Phase 4 — Prove It With Real Maintainers (Month 2–3)

**This phase has no code deliverable. It has an evidence deliverable.**

Find **5 to 10 maintainers who actually maintain meaningful forks.** Measure:

```
time spent before GitCo            time spent with GitCo
sync attempts                      successful syncs
conflicts detected                 incorrect classifications
rollback events                    abandoned forks recovered
continued use after the first run
```

> A repository with zero stars and no visible issue activity does not mean the code is bad. **It means there is almost no public evidence yet that the problem is being solved for anyone except its author.**

**Do not proceed to Phase 5 until this evidence exists.**

## Phase 5 — Build the Actual Moat (Months 3–6)

| # | Action |
|---|---|
| 5.1 | **`gitco impact` — patch-impact analysis** (§9.1). The killer feature. 3–4 weeks. |
| 5.2 | **Predictive conflict detection** (§9.2) — dry-run merge before sync. |
| 5.3 | **`gitco debt` — fork debt** (§9.4). |
| 5.4 | **Portfolio-wide `gitco status`** that ranks by attention score rather than printing a table. |
| 5.5 | **`gitco init --from-github`** — automatic portfolio discovery, replacing manual YAML as the primary path. |
| 5.6 | **Restore multi-provider + local LLM support** (§7.5). Removes the vendor-lock-in objection. |
| 5.7 | **Replace regex output parsing with typed structured results** (§7.2) and evidence-derived confidence (§7.3). |
| 5.8 | **Harden the LLM boundary** (F-16, §7.6) — delimiting, schema validation, redaction, disclosure prompt, no-LLM-drives-mutation rule. |
| 5.9 | **Automatic contributor skill graph** (§9.5), replacing manual `skills:` configuration. |
| 5.10 | **Code-context matching** (§9.6), maintainer receptiveness (§9.7), issue claimability (§9.8), contribution readiness (§9.9). |
| 5.11 | **Recommendation evaluation harness** (§9.13) and `GITCO-SCORE-SPEC.md` (§9.14). |
| 5.12 | **Worktree-based `gitco contribute`** (§10.7) and `gitco preflight` (§10.9). |
| 5.13 | **`gitco next`** (§10.5) and **`gitco inbox`** (§10.6). |
| 5.14 | **Multi-forge support** behind the `Forge` Protocol — GitLab, Gitea, Forgejo, Codeberg. |
| 5.15 | **MCP server + agent adapters** (§7.8) and the contribution manifest (§7.9). |
| 5.16 | **A `pre-commit` hook and a GitHub Action** so `gitco impact` can gate PRs. |
| 5.17 | **Plugin API** via `entry_points` for custom detectors, forges, providers, scorers, exporters. |

## Phase 6 — Community (Months 6–12)

| # | Action |
|---|---|
| 6.1 | **Write `ARCHITECTURE.md`** — the map of layers and Protocol boundaries. Highest-ROI document for a new contributor. |
| 6.2 | **Add a testing section to `CONTRIBUTING.md`** (currently zero mentions of testing). |
| 6.3 | **Publish a real demo** — an asciinema cast of `gitco impact` finding a genuine breaking change in a real fork. **One compelling 30-second demo outperforms 5,252 lines of documentation.** |
| 6.4 | **Write the launch post around the wedge, not the feature list.** Title it after the problem — *"Your fork is 400 commits behind and you don't know which ones will break your patches"* — not the tool. |
| 6.5 | **Dogfood publicly.** Pick 10–20 serious OSS projects, use GitCo to contribute, and publish: what GitCo recommended · why · time to first PR · maintainer response · whether it merged · what the recommendation logic learned. The strongest possible claim becomes **"GitCo helped its maintainers land 50 contributions across 20 major OSS projects."** |
| 6.6 | **Eat the dog food recursively.** `gitco next --repo <this-repo>`. Label GitCo's own issues `good first issue`, `help wanted`, `docs`, `testing`, `architecture`, `provider`, `scoring`. Contributors then experience GitCo while contributing to GitCo. |
| 6.7 | **Write issues properly.** Every issue carries: Problem · Desired behavior · Likely files · Acceptance criteria · Testing · Context · Difficulty · Skills. GitCo then becomes a benchmark-quality contribution repository. |
| 6.8 | **Set and keep a documented release cadence.** Nothing signals abandonment like the current 11-month gap. |
| 6.9 | **Enable GitHub Discussions; add `SUPPORT.md`.** |
| 6.10 | **Document a contributor ladder** — Contributor → Regular Contributor → Reviewer → Maintainer → Core Maintainer — with explicit expectations. The months-old dependency PR backlog is already a warning that maintenance bandwidth needs structure. |
| 6.11 | **Consider publishing an open benchmark dataset** — developer profile · issue metadata · repository context · human relevance judgment · contribution outcome, with careful privacy design. **If GitCo maintains the respected benchmark for OSS contribution recommendation, it gains intellectual legitimacy independent of the CLI itself.** |

## Version-Themed Milestones

Not a feature wishlist — explicit outcomes per version:

```
0.2 — Trust
      unique distribution · 200+ tests · Git transaction model
      worktree support · safe installation · CI gates

0.3 — Portfolio
      GitHub fork autodiscovery · local clone discovery
      portfolio status · fork debt

0.4 — Intelligence
      structured change analysis · provider abstraction
      upstream impact · local model support

0.5 — Discovery
      automatic skill graph · repository readiness
      maintainer responsiveness · issue claimability · ranking benchmark

0.6 — Contribution
      gitco next · gitco contribute · worktree provisioning
      contribution plan · preflight

0.7 — Lifecycle
      gitco inbox · PR tracking · maintainer-response tracking · branch refresh

0.8 — Agent Platform
      MCP server · agent integrations · contribution manifest

0.9 — Ecosystem
      GitLab adapter · plugins · stable JSON API

1.0 — Trustworthy OSS Contribution Control Plane
      stable contracts · proven recommendation quality · signed releases
      documented security model · migration guarantees · a real community
```

---

# PART 13 — THE PRIORITIZED FIX LIST

Ordered strictly by (impact ÷ effort). Do them top to bottom.

| Rank | Fix | Effort | Impact |
|---|---|---|---|
| 1 | Fix the stale absolute import in `prompts/templates.py:7` | 5 min | 🔴 Package becomes importable |
| 2 | Remove the 4 phantom re-exports from `libs/__init__.py` | 15 min | 🔴 Package import completes |
| 3 | Fix the 2 swallowed broken imports in `utils/completion.py` | 10 min | 🟠 Shell completion starts working |
| 4 | Delete `cli.py`, move `main` into `cli/__init__.py`, add `__main__.py` | 1 hr | 🔴 Entry point works for the first time ever |
| 5 | Rename the PyPI package + register the name | 1 hr | 🔴 Distribution becomes possible at all |
| 6 | `tests/test_imports.py` + a real CI workflow | 3 hrs | 🔴 Makes 1–4 permanent |
| 7 | Add `mypy` + `py.typed` | 1 hr | 🔴 Would have caught all 17 import bugs in 2 seconds |
| 8 | Delete the `try/except ImportError` in registration | 5 min | 🟠 Stops silent-success in automation |
| 9 | `grep -rE` + remove all `\|\| true` + commit `.secrets.baseline` | 30 min | 🟠 Security gates start working |
| 10 | Delete `SSHGitHubClient` / `_make_ssh_request` | 30 min | 🟠 Closes CWE-214 and removes a guaranteed-broken parser |
| 11 | Add the Zip Slip guard to backup restoration | 1 hr | 🟠 Closes CWE-22 |
| 12 | Replace `.git`-is-a-directory with `git rev-parse` introspection | 2 hrs | 🟠 Worktrees and submodules stop being rejected |
| 13 | Reconnect `sync` / `status` / `analyze` / `discover` to real APIs | 3–5 days | 🔴 **The product starts existing** |
| 14 | Restore the 16,570 deleted test lines | 1–2 weeks | 🔴 Regression safety returns |
| 15 | Move all 54 function-level imports to module top | 2 hrs | 🟠 Makes the F-03 class structurally impossible |
| 16 | `libs/protocols.py` + Protocol-typed layer boundaries | 2 days | 🟠 Prevents the entire F-03 class forever |
| 17 | Generate CLI docs from Click introspection | 1 day | 🟡 Ends doc drift permanently |
| 18 | Drop `gitpython` + `tiktoken`; reconcile requirement files | 20 min | 🟡 Smaller, faster, lower-risk installs |
| 19 | Replace `black` with `ruff format`; bump all hooks; run pre-commit in CI | 30 min | 🟡 One tool, no version skew, actually enforced |
| 20 | Add `check=True` to all `subprocess.run` calls | 30 min | 🟡 Silent Git failures become loud |
| 21 | Fix 202 `G004` + 48 `TRY400` + 23 `DTZ005` | 1 day | 🟡 Logs become aggregatable; stack traces survive; timestamps unambiguous |
| 22 | Split `git_ops.py` into three modules | 1 day | 🟡 Reviewability |
| 23 | Collapse three HTTP stacks into one; remove `PyGithub` | 1 day | 🟡 One place for auth, proxy, TLS, and rate-limit bugs |
| 24 | Build the Git fixture matrix + failure-injection suite | 1 week | 🔴 The only way a Git-mutating tool becomes trustworthy |
| 25 | Add `--dry-run` / plan-first to every mutating command | 3 days | 🟠 The core trust feature |
| 26 | Add the transaction journal + `gitco undo` | 3 days | 🟠 Recoverability becomes provable |
| 27 | Add `gitco doctor` | 2 days | 🟠 Eliminates most support friction |
| 28 | Trusted Publishing + provenance + SBOM + SHA-pinned actions | 4 hrs | 🟡 Supply-chain credibility |
| 29 | Tag and ship `v0.1.0` | 2 hrs | 🟠 Validates ~700 lines of untested release automation |
| 30 | Adopt XDG config paths with a migration shim | 2 hrs | 🔵 Correctness + ends the docs/code contradiction |
| 31 | Nest the 23 flat `Settings` fields | 3 hrs | 🔵 Do it before the surface hardens |
| 32 | Write the threat model + data-flow diagram | 1 day | 🟠 The precondition for asking anyone to trust this |
| 33 | Replace regex LLM parsing with typed structured output | 3 days | 🟡 Removes the silent-degradation failure mode |
| 34 | Evidence-derived confidence instead of model self-report | 2 days | 🟡 Makes the output defensible |
| 35 | Harden the LLM boundary against prompt injection | 3 days | 🟠 First-class threat for this product category |
| 36 | Restore multi-provider + local LLM support | 1 week | 🟢 Removes the vendor-lock-in objection |
| 37 | Rename `*_score` heuristics to `activity signals` | 1 hr | 🟡 Stops presenting guesses as measurements |
| 38 | Ship as a `gh` extension | 3 days | 🟢 Distribution to millions |
| 39 | `gitco init --from-github` portfolio autodiscovery | 1 week | 🟢 Removes the worst onboarding friction |
| 40 | **Build `gitco impact` (patch-impact analysis)** | 3–4 weeks | 🟢 **The actual moat** |
| 41 | Predictive conflict detection | 1 week | 🟢 The other half of the moat |
| 42 | Fork debt (`gitco debt`) | 1 week | 🟢 A metric only GitCo can compute |
| 43 | Automatic contributor skill graph | 3 weeks | 🟢 A local asset that cannot be scraped |
| 44 | Maintainer receptiveness + issue claimability + contribution readiness | 2 weeks | 🟢 Makes recommendations actionable |
| 45 | Recommendation evaluation harness + score spec | 2 weeks | 🟢 Scientific credibility |
| 46 | `gitco next` + `gitco contribute` + `gitco preflight` + `gitco inbox` | 4 weeks | 🟢 The hero loop |
| 47 | MCP server + agent adapters + contribution manifest | 2 weeks | 🟢 GitCo becomes infrastructure |
| 48 | Multi-forge (GitLab / Gitea / Forgejo / Codeberg) | 2–3 weeks | 🟢 Removes the market cap |
| 49 | Prove it with 5–10 real fork maintainers | 4 weeks | 🟢 The only evidence that matters |
| 50 | Public dogfooding log + launch post + demo cast | 2 weeks | 🟢 Adoption |

---

# PART 14 — WHAT TO DELETE, DEMOTE, OR REWRITE

**"Greatest OSS tool" will require removing as much as adding.** The current surface is broad enough that it risks becoming a collection of technically impressive features without one indispensable workflow.

## 14.1 Delete Outright

| Target | Reason |
|---|---|
| `src/gitco/cli.py` | Permanently unreachable dead code (F-02) |
| `SSHGitHubClient`, `_make_ssh_request`, `create_ssh_github_client`, `SSHGitHubResponse` | CWE-214 credential leak, guaranteed-broken parser, category error, constructed by nothing (F-07, F-08) |
| The `try/except ImportError` around command registration | Converts a broken install into a silent exit-0 (F-14) |
| Every `\|\| true` on a security step | Security theater (F-11) |
| `.github/security/config.yml` | 240 lines read by nothing — **or** implement it fully (F-24) |
| `docs/QA.md` | A manual test plan for an imagined program — **or** convert every step to an integration test (F-22) |
| `gitpython`, `tiktoken` dependencies | Never imported (F-19) |
| `PyGithub` dependency | One of three redundant HTTP stacks (F-20) |
| `black` from the toolchain | Superseded by `ruff format` (F-40) |
| `mirrors-prettier` pre-commit hook | Archived upstream (F-40) |
| One of the two release workflows | Duplicated logic, neither ever executed (F-28) |
| `SECURITY.md` boilerplate paragraph and the false `1.0.x` row | Misstates the supported version set (F-23) |
| The `Typing :: Typed` classifier — **or** add `py.typed` | False advertisement (F-21) |

## 14.2 Demote

| Target | Reason |
|---|---|
| **Generic repository-health dashboards** | Keep the underlying signals; do not make them central until they directly improve contribution choices |
| **`influence` / `collaboration` / `recognition` / `sustainability` scores** | Do not present them as objective before validation; rename to activity signals (§9.10) |
| **Excessive top-level CLI surface** | `activity`, `logs`, `performance`, `validate-repo` belong under namespaces, not at root |
| **Manual repository YAML onboarding** | Make it advanced configuration; `init --from-github` becomes the primary path (§4.7) |
| **Model and provider details in primary UX** | Implementation detail; lead with the result, not the vendor (§7.4) |
| **"AI-powered" as headline positioning** | In 2026 this is table stakes, not differentiation (§6.6) |
| **Backup/export/activity/contributions surface area** | Real work, but secondary until the hero loop is excellent (§14.4) |

## 14.3 Rewrite

| Target | Replacement |
|---|---|
| Brittle regex-based LLM output parsing | Typed structured output with schema validation and reject-retry (§7.2) |
| Model-self-reported confidence | Evidence-derived confidence (§7.3) |
| Hand-maintained `.git` filesystem assumptions | Git-native introspection via `rev-parse` (F-15) |
| Clever multi-path Git credential extraction | The explicit `GH_TOKEN` → `gh auth token` → PAT → GitHub App → anonymous chain (F-24) |
| Every Click callback over 30 lines | parse → service → render, with rendering in `render/` (§5.4) |
| `libs/exporter.py`'s four loose functions re-exported as a phantom class | A real `DataExporter` or explicit function imports (F-03) |
| Additive-constant recommendation scoring | Decomposed, separately-explained component scores (§9.10) |
| Flat 23-field `Settings` | Nested configuration groups (§4.6) |
| `~/.gitco/config.yml` | XDG path with a migration shim (F-34) |
| Ad-hoc `dict[str, Any]` returns from Git operations | Typed result dataclasses (`SyncResult`, `MergeResult`, `FetchResult`) |

## 14.4 The Hero Loop Is the Only Priority Until It Works

Until this sequence is excellent, everything else is a distraction:

```
gitco init
     ↓
gitco status
     ↓
gitco next
     ↓
gitco contribute
     ↓
gitco preflight
     ↓
gitco inbox
     ↓
merged
     ↓
GitCo gets smarter
```

**Stop adding generic dashboard features until that loop works.**

---

# PART 15 — WHAT IS GENUINELY GOOD

An honest assessment names the strengths, and there are real ones. **These should be preserved, not rewritten, during every phase above.**

| Asset | Why it matters |
|---|---|
| **`utils/retry.py` (672 lines)** | A proper retry framework: exponential and linear backoff, jitter to prevent thundering herd, timeout-aware strategy, recoverable-vs-terminal error classification (`_is_recoverable_error`), and `urllib3.Retry` integration. **Above the bar for most CLI tools.** |
| **`utils/rate_limiter.py` (351 lines)** | Separate GitHub and LLM budgets with per-minute, per-hour, and burst limits plus a minimum inter-request interval, wired through a `RateLimitedAPIClient` base class. **Genuinely thoughtful; most tools do none of this.** |
| **`utils/logging.py` (529 lines)** | Structured logging with file output, rotation, size caps, backup counts, and a detailed format mode. Error records captured during testing included `error_type`, `error_message`, full `stack_trace`, a context dict, an ISO-8601 timestamp, and an operation name. **This is better structured logging than most production services have.** |
| **`GitRepositoryManager` (33 public methods)** | `safe_stash_changes`, `restore_stash`, `drop_stash`, `safe_stash_and_restore`, `abort_merge`, `resolve_conflicts`, `get_merge_status`, `check_repository_sync_status`, and full upstream-remote lifecycle management. **The safety thinking here — stash before sync, restore after, abort cleanly on conflict — is exactly right for a fork-sync tool, and is the hardest part to get right.** |
| **`GitRepository` (32 methods)** | `get_commit_diff_analysis`, `_detect_merge_conflicts`, `get_recent_changes`, `_get_detailed_commit_diff`. Real Git plumbing, defensively written, `shell=True`-free. |
| **`analyze_changes_without_llm` (105 lines)** | A genuine heuristic fallback so the tool degrades to usefulness without an API key. **Many AI-first tools skip this. Keeping it is a differentiator — and it should be promoted from fallback to first-class path.** |
| **`prompts/templates.py`** | Prompts isolated from logic and rendered via Jinja2. **Correct, and rare.** Makes prompts reviewable, diffable, and swappable. |
| **`patterns/constants.py` (476 lines)** | Ten named detection heuristic families centralized and reviewable rather than scattered as inline regexes. |
| **`libs/detector.py` (742 lines)** | `BreakingChangeDetector` and `SecurityDeprecationDetector` aimed squarely at the actual wedge. **The crown jewel, currently unreachable behind a broken CLI.** |
| **`libs/discovery.py`'s `SkillMatcher`** | Explainable skill matching with exact/partial/related/language tiers. The constants need replacing; **the explainability must be preserved.** |
| **`BatchProcessor`** | Sizes its worker pool from `psutil.virtual_memory()` and `psutil.cpu_count()`, with caching, a thread pool, and performance monitoring. Overkill for today, but shows care. |
| **`Config` / `Settings` / `Repository` dataclasses** | Clean, typed, sensible defaults, with a dedicated `ConfigValidator` producing structured `ValidationError` objects. |
| **`utils/exception.py`** | A real 17-class typed exception hierarchy under `GitCoError` — already the right foundation for replacing the 199 blind excepts. |
| **Rich-based output** | The error panels triggered during testing were legitimately well-formatted. Presentation quality is genuinely high. |
| **Structured automation support** | Quiet mode and text/JSON/CSV output modes. **Exactly what a mature CLI should do: interactive for humans, scriptable for machines.** |
| **Backup/recovery considered early** | `BackupManager` with metadata persistence, multi-repository backups, restoration, deletion, cleanup, and config restoration. **Most early developer tools add recovery only after somebody loses work.** |
| **Documentation volume and structure** | 5,252 lines across 17 files covering quick-start, configuration, usage, CLI reference, features, tutorials, persona workflows, troubleshooting, FAQ, and releases. **The structure is what a mature project looks like** — the accuracy is the problem, not the ambition. |
| **Community scaffolding** | `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, three issue templates, a PR template, Dependabot, conventional-commit enforcement. **All present on day one — substantially better OSS hygiene than most projects at this stage.** |
| **Local-first form factor** | A CLI is the correct surface, because the relevant context — fork state, branches, dirty working tree, upstream remotes, changed files, development environment, repository configuration, developer workflow — lives locally. **This is the moat, and it was chosen correctly by instinct.** |
| **Treating OSS contribution as more than issue search** | Directionally correct, and the reason the project has a future. |

> **This is the crux: the parts requiring deep thought are done well; the parts requiring verification were skipped entirely. That is a fixable ordering problem, not a talent problem.**

---

# PART 16 — METRICS THAT MATTER

## 16.1 North-Star Metrics

Do not optimize primarily for stars. Track, via opt-in aggregated telemetry where ethically appropriate — or via explicit surveys and community data if telemetry stays disabled:

```
weekly active contributors
recommendation → investigation rate
recommendation → contribution-start rate
contribution-start → PR rate
PR → merge rate
median time to useful recommendation
median time from recommendation → PR
repeat contribution rate
repositories managed per active user
```

## 16.2 Secondary (Vanity) Metrics

```
stars · forks · Discord members · downloads
```

These are lagging indicators of the above, not substitutes for them.

## 16.3 The Milestone That Actually Matters

> **Five independent fork maintainers use GitCo repeatedly, trust its sync plans, understand its failure modes, and can point to time or maintenance risk it removed.**

**Your next milestone should not be another command, dashboard, provider, or tutorial. It should be that.**

If you achieve it, contribution discovery and AI analysis have somewhere credible to grow. Without it, GitCo remains an impressive amount of engineering looking for a narrower product.

---

# PART 17 — THE ENGINEERING DOCTRINE

Every recommendation in this document reduces to eight principles. Adopt them explicitly, write them into `CONTRIBUTING.md`, and enforce them in review:

```
deterministic before probabilistic
safe before clever
local before cloud
evidence before AI claims
structured before free-form
measured before marketed
workflow before features
interoperability before lock-in
trust before growth
```

And one operational rule that would have prevented every finding in this document:

> **Never delete the tests before the refactor. The tests were not overhead slowing the refactor down — the tests *were* the refactor's correctness proof.**

---

# PART 18 — THE HONEST BOTTOM LINE

**What GitCo is right now:** ~19,500 lines of Python containing a genuinely competent Git-operations library, a real rate limiter, a real retry framework, excellent structured logging, and a thoughtful breaking-change detector — **welded to a command-line interface that has never once executed successfully, distributed under a name that belongs to someone else, with zero tests, zero working CI, zero releases, and zero users.**

**Why it got here:** not incompetence. The library code is above average. It got here because on 2025-08-15, in a nine-minute window, the project deleted 16,570 lines of tests and every CI workflow, then immediately performed a 6,000-line architectural refactor. Every subsequent problem is downstream of that single ordering decision. The codebase then spent twelve months in a state where **no mechanism existed that could tell anyone it was broken** — and so nobody knew, including the author, who has since shipped four more commits on top of a package that cannot be imported, and written a 780-line manual QA plan for commands that do not exist.

**The lesson, stated plainly:** deleting the tests did not make the refactor faster. It made the refactor's failure **invisible**, which is strictly worse than making it slow. The 780-line QA document written afterward is the tell — it is an attempt to buy back with prose what was thrown away in code, and it failed, because it documents a program that was never built.

**The genuinely good news, and it is substantial:**

1. **The hard part is done.** Safe stashing, merge-conflict recovery, rate limiting with burst budgets, retry with jitter, skill matching, breaking-change heuristics, structured logging, a typed exception hierarchy — that is the expensive, judgment-heavy 70%. It exists and it is decent.
2. **The broken part is cheap.** Three stale imports, four phantom re-exports, one file rename, and a set of glue functions. **Phase 0 is a two-day job.** A competent engineer gets `gitco --help` working in under an hour.
3. **The tests are not gone.** All 16,570 lines sit in `git show cad42cf^`. Weeks of work are recoverable.
4. **Zero users means zero migration cost.** Rename the package, break every API, restructure everything — nobody will notice. **This freedom expires the moment the first person installs it, and it will never be this cheap again.** That argues strongly for doing the full architectural cleanup *before* seeking any attention.
5. **The wedge is real and unoccupied.** *"Which upstream changes will break my patches?"* is a question `wei/pull`'s 7,200 stars do not answer, `gh repo sync` does not answer, and no good-first-issue directory answers. GitCo has ~1,200 lines of detector and discovery code aimed squarely at it.

**The honest current label is not "production-ready" and not "beta."** It is: **a substantial pre-alpha foundation with a promising fork-maintenance wedge, currently non-functional.** That is still respectable, and it gives a sharper path to something people can trust than any optimistic label would.

**The strongest possible future GitCo is not a fork manager, not a good-first-issue finder, not an AI Git wrapper, not a repository dashboard, and not another coding agent.** It is:

> # **The local-first operating system for serious open-source contributors.**
>
> **GitCo understands your forks, your code history, your skills, your active contributions, upstream changes, repository health, issue availability, maintainer behavior, and contribution outcomes — then tells you what deserves your attention and safely carries that work from discovery to merge.**

The moat is the **contributor → repository → issue → code → outcome graph**, because prompts are copyable and graphs built from your own local history are not.

The defining product promise is:

> **GitCo should make an experienced open-source contributor dramatically more effective while making a first-time contributor dramatically less lost.**

**The single decision that determines this project's fate is whether the next commit is a feature or a test.**

If it is a feature, GitCo becomes another abandoned repository with excellent documentation for software that does not run — and there are thousands of those. If it is `tests/test_imports.py` plus a CI workflow, then in **two days it becomes a working tool**, in **two months a credible one**, and in **six months — if the patch-impact analysis in §9.1 gets built — something with a genuine, defensible reason to exist that nothing else on the market provides.**

**The code deserves the second path. Write the test first.**

---

# APPENDIX A — REPRODUCTION COMMANDS

```bash
# 1. Clone and build
git clone <repo> && cd gitco
python -m venv .venv && .venv/bin/pip install build
.venv/bin/python -m build --wheel

# 2. F-01 — the package does not import
.venv/bin/pip install dist/*.whl
.venv/bin/gitco --help
#  → ModuleNotFoundError: No module named 'gitco.detector'

.venv/bin/python -c "import sys; sys.path.insert(0,'src'); import gitco.libs"
#  → same failure, at prompts/templates.py:7

# 3. F-02 — the entry point is shadowed by the package
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); import gitco.cli as c; \
                     print(c.__file__, hasattr(c,'main'))"
#  → .../gitco/cli/__init__.py  False

# 4. F-03 — phantom classes
for s in GitOperations Analyzer DiscoveryEngine HealthMetrics PerformanceMetrics \
         LogManager ShellCompletion RepositoryValidator DataExporter ContributionDiscovery; do
  printf '%s: %s definitions\n' "$s" "$(grep -rc "^class $s\b" src/ | grep -v ':0' | wc -l)"
done
#  → all zero

grep -n "^class " src/gitco/libs/exporter.py    # → no output; the module has no classes

# 5. F-06 — phantom re-exports poison the package import
sed -i 's|^from gitco.detector import|from ..libs.detector import|' src/gitco/prompts/templates.py
.venv/bin/python -c "import sys; sys.path.insert(0,'src'); import gitco.libs"
#  → ImportError: cannot import name 'ContributionDiscovery' from 'gitco.libs.discovery'

# 6. F-04 — the PyPI name belongs to someone else
pip download gitco==0.0.6 -d /tmp/x --no-deps && pip show gitco
#  → Author: Emmanuel Letremble — "generate git commit messages from the current diff file"

# 7. F-05 — the deleted tests are still in history
git show --numstat cad42cf | awk '$3 ~ /^tests\// {n++; s+=$2} END {print n" files, "s" lines"}'
#  → 36 files, 16570 lines
git show cad42cf^:tests/test_imports.py     # the 22 lines that would have caught everything
git log -1 --format='%ai' cad42cf && git log -1 --format='%ai' 451fd1b
#  → 2025-08-15 13:13:36 -0700  /  2025-08-15 13:22:38 -0700   (nine minutes)

# 8. F-08 — curl -w writes AFTER the body, not before
curl -s -w '%{http_code}\n%{header_json}\n' https://api.github.com/rate_limit | head -1
#  → "{"   ← what int(lines[0]) is handed; ValueError, swallowed into a generic APIError

# 9. F-09 — the secret gate is a no-op
mkdir -p /tmp/g/src && echo 'T="ghp_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"' > /tmp/g/src/leak.py
cd /tmp/g && grep -r  "sk-|pk_|ghp_|gho_|ghu_|ghs_|ghr_" src/; echo "exit=$?"   # → exit=1, no match
         grep -rE "sk-|ghp_" src/;                        echo "exit=$?"        # → exit=0, matches

# 10. F-11/F-12 — every security tool is advisory; the baseline is missing
grep -rn "|| true" .github/workflows/                 # → 9 occurrences
ls .secrets.baseline                                  # → No such file or directory

# 11. F-19 — dead dependencies
grep -rn "^import git$\|^from git import\|tiktoken" src/    # → no output

# 12. Static analysis
ruff check src/                                       # → "All checks passed!"  (7 rule families)
ruff check --select ALL --statistics src/             # → 2,874 violations
ruff check --select ALL --output-format=concise src/ | wc -l

# 13. Bisect when the package broke
for c in cb5270c c6727ee d71824a; do
  git stash -u -q 2>/dev/null; git checkout -q $c
  python -c "import sys; sys.path.insert(0,'src'); import gitco.libs" 2>&1 | tail -1
done

# 14. Enumerate the real command tree (requires the manual repair from steps 5 and the shims)
python - <<'PY'
import sys; sys.path.insert(0,'src')
from gitco._entry import main            # cli.py copied aside to defeat the shadowing
def walk(cmd, p=''):
    for n, sub in sorted(getattr(cmd, 'commands', {}).items()):
        print(p + n); walk(sub, p + '  ')
walk(main)
PY
```

---

# APPENDIX B — FILES REQUIRING IMMEDIATE CHANGE

| File | Change |
|---|---|
| `src/gitco/prompts/templates.py:7` | `gitco.detector` → `..libs.detector` |
| `src/gitco/utils/completion.py:158,175` | `..config` → `..libs.config`; replace `except Exception: pass` with a logged, typed handler |
| `src/gitco/cli.py` | **Delete**; move `main` to `cli/__init__.py` |
| `src/gitco/cli/__init__.py` | Add `main`; register command groups; **remove the `try/except ImportError`** |
| `src/gitco/__main__.py` | **Create** — `from .cli import main; main()` |
| `src/gitco/py.typed` | **Create** — empty file (PEP 561); add to `[tool.setuptools.package-data]` |
| `src/gitco/libs/__init__.py:18-22` | Remove the 4 phantom re-exports; stop eagerly importing the world |
| `src/gitco/cli/core.py` | Rewrite `sync`, `analyze`, `discover`, `status`, `activity`, `logs`, `performance`, `completion`, `validate_repo` against the real APIs; fix `config.repositories.keys()`; move all imports to module top |
| `src/gitco/cli/upstream.py:393,396` | `get_default_branch_name` → `get_default_branch`; `merge_upstream` → `merge_upstream_branch`; make `--repo` a config-name lookup, not a path |
| `src/gitco/libs/github_client.py` | **Delete `SSHGitHubResponse`, `SSHGitHubClient`, `_make_ssh_request`, `create_ssh_github_client`**; single in-process HTTP session; remove `PyGithub` |
| `src/gitco/libs/git_ops.py:206,226,890,2531` | Replace `.git` filesystem inference with `git rev-parse` introspection; add `check=True` to `subprocess.run` |
| `src/gitco/libs/backup.py:~466` | Add the resolve-and-contain path guard; reject symlink and duplicate entries; honor `overwrite_existing` |
| `src/gitco/libs/config.py:597` | XDG config path with a migration shim; nest the 23 `Settings` fields |
| `src/gitco/libs/analyzer.py:429,578` | Remove the hardcoded `gpt-3.5-turbo` default; replace `_parse_text_response` with schema-validated structured output |
| `src/gitco/libs/protocols.py` | **Create** — `SyncService`, `AnalysisService`, `DiscoveryService`, `HealthService` |
| `src/gitco/utils/__init__.py` | Replace the starred `__all__` splat with an explicit list; include `rate_limiter` and `completion` |
| `src/gitco/__init__.py` + `src/gitco/libs/__init__.py` | De-duplicate `__version__`, `__author__`, `__email__`, `__license__`, `__url__`; fix the canonical URL |
| `pyproject.toml` | Rename the distribution; drop `gitpython` + `tiktoken` + `pygithub`; `2 - Pre-Alpha`; fix all 10 URLs; add `mypy`; add `py.typed` to package-data; reconcile with `requirements.txt` |
| `requirements.txt` | Reconcile with `pyproject.toml` or delete in favour of a single source of truth |
| `.github/workflows/ci.yml` | **Create** — full test/lint/type/build/install matrix, required on `main` |
| `.github/workflows/pypi-publish.yml` | Fix `grep -rE`; remove all `\|\| true`; Trusted Publishing (OIDC); fix the `pip index versions` guard |
| `.github/workflows/release.yml` | Replace `actions/create-release@v1`; remove all `\|\| true`; consolidate with `pypi-publish.yml` |
| `.github/workflows/pr-checks.yml` | Remove the `\|\| true` on the link checker; add lint/format/type/test/build gates |
| `.github/dependabot.yml` | Fix `reviewers` / `assignees` to the canonical owner |
| `.github/security/config.yml` | Implement it (real `bandit.yaml`, blocking gates) or delete it |
| `.secrets.baseline` | **Create** |
| `.pre-commit-config.yaml` | Drop `black` for `ruff format`; replace `mirrors-prettier`; bump every hook; enforce in CI |
| `tests/` | **Restore from `cad42cf^`**, then extend with the fixture matrix, failure injection, and property-based suites |
| `tests/test_imports.py` | **Create first** — before anything else |
| `SECURITY.md` | Remove the template boilerplate; fix the version table |
| `docs/QA.md` | Delete, or convert every step into an integration test |
| `docs/cli/*.md` | Regenerate from Click introspection |
| `README.md` | Fix the install command; add a pre-alpha banner; reposition around the wedge; add the "Why not `gh repo sync`?" table |
| `CONTRIBUTING.md` | Add a testing section — it currently has none |
| `ARCHITECTURE.md` | **Create** |
| `docs/security/threat-model.md` | **Create** |
| `docs/adr/` | **Create** |
| `CITATION.cff`, `.editorconfig`, `SUPPORT.md`, lockfile | **Create** |
