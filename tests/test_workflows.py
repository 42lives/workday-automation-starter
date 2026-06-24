import tempfile
import unittest
from pathlib import Path

from workday_automation_starter.doc_outline import build_doc_outline
from workday_automation_starter.email_digest import build_email_digest, parse_email_items
from workday_automation_starter.file_plan import build_file_plan, classify_file
from workday_automation_starter.report_draft import build_report_draft, parse_calendar_events
from workday_automation_starter.smart_clean import (
    SmartCleanOptions,
    apply_smart_clean_plan,
    build_smart_clean_plan,
    matches_rules,
)
from workday_automation_starter.trend_digest import build_trend_digest, parse_trend_items, score_importance


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

    def test_smart_clean_respects_include_exclude_and_protects_private_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "report.pdf").write_text("placeholder\n", encoding="utf-8")
            (root / "photo.png").write_text("placeholder\n", encoding="utf-8")
            (root / "private").mkdir()
            (root / "private" / "secret-note.txt").write_text("placeholder\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=fake\n", encoding="utf-8")

            plan = build_smart_clean_plan(
                root,
                SmartCleanOptions(include=["*.pdf", "*.png", "private/*", ".env"], exclude=["private/*"]),
            )

        planned = {action["relative_source"] for action in plan["actions"]}
        protected = {item["path"] for item in plan["protected"]}
        skipped = {item["path"] for item in plan["skipped"]}
        self.assertEqual(planned, {"report.pdf", "photo.png"})
        self.assertEqual(protected, {".env"})
        self.assertEqual(skipped, {"private/secret-note.txt"})

    def test_smart_clean_apply_moves_files_and_keeps_manifest_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source = root / "notes.md"
            source.write_text("# Notes\n", encoding="utf-8")

            plan = build_smart_clean_plan(root, SmartCleanOptions(include=["*.md"], exclude=[]))
            applied = apply_smart_clean_plan(plan)

            actions = applied["actions"]
            self.assertTrue(applied["applied"])
            self.assertFalse(source.exists())
            self.assertEqual(len(actions), 1)
            self.assertTrue(Path(actions[0]["target"]).exists())

    def test_smart_clean_rule_matching_supports_only_and_excluded_patterns(self) -> None:
        self.assertTrue(matches_rules("reports/june.pdf", ["reports/*"], []))
        self.assertFalse(matches_rules("images/card.png", ["reports/*"], []))
        self.assertFalse(matches_rules("reports/private.pdf", ["reports/*"], ["reports/private.*"]))

    def test_daily_report_combines_sample_email_and_calendar_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            emails = root / "emails.txt"
            calendar = root / "calendar.csv"
            emails.write_text(
                "From: partner@example.test\n"
                "Subject: Proposal review\n"
                "Body: Please review the proposal and send comments.\n",
                encoding="utf-8",
            )
            calendar.write_text(
                "date,time,title,status,notes\n"
                "2026-06-24,09:30,Partner sync,completed,Reviewed project status\n"
                "2026-06-25,14:00,Planning meeting,scheduled,Prepare agenda\n",
                encoding="utf-8",
            )

            events = parse_calendar_events(calendar)
            markdown = build_report_draft(emails, calendar, "weekly", "markdown")
            json_output = build_report_draft(emails, calendar, "weekly", "json")

        self.assertEqual(len(events), 2)
        self.assertIn("# Weekly Work Report Draft", markdown)
        self.assertIn("Proposal review", markdown)
        self.assertIn("Planning meeting", markdown)
        self.assertIn('"follow_ups": 1', json_output)

    def test_trend_digest_filters_scores_and_exports_notion_ready_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            trends = Path(tmpdir) / "trends.csv"
            trends.write_text(
                "date,topic,source,title,url,summary\n"
                "2026-06-24,AI,Example News,OpenAI automation workflow,https://example.test/a,"
                "OpenAI released an automation workflow. It helps teams review documents. It may affect office work.\n"
                "2026-06-24,Finance,Example News,Market update,https://example.test/b,"
                "Markets moved today. Analysts are watching rates. No automation impact noted.\n",
                encoding="utf-8",
            )

            items = parse_trend_items(trends)
            markdown = build_trend_digest(trends, "AI", 10, "markdown")
            csv_output = build_trend_digest(trends, "AI", 10, "csv")

        self.assertEqual(len(items), 2)
        self.assertGreater(score_importance(items[0]), score_importance(items[1]))
        self.assertIn("# Trend Digest: AI", markdown)
        self.assertIn("OpenAI automation workflow", markdown)
        self.assertNotIn("Market update", markdown)
        self.assertIn("summary_1,summary_2,summary_3", csv_output)


if __name__ == "__main__":
    unittest.main()
