import tempfile
import unittest
from pathlib import Path

from workday_automation_starter.doc_outline import build_doc_outline
from workday_automation_starter.email_digest import build_email_digest, parse_email_items
from workday_automation_starter.file_plan import build_file_plan, classify_file


class WorkdayAutomationTest(unittest.TestCase):
    def test_file_plan_groups_common_office_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "notes.md").write_text("# Notes\n", encoding="utf-8")
            (root / "deck.pptx").write_text("placeholder\n", encoding="utf-8")
            (root / "data.csv").write_text("a,b\n", encoding="utf-8")
            (root / "image.png").write_text("placeholder\n", encoding="utf-8")

            plan = build_file_plan(root)

        self.assertEqual(plan["summary"]["documents"], 1)
        self.assertEqual(plan["summary"]["presentations"], 1)
        self.assertEqual(plan["summary"]["spreadsheets"], 1)
        self.assertEqual(plan["summary"]["images"], 1)

    def test_file_plan_marks_private_like_files(self) -> None:
        self.assertEqual(classify_file(Path(".env")), "possible_private")
        self.assertEqual(classify_file(Path("private.pem")), "possible_private")

    def test_doc_outline_creates_requested_slide_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            note = Path(tmpdir) / "guide.txt"
            note.write_text(
                "Generative AI Guide. Start with a repeated task. Define the input. "
                "Create a draft. Review the output. Save the workflow.",
                encoding="utf-8",
            )

            outline = build_doc_outline(note, 3)

        self.assertIn("# Presentation Outline", outline)
        self.assertIn("## Slide 1", outline)
        self.assertIn("## Slide 3", outline)

    def test_email_digest_creates_markdown_and_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = Path(tmpdir) / "inbox.txt"
            inbox.write_text(
                "From: teammate@example.test\n"
                "Subject: Draft review\n"
                "Body: Please review the proposal draft before Friday.\n",
                encoding="utf-8",
            )

            items = parse_email_items(inbox)
            markdown = build_email_digest(inbox, "markdown")
            csv_output = build_email_digest(inbox, "csv")

        self.assertEqual(len(items), 1)
        self.assertIn("Review requested material", markdown)
        self.assertIn("sender,subject,summary,next_action", csv_output)


if __name__ == "__main__":
    unittest.main()
