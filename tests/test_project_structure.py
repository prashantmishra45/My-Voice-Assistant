from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ProjectStructureTests(unittest.TestCase):
    def test_required_directories_exist(self) -> None:
        required = [
            "src",
            "docs",
            "docs/features",
            "docs/journal",
            "docs/decisions",
            "docs/contributions",
            "architecture",
            "research",
            "setup",
            "tests",
        ]
        for directory in required:
            with self.subTest(directory=directory):
                self.assertTrue((ROOT / directory).is_dir())

    def test_required_documents_exist(self) -> None:
        required = [
            "README.md",
            "PROJECT_CONTEXT.md",
            "CHANGELOG.md",
            "setup/external_requirements.md",
            "architecture/scalable_architecture.md",
            "docs/roadmap.md",
            "docs/features/basic_voice_conversation.md",
        ]
        for document in required:
            with self.subTest(document=document):
                self.assertTrue((ROOT / document).is_file())


if __name__ == "__main__":
    unittest.main()

