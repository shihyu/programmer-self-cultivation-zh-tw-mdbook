import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.publish_pages import publish_pages


def git(*args, cwd=None):
    return subprocess.run(
        ["git", *map(str, args)], cwd=cwd, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


class PublishingTests(unittest.TestCase):
    def test_publish_pages_pushes_only_built_html_and_updates_branch(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as temporary:
            base = Path(temporary)
            remote = base / "remote.git"
            project = base / "project"
            git("init", "--bare", "--initial-branch=main", remote)
            project.mkdir()
            git("init", "--initial-branch=main", cwd=project)
            git("config", "user.name", "Test", cwd=project)
            git("config", "user.email", "test@example.com", cwd=project)
            (project / "README.md").write_text("source only", encoding="utf-8")
            git("add", "README.md", cwd=project)
            git("commit", "-m", "Source", cwd=project)
            git("remote", "add", "origin", remote, cwd=project)
            git("push", "-u", "origin", "main", cwd=project)

            output = project / "book"
            output.mkdir()
            (output / "index.html").write_text("first build", encoding="utf-8")
            (output / "chapters").mkdir()
            (output / "chapters/1.html").write_text("chapter", encoding="utf-8")

            publish_pages(project)
            self.assertEqual(git("--git-dir", remote, "show", "gh-pages:index.html"), "first build")
            self.assertEqual(git("--git-dir", remote, "show", "gh-pages:chapters/1.html"), "chapter")
            self.assertEqual(git("--git-dir", remote, "show", "gh-pages:.nojekyll"), "")
            self.assertNotIn("README.md", git("--git-dir", remote, "ls-tree", "--name-only", "gh-pages"))

            (output / "index.html").write_text("second build", encoding="utf-8")
            publish_pages(project)
            self.assertEqual(git("--git-dir", remote, "show", "gh-pages:index.html"), "second build")
            self.assertEqual(git("--git-dir", remote, "rev-list", "--count", "gh-pages"), "2")

    def test_publish_pages_requires_built_html(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as temporary:
            with self.assertRaises(FileNotFoundError):
                publish_pages(Path(temporary))


if __name__ == "__main__":
    unittest.main()
