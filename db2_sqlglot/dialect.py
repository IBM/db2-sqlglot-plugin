# -------------------------------------------------------------------------------------------------#
#                      DISCLAIMER OF WARRANTIES AND LIMITATION OF LIABILITY                       #
#                                                                                                 #
#  (C) COPYRIGHT International Business Machines Corp. 2026 All Rights Reserved             #
#  Licensed Materials - Property of IBM                                                           #
#                                                                                                 #
#  US Government Users Restricted Rights - Use, duplication or disclosure restricted by GSA ADP   #
#  Schedule Contract with IBM Corp                                                               #
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

from sqlglot import tokens
from sqlglot.dialects.dialect import Dialect

from db2_sqlglot.generator import Db2 as Db2Generator
from db2_sqlglot.parser import Db2Parser


class Db2(Dialect):
    NULL_ORDERING = "nulls_are_large"
    TYPED_DIVISION = True

    # Time format mappings for Db2
    # https://www.ibm.com/docs/en/db2/11.5?topic=functions-timestamp-format
    TIME_MAPPING = {
        "YYYY": "%Y",
        "YY": "%y",
        "MM": "%m",
        "DD": "%d",
        "HH": "%H",
        "HH12": "%I",
        "HH24": "%H",
        "MI": "%M",
        "SS": "%S",
        "FF": "%f",
        "FF3": "%f",
        "FF6": "%f",
        "MON": "%b",
        "MONTH": "%B",
        "DY": "%a",
        "DAY": "%A",
    }

    class Tokenizer(tokens.Tokenizer):
        # Don't map Db2-specific types (GRAPHIC, VARGRAPHIC, DBCLOB) to token
        # types. Let them be parsed as identifiers so we can preserve the
        # original type name. They will be handled in the parser and generator.
        VAR_SINGLE_TOKENS = {"@"}

    Parser = Db2Parser
    Generator = Db2Generator
