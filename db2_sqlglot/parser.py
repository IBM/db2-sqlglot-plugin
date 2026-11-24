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

    # Map Db2-specific type keywords to their base types for parsing.
    # This allows the parser to recognize GRAPHIC, VARGRAPHIC, and DBCLOB as
    # valid types.
    TYPE_TOKENS = {
        *parser.Parser.TYPE_TOKENS,
        # Db2-specific types will be parsed as DataType with the name preserved
    }

    # The isolation-clause is kept in an arg of its own rather than in "options":
    # other dialects write query options in their own syntax (T-SQL as OPTION(...)),
    # and DELETE has no options.
    QUERY_MODIFIER_PARSERS = {
        **parser.Parser.QUERY_MODIFIER_PARSERS,
        TokenType.WITH: lambda self: ("isolation", self._parse_isolation_clause()),
    }

    SET_OP_MODIFIERS = {*parser.Parser.SET_OP_MODIFIERS, "isolation"}

    STATEMENT_PARSERS = {
        **parser.Parser.STATEMENT_PARSERS,
        TokenType.DELETE: lambda self: self._parse_isolation(self._parse_delete()),
        TokenType.UPDATE: lambda self: self._parse_isolation(self._parse_update()),
    }

    def _parse_isolation(self, expression: exp.Expression) -> exp.Expression:
        """
        Parse the isolation-clause at the end of an UPDATE or DELETE statement.
        """
        expression.set("isolation", self._parse_isolation_clause())
        return expression

    def _parse_isolation_clause(self) -> t.Optional[exp.Var]:
        """
        Parse the isolation-clause WITH UR, WITH CS, WITH RR or WITH RS.
        """
        index = self._index
        if self._match(TokenType.WITH) and self._match_texts(("UR", "CS", "RR", "RS")):
            return exp.var(self._prev.text.upper())
        self._retreat(index)
        return None
