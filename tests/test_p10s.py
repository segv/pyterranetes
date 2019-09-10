import os
import subprocess
import re


def test_p10s_in_subdir(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    subprocess.run(["p10s", "g", ".."], check=True)

    assert (fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'out' / 'simple.tf.json').exists()


def test_p10s_verbose(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    proc = subprocess.run(["p10s", "g", "--verbose", ".."],
                          check=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    assert re.match("Compiling .*?/tests/fixtures/generator_data/p10s_relative_dir/simple.p10s\n  Rendering <p10s.terraform.Context> to out/simple.tf.json in .*?/tests/fixtures/generator_data/p10s_relative_dir\n", proc.stdout.decode("utf-8"))


def test_terraform_subcommand(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    proc = subprocess.run(["env", "PYTERRANETES_TERRAFORM=echo",
                           "p10s", "terraform",
                           "this", "is", "a test"],
                          check=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    assert proc.stdout.decode("utf-8") == "this is a test\n"


def test_tf_fail(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    proc = subprocess.run(["env", "PYTERRANETES_TERRAFORM=false",
                           "p10s", "tf", "plan"],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    assert proc.returncode == 1
    assert proc.stdout.decode("utf-8") == ""
