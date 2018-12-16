from p10s.base import BaseContext
from pathlib import Path


def test_context_output_type1():
    c = BaseContext(output=".")
    assert isinstance(c.output, Path)


def test_context_output_type2():
    c = BaseContext(output=Path(".").resolve())
    assert isinstance(c.output, Path)


class DummyContext(BaseContext):
    output_file_extension = '.txt'


def test_context_input_type():
    c = DummyContext(input="foo.p10s")
    assert isinstance(c.input, Path)


def test_context_input_output():
    c = DummyContext(input="foo.p10s")
    assert c.output == Path('foo.txt')
