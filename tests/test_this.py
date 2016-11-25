import pytest

from . import unit
from chain_caller import this, resolve


@pytest.fixture
def _obj():
    class Some:
        string = 'string'
        integer = 10
        lst = [1, 1.5, 'String']
        dct = {
            'dict': {},
            'string': 'String',
            'integer': 10,
        }

        def chained(self):
            return self

        def __getattr__(self, name):
            return name

        def int_val(self, some):
            return self.integer * some

        @property
        def some(self):
            return self.lst

    return Some()


@unit
def test_magic(_obj):
    assert 10 == resolve(this.dct['integer'], _obj)
    assert 'string' == resolve(this.dct['string'].lower(), _obj)
    assert 1 == resolve(this.lst[0], _obj)
    assert 1.5 == resolve(this.some[1], _obj)
    assert None is resolve(this.dct['dict'].get('http', None), _obj)
    assert 'name' == resolve(this.name, _obj)
    assert True == resolve(this.name == 'name', _obj)


@unit
def test_func_calls(_obj):
    assert 100 == resolve(this.int_val(10), _obj)
    assert 100 == resolve(this.int_val(this.integer), _obj)
    assert _obj == resolve(this.chained().chained(), _obj)


@unit
def test_math(_obj):
    assert 100 == resolve(this.integer + 90, _obj)
    assert 100 == resolve(this.integer * 10, _obj)
    assert 100 == resolve(this.dct['integer'] * 10, _obj)
    assert 100 == resolve(this.dct['integer'] * 10, _obj)
    assert 100 == resolve(90 + this.integer, _obj)
    assert 100 == resolve(10 * this.integer, _obj)
    assert 100 == resolve(10 * this, 10)


@unit
def test_immutability(_obj):
    assert resolve(this, _obj) is resolve(this, _obj) is _obj
    assert resolve(this.integer, _obj) is resolve(this.integer, _obj)
    assert resolve(this.chained().chained(), _obj) \
        is resolve(this.chained(), _obj)
