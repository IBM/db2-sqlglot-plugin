#-------------------------------------------------------------------------------------------------#
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
#-------------------------------------------------------------------------------------------------#

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
        "POSSTR": lambda args: exp.StrPosition(
            this=seq_get(args, 0), substr=seq_get(args, 1)
        ),
        "VARCHAR_FORMAT": lambda args: exp.TimeToStr(
            this=seq_get(args, 0), format=seq_get(args, 1)
        ),
    }
    
    # Map DB2-specific type keywords to their base types for parsing.
    # This allows the parser to recognize GRAPHIC, VARGRAPHIC, and DBCLOB as
    # valid types.
    TYPE_TOKENS = {
        *parser.Parser.TYPE_TOKENS,
        # DB2-specific types will be parsed as DataType with the name preserved
    }
