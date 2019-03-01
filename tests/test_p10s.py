import os
import subprocess
import re


def test_p10s_in_subdir(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    subprocess.check_call("p10s g ..", shell=True)

    assert (fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'out' / 'simple.tf.json').exists()


def test_p10s_verbose(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    ret = subprocess.check_output("p10s g --verbose ..",
                                  shell=True,
                                  stderr=subprocess.STDOUT)
    ret = ret.decode("utf-8")
    assert re.match("Compiling .*?/tests/fixtures/generator_data/p10s_relative_dir/simple.p10s\n  Rendering <p10s.terraform.Context> to out/simple.tf.json in .*?/tests/fixtures/generator_data/p10s_relative_dir\n", ret)
