import os
import subprocess


def test_p10s_in_subdir(fixtures_dir):
    working_dir = fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'pwd'
    os.chdir(str(working_dir))
    subprocess.check_call("p10s g ..", shell=True)

    assert (fixtures_dir / 'generator_data' / 'p10s_relative_dir' / 'out' / 'simple.tf.json').exists()
