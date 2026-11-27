import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import envvault


class TestEnvVault(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.vault_path = self.base_dir / "vault.enc.json"
        self.path_patcher = patch.object(envvault, "STORE_PATH", self.vault_path)
        self.env_patcher = patch.dict(os.environ, {"ENVVAULT_PASS": "test-passphrase-123"}, clear=False)
        self.path_patcher.start()
        self.env_patcher.start()

    def tearDown(self) -> None:
        self.env_patcher.stop()
        self.path_patcher.stop()
        self.temp_dir.cleanup()

    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        exit_code = 0
        with patch("sys.argv", ["envvault", *argv]), redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                envvault.main()
            except SystemExit as exc:
                exit_code = exc.code if isinstance(exc.code, int) else 1
        return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()

    def test_add_list_search_get_and_delete(self) -> None:
        code, out, _ = self.run_cli(["add", "API_KEY", "secret_abc_123", "--tags", "api,prod"])
        self.assertEqual(code, 0)
        self.assertIn("Encrypted & saved 'API_KEY'", out)

        raw_disk = self.vault_path.read_text(encoding="utf-8")
        self.assertNotIn("secret_abc_123", raw_disk)

        code, out, _ = self.run_cli(["list", "--tag", "prod"])
        self.assertEqual(code, 0)
        self.assertIn("API_KEY", out)

        code, out, _ = self.run_cli(["search", "api"])
        self.assertEqual(code, 0)
        self.assertIn("API_KEY", out)

        code, out, _ = self.run_cli(["get", "API_KEY"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "secret_abc_123")

        code, out, _ = self.run_cli(["delete", "API_KEY"])
        self.assertEqual(code, 0)
        self.assertIn("Deleted 'API_KEY'", out)

        code, _, _ = self.run_cli(["get", "API_KEY"])
        self.assertNotEqual(code, 0)

    def test_wrong_passphrase_fails(self) -> None:
        code, _, _ = self.run_cli(["add", "DB_PASS", "hunter2"])
        self.assertEqual(code, 0)

        with patch.dict(os.environ, {"ENVVAULT_PASS": "wrong-passphrase"}, clear=False):
            code, _, err = self.run_cli(["list"])
            self.assertNotEqual(code, 0)
            self.assertIn("Invalid passphrase", err)

    def test_overwrite_existing_entry(self) -> None:
        self.run_cli(["add", "TOKEN", "old_val", "--tags", "v1"])
        self.run_cli(["add", "TOKEN", "new_val", "--tags", "v2"])

        code, out, _ = self.run_cli(["get", "TOKEN"])
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "new_val")

    def test_import_and_export_dotenv(self) -> None:
        sample_env = self.base_dir / "sample.env"
        sample_env.write_text(
            "# Comment line\nAPP_ENV=production\nAPI_SECRET=\"my secret key\"\n",
            encoding="utf-8",
        )

        code, out, _ = self.run_cli(["import-env", str(sample_env), "--tags", "backend"])
        self.assertEqual(code, 0)
        self.assertIn("Imported 2 entries", out)

        exported_env = self.base_dir / "exported.env"
        code, out, _ = self.run_cli(["export-env", str(exported_env), "--tag", "backend"])
        self.assertEqual(code, 0)
        self.assertIn("Exported 2 entries", out)

        content = exported_env.read_text(encoding="utf-8")
        self.assertIn("APP_ENV=production", content)
        self.assertIn('API_SECRET="my secret key"', content)


if __name__ == "__main__":
    unittest.main()