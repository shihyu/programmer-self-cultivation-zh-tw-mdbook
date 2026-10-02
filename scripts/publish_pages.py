"""Push the locally built mdBook HTML to the gh-pages branch."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(cwd), *map(str, args)],
        capture_output=True, text=True,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def _branch_exists(cwd: Path, branch: str) -> bool:
    return _git(cwd, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0


def publish_pages(project_root: Path) -> None:
    """Publish book/ as the root of a separate gh-pages branch."""
    root = project_root.resolve()
    book = root / "book"
    if not (book / "index.html").is_file():
        raise FileNotFoundError(f"Build the HTML book first: {book / 'index.html'}")
    if (book / ".git").exists():
        raise ValueError("The generated book must not contain a .git entry")
    top = Path(_git(root, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    if top != root:
        raise ValueError(f"Project must be the Git repository root: {root}")
    _git(root, "remote", "get-url", "origin")

    with tempfile.TemporaryDirectory(prefix="mdbook-pages-") as temporary:
        worktree = Path(temporary) / "worktree"
        _git(root, "worktree", "add", "--detach", str(worktree), "HEAD")
        try:
            if not _branch_exists(root, "gh-pages"):
                remote = _git(root, "ls-remote", "--exit-code", "--heads", "origin", "gh-pages", check=False)
                if remote.returncode == 0:
                    _git(root, "fetch", "origin", "gh-pages:refs/heads/gh-pages")
                elif remote.returncode != 2:
                    raise RuntimeError(remote.stderr.strip() or "Could not inspect remote gh-pages branch")

            if _branch_exists(root, "gh-pages"):
                _git(worktree, "switch", "gh-pages")
            else:
                _git(worktree, "switch", "--orphan", "gh-pages")

            for entry in worktree.iterdir():
                if entry.name == ".git":
                    continue
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
            shutil.copytree(book, worktree, dirs_exist_ok=True)
            (worktree / ".nojekyll").touch()
            _git(worktree, "add", "--all")

            changed = _git(worktree, "diff", "--cached", "--quiet", check=False).returncode
            if changed not in (0, 1):
                raise RuntimeError("Could not inspect the Pages changes")
            if changed:
                name = _git(root, "config", "user.name", check=False).stdout.strip() or "shihyu"
                email = _git(root, "config", "user.email", check=False).stdout.strip() or "shihyu@users.noreply.github.com"
                _git(worktree, "-c", f"user.name={name}", "-c", f"user.email={email}",
                     "commit", "-m", "Deploy mdBook HTML")
            _git(worktree, "push", "origin", "gh-pages")
            print("published book/ to origin/gh-pages")
        finally:
            _git(root, "worktree", "remove", "--force", str(worktree))


if __name__ == "__main__":
    publish_pages(ROOT)
