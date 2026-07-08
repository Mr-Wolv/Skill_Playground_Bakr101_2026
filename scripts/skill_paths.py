"""Shared path resolution for skill sync scripts.

The "global" skill store is the user's local agent skill directory. It must
never be hardcoded to a specific machine/username (this repo is public). Resolve
it in this order:

  1. $HERMES_SKILLS_HOME  (explicit override; CI or non-default layout)
  2. ~/.agents/skills     (default Hermes global store)
  3. $XDG_DATA_HOME/hermes/skills

This keeps the scripts portable and username-free in the source.
"""
from pathlib import Path


def global_skills_dir() -> Path:
    override = __import__("os").environ.get("HERMES_SKILLS_HOME")
    if override:
        return Path(override).expanduser()
    default = Path.home() / ".agents" / "skills"
    if default.exists():
        return default
    xdg = __import__("os").environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "hermes" / "skills"
    return default


def runtime_skills_dir() -> Path:
    """Hermes's primary runtime load path (~/.hermes/skills).

    This is what Hermes actually loads skills from at boot. Override with
    $HERMES_RUNTIME_SKILLS for non-default layouts. Never hardcoded to a
    username so the script stays portable / public-repo-safe.
    """
    override = __import__("os").environ.get("HERMES_RUNTIME_SKILLS")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".hermes" / "skills"


def local_skills_dir() -> Path:
    """The skill_manage write target (<LOCALAPPDATA>/hermes/skills).

    Distinct from the runtime and mirror stores. Skills created via the agent's
    own skill tooling land here. Treated as a SEPARATE, PRIVATE load path that
    sync routines must never modify or "correct" against the mirror.
    """
    local = __import__("os").environ.get("LOCALAPPDATA")
    base = Path(local) if local else Path.home() / "AppData" / "Local"
    return base / "hermes" / "skills"


def user_skills_dir() -> Path:
    """The HUMAN's own private skill space (~/skills).

    Deliberately ASIDE from every agent. It is NOT part of any agent's load
    path and is excluded from every sync path. Skills here belong to the human,
    not to Hermes or the shared catalog. No sync script reads or writes this
    directory. Override with $HERMES_USER_SKILLS for non-default layouts.
    """
    override = __import__("os").environ.get("HERMES_USER_SKILLS")
    if override:
        return Path(override).expanduser()
    return Path.home() / "skills"
