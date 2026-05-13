from __future__ import annotations

from sqlglot import exp, parser
from sqlglot.helper import seq_get


class Db2Parser(parser.Parser):
    FUNCTIONS = {
        **parser.Parser.FUNCTIONS,
        "CHAR": exp.Cast.from_arg_list,
        "DAYOFWEEK": lambda args: exp.Extract(
            this=exp.var("DAYOFWEEK"), expression=seq_get(args, 0)
        ),
        "DAYOFYEAR": lambda args: exp.Extract(
            this=exp.var("DAYOFYEAR"), expression=seq_get(args, 0)
        ),
        "POSSTR": lambda args: exp.StrPosition(this=seq_get(args, 0), substr=seq_get(args, 1)),
        "VARCHAR_FORMAT": lambda args: exp.TimeToStr(
            this=seq_get(args, 0), format=seq_get(args, 1)
        ),
    }
    
    # Map DB2-specific type keywords to their base types for parsing
    # This allows the parser to recognize GRAPHIC, VARGRAPHIC, DBCLOB as valid types
    TYPE_TOKENS = {
        *parser.Parser.TYPE_TOKENS,
        # DB2-specific types will be parsed as DataType with the name preserved
    }
