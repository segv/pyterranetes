import json
import subprocess
import signal
import pytest
import time
from contextlib import contextmanager


@pytest.fixture
def simple_p10s(fixtures_dir):
    return fixtures_dir / 'generator_data' / 'simple' / 'simple.p10s'


@pytest.fixture
def pwd_p10s(fixtures_dir):
    return fixtures_dir / 'generator_data' / 'simple' / 'pwd.p10s'


@contextmanager
def p10s_process(args, cwd=None):
    with subprocess.Popen(["p10s"] + args, cwd=str(cwd)) as p10s:
        time.sleep(1)
        try:
            yield
        finally:
            p10s.terminate()


class LoopExhausted(Exception):
    pass


def wait_until(condition):
    for i in range(50):
        v = condition()
        if v:
            return v
        time.sleep(0.1)
    else:
        raise LoopExhausted()


@pytest.mark.flaky(reruns=3, reruns_delay=5)
@pytest.mark.parametrize("signum", [signal.SIGTERM, signal.SIGINT])
def test_watcher_signal(tmp_dir, signum):
    proc = subprocess.Popen(["p10s", "watch"], cwd=str(tmp_dir))
    try:
        proc.send_signal(signum)

        def done():
            proc.poll()
            return proc.returncode is not None

        try:
            wait_until(done)
        except LoopExhausted:
            pytest.fail("watch failed to terminate")

        if proc.returncode != -signum:
            pytest.fail("watch was not terminted with %s (returncode: %s)" % (signum, proc.returncode))
    finally:
        proc.kill()


@pytest.mark.flaky(reruns=3, reruns_delay=5)
@pytest.mark.slow
def test_watcher_file_create(tmp_dir, simple_p10s):
    with p10s_process(["watch", "."], tmp_dir):
        new = tmp_dir / 'simple.p10s'
        new.write_bytes(simple_p10s.read_bytes())

        out = new.with_suffix('.tf.json')
        expected = simple_p10s.with_suffix('.tf.json')

        try:
            wait_until(lambda: out.exists())
            assert out.read_text() == expected.read_text()
        except LoopExhausted:
            pytest.fail("didn't build for newly created file %s in %s" % (new, tmp_dir))


@pytest.mark.flaky(reruns=3, reruns_delay=5)
@pytest.mark.slow
def test_watcher_move(tmp_dir, simple_p10s):
    dst = tmp_dir / 'simple.p10s'
    dst.write_bytes(simple_p10s.read_bytes())

    with p10s_process(["watch", "."], tmp_dir):
        new_dst = tmp_dir / 'simple2.p10s'
        dst.rename(new_dst)
        out = new_dst.with_suffix('.tf.json')
        expected = simple_p10s.with_suffix('.tf.json')

        try:
            wait_until(lambda: out.exists())
            assert out.read_text() == expected.read_text()
        except LoopExhausted:
            pytest.fail("didn't build for moved file %s in %s" % (new_dst, tmp_dir))


@pytest.mark.flaky(reruns=3, reruns_delay=10)
@pytest.mark.slow
def test_watcher_modify(tmp_dir, simple_p10s, pwd_p10s):
    dst = tmp_dir / 'simple.p10s'
    dst.write_bytes(simple_p10s.read_bytes())

    with p10s_process(["watch", "."], tmp_dir):
        dst.write_bytes(pwd_p10s.read_bytes())
        out = dst.with_suffix('.tf.json')

        try:
            wait_until(lambda: out.exists())
            out_json = json.loads(out.read_text())

            assert out_json == {
                'data': {
                    'bar': {
                        'foo': {
                            'pwd': str(tmp_dir)
                        }}
                }
            }
        except LoopExhausted:
            pytest.fail("didn't build for modified file %s in %s" % (dst, tmp_dir))
