# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import sqlite3
from textwrap import dedent

import pytest
import simplejson as json
from simplesqlite import SimpleSQLite
from sqliteschema import DataNotFoundError, SQLiteSchemaExtractor
from sqliteschema._schema import SQLiteTableSchema

from ._common import print_test_result
from .fixture import database_path, mb_database_path  # noqa: W0611


class Test_SQLiteSchemaExtractor_constructor(object):
    def test_normal_sqlite3_connection(self, database_path):
        con = sqlite3.connect(database_path)
        SQLiteSchemaExtractor(con)

    def test_normal_simplesqlite(self, database_path):
        con = SimpleSQLite(database_path)
        SQLiteSchemaExtractor(con)

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception_constructor(self, extractor_class):
        with pytest.raises(IOError):
            extractor_class("not_exist_path").fetch_table_names()


class Test_SQLiteSchemaExtractor_fetch_table_names(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        assert extractor.fetch_table_names() == ["testdb0", "testdb1", "constraints"]


class Test_SQLiteSchemaExtractor_fetch_sqlite_master(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        part_expected = [
            {
                "tbl_name": "testdb0",
                "sql": "CREATE TABLE 'testdb0' (\"attr_a\" INTEGER, [attr b] INTEGER)",
                "type": "table",
                "name": "testdb0",
                "rootpage": 2,
            },
            {
                "tbl_name": "testdb0",
                "sql": 'CREATE INDEX testdb0_attra_index_71db ON testdb0("attr_a")',
                "type": "index",
                "name": "testdb0_attra_index_71db",
                "rootpage": 3,
            },
        ]

        actual = extractor.fetch_sqlite_master()[0:2]
        print_test_result(
            expected=json.dumps(part_expected, indent=4), actual=json.dumps(actual, indent=4)
        )

        assert part_expected == actual


class Test_SQLiteSchemaExtractor_fetch_database_schema_as_dict(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        output = extractor.fetch_database_schema_as_dict()
        expected = json.loads(
            dedent(
                """\
                {
                    "testdb0": [
                        {
                            "Attribute": "attr_a",
                            "Index": true,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "attr b",
                            "Index": false,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        }
                    ],
                    "testdb1": [
                        {
                            "Attribute": "foo",
                            "Index": true,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "bar",
                            "Index": false,
                            "Type": "REAL",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "hoge",
                            "Index": true,
                            "Type": "TEXT",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        }
                    ],
                    "constraints": [
                        {
                            "Attribute": "primarykey_id",
                            "Index": true,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "PRI",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "notnull_value",
                            "Index": false,
                            "Type": "REAL",
                            "Null": "YES",
                            "Key": "",
                            "Default": ""
                        },
                        {
                            "Attribute": "unique_value",
                            "Index": true,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "UNI",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "def_text_value",
                            "Index": false,
                            "Type": "TEXT",
                            "Null": "NO",
                            "Key": "",
                            "Default": "'null'"
                        },
                        {
                            "Attribute": "def_num_value",
                            "Index": false,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "",
                            "Default": "0"
                        }
                    ]
                }
                """
            )
        )

        print_test_result(
            expected=json.dumps(expected, indent=4), actual=json.dumps(output, indent=4)
        )

        assert output == expected


class Test_SQLiteSchemaExtractor_fetch_table_schema(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        expected = SQLiteTableSchema(
            "testdb1",
            json.loads(
                """
                {
                    "testdb1": [
                        {
                            "Attribute": "foo",
                            "Index": true,
                            "Type": "INTEGER",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "bar",
                            "Index": false,
                            "Type": "REAL",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        },
                        {
                            "Attribute": "hoge",
                            "Index": true,
                            "Type": "TEXT",
                            "Null": "NO",
                            "Key": "",
                            "Default": "NULL"
                        }
                    ]
                }
                """
            ),
        )
        output = extractor.fetch_table_schema("testdb1")

        print(json.dumps(output.as_dict(), indent=4))

        assert output == expected

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception(self, extractor_class, database_path):
        extractor = extractor_class(database_path)

        with pytest.raises(DataNotFoundError):
            print(extractor.fetch_table_schema("not_exist_table"))


class Test_SQLiteSchemaExtractor_get_attr_names(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        testdb1 = extractor.fetch_table_schema("testdb1")
        assert testdb1.get_attr_names() == ["foo", "bar", "hoge"]
        assert testdb1.primary_key is None
        assert testdb1.index_list == ["foo", "hoge"]

        constraints = extractor.fetch_table_schema("constraints")
        assert constraints.primary_key == "primarykey_id"
        assert constraints.index_list == ["primarykey_id", "unique_value"]

    def test_normal_mb(self, mb_database_path):
        extractor = SQLiteSchemaExtractor(mb_database_path)
        expected = ["いち", "に"]

        assert extractor.fetch_table_schema("テーブル").get_attr_names() == expected


class Test_SQLiteSchemaExtractor_dumps(object):
    @pytest.mark.parametrize(
        ["output_format", "verbosity_level", "expected"],
        [
            [
                "text",
                100,
                dedent(
                    """\
                    testdb0 (
                        attr_a INTEGER Null,
                        attr b INTEGER Null
                    )

                    testdb1 (
                        foo INTEGER Null,
                        bar REAL Null,
                        hoge TEXT Null
                    )

                    constraints (
                        primarykey_id INTEGER Key Null,
                        notnull_value REAL Null,
                        unique_value INTEGER Key Null,
                        def_text_value TEXT Null,
                        def_num_value INTEGER Null
                    )
                    """
                ),
            ],
            [
                "markdown",
                100,
                dedent(
                    """\
                    # testdb0
                    |Attribute| Type  |Null|Key|Default|Index|
                    |---------|-------|----|---|-------|:---:|
                    |attr_a   |INTEGER|NO  |   |NULL   |  X  |
                    |attr b   |INTEGER|NO  |   |NULL   |     |

                    # testdb1
                    |Attribute| Type  |Null|Key|Default|Index|
                    |---------|-------|----|---|-------|:---:|
                    |foo      |INTEGER|NO  |   |NULL   |  X  |
                    |bar      |REAL   |NO  |   |NULL   |     |
                    |hoge     |TEXT   |NO  |   |NULL   |  X  |

                    # constraints
                    |  Attribute   | Type  |Null|Key|Default|Index|
                    |--------------|-------|----|---|-------|:---:|
                    |primarykey_id |INTEGER|NO  |PRI|NULL   |  X  |
                    |notnull_value |REAL   |YES |   |       |     |
                    |unique_value  |INTEGER|NO  |UNI|NULL   |  X  |
                    |def_text_value|TEXT   |NO  |   |'null' |     |
                    |def_num_value |INTEGER|NO  |   |0      |     |
                    """
                ),
            ],
        ],
    )
    def test_normal(self, database_path, output_format, verbosity_level, expected):
        extractor = SQLiteSchemaExtractor(database_path)
        output = extractor.dumps(output_format, verbosity_level)

        print_test_result(expected=expected, actual=output)

        assert output == expected
