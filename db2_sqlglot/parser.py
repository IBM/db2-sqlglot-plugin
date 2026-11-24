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

from sqlglot import exp, parser
from sqlglot.helper import seq_get
from sqlglot.tokens import TokenType


class Db2DefaultColumnConstraint(exp.Expression, exp.ColumnConstraintKind):
    """
    DEFAULT without a value. Db2 uses the default of the column's data type.
    """

    arg_types = {}


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

    CONSTRAINT_PARSERS = {
        **parser.Parser.CONSTRAINT_PARSERS,
        "DEFAULT": lambda self: self._parse_default(),
        "WITH": lambda self: (
            self._parse_default()
            if self._match_text_seq("DEFAULT")
            else parser.Parser.CONSTRAINT_PARSERS["WITH"](self)
        ),
    }

    def _parse_default(self) -> exp.Expression:
        """
        Parse DEFAULT or WITH DEFAULT, with or without a value.
        """
        if not self._curr or self._match_set((TokenType.COMMA, TokenType.R_PAREN), advance=False):
            return self.expression(Db2DefaultColumnConstraint())
        return parser.Parser.CONSTRAINT_PARSERS["DEFAULT"](self)
