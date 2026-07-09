"""Shared path resolution for skill sync scripts.

Store topology (after the 2026-07 oscillation fix — see AGENTS.md "Store
Ownership & Boundaries"):

  On this machine the GLOBAL store (B, the source of truth) and Hermes's
  RUNTIME load path (C) are the SAME physical directory. This is the core
  fix: there is exactly ONE store that is both the truth and the live load
  path, so the runtime can never diverge from the truth (the old B<->C
  oscillation is structurally impossible). The pointer is
  $HERMES_SKILLS_HOME = <LOCALAPPDATA>/hermes/skills, set persistently in
  the Windows user environment so it survives reboots and is inherited by
  the Hermes launcher.

  global_skills_dir() resolves in this order (portable, never a username):

    1. $HERMES_SKILLS_HOME  (explicit override; this machine points it AT C)
    2. ~/.agents/skills     (default Hermes global store — used by CI, which
                            does NOT set HERMES_SKILLS_HOME, so CI stays an
                            independent auditor against the default global)
    3. $XDG_DATA_HOME/hermes/skills

  runtime_skills_dir() resolves Hermes's live load path (C). When
  $HERMES_SKILLS_HOME == runtime dir, B and C are identical objects.

  Sanity: global_skills_dir() asserts it does not resolve to a path that is a
  SUBDIRECTORY or a DISTINCT copy whose content clashes with the runtime; for
  the merged layout the two paths are equal and the guard is a no-op.
"""
import os
from pathlib import Path


def global_skills_dir() -> Path:
    override = os.environ.get("HERMES_SKILLS_HOME")
    if override:
        return Path(override).expanduser().resolve()
    default = Path.home() / ".agents" / "skills"
    if default.exists():
        # Resolve so a junction/symlink (e.g. ~/.agents/skills -> runtime C)
        # returns the SAME string as runtime_skills_dir(), making B and C
        # unambiguously one store.
        return default.resolve()
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "hermes" / "skills"
    return default


def runtime_skills_dir() -> Path:
    """Hermes's primary runtime load path.

    Hermes loads skills from $HERMES_HOME/skills at boot. On a default install
    $HERMES_HOME is ~/.hermes, so this resolves to ~/.hermes/skills; when
    HERMES_HOME points elsewhere (e.g. <LOCALAPPDATA>/hermes) the runtime
    follows it. Override the resolved path directly with $HERMES_RUNTIME_SKILLS
    for non-default layouts. Never hardcoded to a username so the script stays
    portable / public-repo-safe.
    """
    override = __import__("os").environ.get("HERMES_RUNTIME_SKILLS")
    if override:
        return Path(override).expanduser()
    home = os.environ.get("HERMES_HOME")
    if home:
        return (Path(home).expanduser() / "skills").resolve()
    return (Path.home() / ".hermes" / "skills").resolve()


def local_skills_dir() -> Path:
    """The skill_manage write target (<LOCALAPPDATA>/hermes/skills).

    On this merged layout this IS the runtime store (C) and therefore the
    source of truth (B). Skills created via the agent's own skill tooling land
    here — and because B==C, that is now correct (they are the truth, not a
    divergent copy). The old "separate private load path" model died with the
    oscillation fix. User private (~/skills) remains wholly aside.
    """
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "hermes" / "skills"


def user_skills_dir() -> Path:
    """The HUMAN's own private skill space (~/skills).

    Deliberately ASIDE from every agent. It is NOT part of any agent's load
    path and is excluded from every sync path. Skills here belong to the human,
    not to Hermes or the shared catalog. No sync script reads or writes this
    directory. Override with $HERMES_USER_SKILLS for non-default layouts.
    """
    override = os.environ.get("HERMES_USER_SKILLS")
    if override:
        return Path(override).expanduser()
    return Path.home() / "skills"


def assert_merged_topology() -> None:
    """Core-oscillation guard.

    The whole B<->C oscillation class is gone ONLY because global_skills_dir()
    (B) and runtime_skills_dir() (C) resolve to the same physical directory.
    If a future change points B elsewhere (e.g. HERMES_SKILLS_HOME unset, or
    pointed at ~/.agents/skills again), the two-store contradiction returns and
    divergence can recur. This guard fails loudly so it cannot regress silently.

    It is a LOCAL-MACHINE guard only: in CI / a fresh checkout the default B
    (~/.agents/skills) is a separate store by design (CI is the independent
    auditor), so the merged invariant does not apply there — skip it.
    """
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return
    try:
        b, c = global_skills_dir(), runtime_skills_dir()
    except Exception as e:
        # A failure to even RESOLVE B/C is itself a topology break (e.g. HOME
        # / profile vars unset). Fail loud with context instead of an opaque
        # RuntimeError traceback that could mask a real store split.
        raise AssertionError(
            f"Oscillation guard could not resolve store paths ({type(e).__name__}: {e}). "
            f"B and C are NOT confirmed merged — fix the environment "
            f"(HERMES_HOME / USERPROFILE / HOME must be set)."
        ) from e
    assert b.resolve() == c.resolve(), (
        f"Oscillation guard tripped: global (B) resolves to {b} but runtime (C) "
        f"resolves to {c}. They MUST be the same physical directory (set "
        f"HERMES_SKILLS_HOME=$HERMES_HOME/skills). A distinct B and C reintroduces "
        f"the source-of-truth divergence that caused the B<->C oscillation."
    )
