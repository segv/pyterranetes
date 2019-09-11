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
