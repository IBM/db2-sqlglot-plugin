from importlib.metadata import PackageNotFoundError, version as get_version

from db2_sqlglot.dialect import Db2

try:
    version = get_version("db2-sqlglot-dialect")
except PackageNotFoundError:
    version = "0.0.0"

__version__ = version
__all__ = ["Db2"]
