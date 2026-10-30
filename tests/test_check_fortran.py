import shutil
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
SCRIPT = HERE.parent / "plugins/fortls-lsp/skills/fortran/scripts/check_fortran.py"


def run(*args, cwd=FIX):
    r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


@unittest.skipUnless(shutil.which("gfortran"), "gfortran not installed")
class CheckFortran(unittest.TestCase):
    def test_clean_file_passes(self):
        rc, out, _ = run("clean/hello.f90", "--root", "clean", "--std", "f2018")
        self.assertEqual(rc, 0, out)
        self.assertIn("1 file(s), 0 error(s), 0 warning(s)", out)

    def test_undeclared_variable_is_an_error(self):
        rc, out, _ = run("undeclared/solver.f90", "--root", "undeclared")
        self.assertEqual(rc, 1, out)
        self.assertRegex(out, r"undeclared/solver\.f90:6:\d+: error: Symbol 'y' at \(1\) has no IMPLICIT type")

    def test_fixed_form_by_extension(self):
        rc, out, _ = run("fixed/legacy.f", "--root", "fixed")
        self.assertEqual(rc, 0, out)

    def test_preprocessor_for_uppercase_extension(self):
        rc, out, _ = run("preproc/flags.F90", "--root", "preproc", "-D", "USE_FAST")
        self.assertEqual(rc, 0, out)

    def test_modules_are_checked_in_dependency_order(self):
        rc, out, _ = run("modules/main.f90", "--root", "modules")
        self.assertEqual(rc, 0, out)
        self.assertIn("1 file(s), 0 error(s)", out)

    def test_directory_argument_checks_every_file(self):
        rc, out, _ = run("modules", "--root", "modules")
        self.assertEqual(rc, 0, out)
        self.assertIn("3 file(s)", out)

    def test_fortls_config_sets_defines_and_exclusions(self):
        rc, out, _ = run("config")
        self.assertEqual(rc, 0, out)
        self.assertIn("1 file(s), 0 error(s)", out)
        self.assertNotIn("broken", out)

    def test_warnings_do_not_fail(self):
        rc, out, _ = run("warning/warn.f90", "--root", "warning")
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"warning/warn\.f90:3:\d+: warning: Unused variable 'unused'")

    def test_dependency_error_is_reported_on_the_dependency(self):
        tmp = Path(self.id().replace(".", "_"))
        work = FIX.parent / "_tmp" / tmp
        shutil.rmtree(work, ignore_errors=True)
        shutil.copytree(FIX / "modules", work)
        (work / "src/consts.f90").write_text("module consts\n  implicit none\n  integer, parameter :: dp = kind(1.0d0)\n  z = 1\nend module consts\n")
        try:
            rc, out, _ = run("main.f90", "--root", ".", cwd=work)
            self.assertEqual(rc, 1, out)
            self.assertIn("[in a module this file needs]", out)
        finally:
            shutil.rmtree(FIX.parent / "_tmp", ignore_errors=True)

    def test_project_tree_is_not_written(self):
        before = sorted(p for p in (FIX / "modules").rglob("*"))
        run("modules", "--root", "modules")
        self.assertEqual(before, sorted(p for p in (FIX / "modules").rglob("*")))


class CheckFortranWithoutCompiler(unittest.TestCase):
    def test_missing_compiler_exits_2(self):
        rc, _, err = run("clean/hello.f90", "--fc", "no-such-gfortran")
        self.assertEqual(rc, 2)
        self.assertIn("not found", err)

    def test_missing_path_exits_2(self):
        rc, _, err = run("nope.f90")
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
