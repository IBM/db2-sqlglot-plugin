# -------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp.                                                               #
#                                                                                                 #
#  The following source code ("Sample") is owned by International Business Machines Corporation   #
#  or one of its subsidiaries ("IBM") and is copyrighted and licensed, not sold. You may use,     #
#  copy, modify, and distribute the Sample in any form without payment to IBM, for the purpose    #
#  of assisting you in the creation of Python applications using the ibm_db library.              #
#                                                                                                 #
#  The Sample code is provided to you on an "AS IS" basis, without warranty of any kind. IBM      #
#  HEREBY EXPRESSLY DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, INCLUDING, BUT NOT       #
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.    #
#  Some jurisdictions do not allow for the exclusion or limitation of implied warranties, so the  #
#  above limitations or exclusions may not apply to you. IBM shall not be liable for any damages  #
#  you suffer as a result of using, copying, modifying or distributing the Sample, even if IBM    #
#  has been advised of the possibility of such damages.                                           #
# -------------------------------------------------------------------------------------------------#

from __future__ import annotations

import typing as t

from sqlglot import exp, parser
from sqlglot.helper import seq_get
from sqlglot.tokens import TokenType

# Units of a Db2 labeled duration (e.g. CURRENT DATE + 3 DAYS), singular and plural, mapped to
# the singular unit stored on exp.Interval.
# https://www.ibm.com/docs/en/db2/12.1?topic=expressions-datetime-operations-durations
LABELED_DURATION_UNITS = {
    f"{unit}{suffix}": unit
    for unit in ("YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND", "MICROSECOND")
    for suffix in ("", "S")
}

_ADDITIVE = (TokenType.PLUS, TokenType.DASH)


class Db2Parser(parser.Parser):
    # Db2 application-period temporal tables: FOR BUSINESS_TIME AS OF / FROM ... TO / BETWEEN
    VERSION_PHRASES = {
        **parser.Parser.VERSION_PHRASES,
        ("FOR", "BUSINESS_TIME"): "BUSINESS_TIME",
    }

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

    # Map Db2-specific type keywords to their base types for parsing.
    # This allows the parser to recognize GRAPHIC, VARGRAPHIC, and DBCLOB as
    # valid types.
    TYPE_TOKENS = {
        *parser.Parser.TYPE_TOKENS,
        # Db2-specific types will be parsed as DataType with the name preserved
    }

    def _parse_factor(self, *args: t.Any, **kwargs: t.Any) -> t.Optional[exp.Expr]:
        """Parse a factor, then a Db2 labeled duration unit that follows it (``3 DAYS``).

        A duration is only recognised as an operand of ``+`` or ``-``: right after one of them,
        or directly before one (``3 MONTHS + d``). Elsewhere a unit word keeps its old meaning,
        e.g. a column alias in ``SELECT 3 DAYS FROM t``.
        """
        after_operator = self._prev is not None and self._prev.token_type in _ADDITIVE
        this = super()._parse_factor(*args, **kwargs)
        if this is None or not self._curr:
            return this

        unit = LABELED_DURATION_UNITS.get(self._curr.text.upper())
        if not unit or self._curr.token_type in (TokenType.STRING, TokenType.IDENTIFIER):
            return this
        if self._next and self._next.token_type == TokenType.L_PAREN:
            return this  # a function call such as DAYS(d), not a duration
        if not after_operator and not (self._next and self._next.token_type in _ADDITIVE):
            return this

        self._advance()
        return self.expression(exp.Interval(this=this, unit=exp.var(unit)))
