import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

from UI.pyqt_prototype.schema import execute_request, ui_schema
from UI.pyqt_prototype.runner import range_tables
from UI.pyqt_prototype.web_server import SequencerServer
from API.util.Latex import LatexTablePrinter


def query(**changes):
    return {"api": "point", "command": "catalan", "parameters": {"n": "4"}, **changes}


class QueryTests(unittest.TestCase):
    def test_all_object_families(self):
        for name, count in {"catalan": 14, "fubini": 75, "parking_func": 125, "stirling": 105, "type_b": 116}.items():
            with self.subTest(name=name):
                self.assertTrue(execute_request(query(command=name))["text"].strip().endswith(f"= {count}"))

    def test_schema_and_explicit_defaults(self):
        schema = ui_schema()
        self.assertEqual(len(schema["commands"]), 5)
        self.assertEqual({a["id"] for a in schema["apis"]}, {"point", "range"})
        self.assertEqual(len(schema["restrictions"]), 6)
        base = query(command="fubini", parameters={"n": 3})
        def restricted(value):
            return execute_request(dict(base, restriction_groups=[[{"name": "zigzag", "parameters": value}]]))["text"]
        self.assertEqual(restricted({}), restricted({"is": True}))
        self.assertNotEqual(restricted({"is": True}), restricted({"is": False}))
        zero = execute_request(query(command="parking_func", parameters={"n": 1, "r": 0, "unit": False}))
        self.assertTrue(zero["text"].strip().endswith("= 1"))

    def test_statistics_and_elements(self):
        result = execute_request(query(statistic="runs", print_elements=True))
        self.assertIn("[", result["text"])
        self.assertNotEqual(result["text"], execute_request(query())["text"])

    def test_restriction_groups_or_and_lists(self):
        base = query(command="fubini", parameters={"n": 3})
        groups = [[{"name": "zigzag", "parameters": {"is": value}}] for value in (True, False)]
        self.assertEqual(execute_request(dict(base, restriction_groups=groups))["text"], execute_request(base)["text"])
        impossible = execute_request(dict(base, restriction_groups=[groups[0] + groups[1]]))
        self.assertTrue(impossible["text"].strip().endswith("= 0"))
        peaks = execute_request(dict(base, restriction_groups=[[{"name": "peaks", "parameters": {"peaks": "2"}}]]))
        self.assertIn("FubiniRankings", peaks["text"])

    def test_range_outputs_and_empty_result(self):
        dimensions = [{"name": "n", "kind": "parameter"}, {"name": "runs", "kind": "computed"}]
        base = query(api="range", command="fubini", parameters={"n": 3}, dimensions=dimensions,
                     restriction_groups=[[{"name": "zigzag", "parameters": {"is": True}}]])
        result = execute_request(base)
        self.assertEqual(result["tables"][0]["data"], [["1", "0"], ["1", "1"], ["0", "6"]])
        latex = execute_request(dict(base, output="latex"))
        self.assertEqual(latex["downloads"][0]["name"], "out.tex")
        self.assertIn(r"\end{document}", latex["downloads"][0]["content"])
        self.assertIn("Raw output:", execute_request(dict(base, output="raw"))["text"])
        sequence = execute_request(query(api="range", output="oeis", dimensions=dimensions[:1]))
        self.assertIn("1 1 2 5 14", sequence["text"])
        empty = execute_request(dict(base, restriction_groups=[[{"name": "zigzag", "parameters": {"is": True}}, {"name": "zigzag", "parameters": {"is": False}}]]))
        self.assertEqual(empty["tables"], [])
        self.assertIn("Empty set", empty["text"])

    def test_multiple_and_sparse_tables(self):
        tables = range_tables({1: {1: {1: 2}, 3: {3: 4}}, 3: {2: {2: 6}}}, ["slice", "column", "row"])
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0].data[1], [0, 0, 0])
        result = execute_request(query(api="range", command="fubini", parameters={"n": 3, "k": 3},
            dimensions=[{"name": "n", "kind": "parameter"}, {"name": "k", "kind": "parameter"}, {"name": "runs", "kind": "computed"}]))
        self.assertGreater(len(result["tables"]), 1)

    def test_missing_range_limit_is_explained(self):
        with self.assertRaisesRegex(ValueError, "upper limit.*'k'"):
            execute_request(query(api="range", command="fubini", dimensions=[{"name": "k", "kind": "parameter"}]))

    def test_invalid_queries(self):
        for payload in [[], query(command="missing"), query(parameters={}), query(parameters={"n": -1}),
                        query(parameters={"n": "1/extra:2"}), query(parameters={"n": []}), query(statistic="missing"),
                        query(print_elements="false"), query(api="range"), query(api="range", dimensions=[{"name": "bad", "kind": "parameter"}])]:
            with self.subTest(payload=payload), self.assertRaises((ValueError, AssertionError)):
                execute_request(payload)

    def test_parallel_output_is_not_mixed(self):
        payloads = [query(command=name, parameters={"n": 5}, print_elements=True) for name in ("catalan", "fubini", "stirling")]
        expected = [execute_request(payload) for payload in payloads]
        with ThreadPoolExecutor(max_workers=3) as executor:
            self.assertEqual(list(executor.map(execute_request, payloads)), expected)

    def test_legacy_latex_filename_still_works(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "output.tex"
            printer = LatexTablePrinter(path)
            printer.writeTable("", (1, 1), "n", (1, 1), "k", [[7]])
            printer.close()
            self.assertIn(r"\end{document}", path.read_text())


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = SequencerServer().start()
        cls.opener = build_opener(ProxyHandler({}))

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_assets_schema_and_query(self):
        for path in ("", "app.js", "app.css", "theme.css", "api/schema"):
            with self.subTest(path=path), self.opener.open(self.server.url + path) as response:
                self.assertEqual(response.status, 200)
        request = Request(self.server.url + "api/query", json.dumps(query()).encode(), {"Content-Type": "application/json", "Origin": self.server.url.rstrip("/")})
        with self.opener.open(request) as response:
            self.assertIn("= 14", json.load(response)["text"])

    def test_rejected_http_requests(self):
        requests = [
            (Request(self.server.url + "api/query", b"{}", {"Content-Type": "application/json", "Origin": "https://other.example"}), 403),
            (Request(self.server.url + "api/query", b"{}", {"Content-Type": "text/plain"}), 415),
            (Request(self.server.url + "api/query", b"{", {"Content-Type": "application/json"}), 400),
            (Request(self.server.url + "api/schema", headers={"Host": "other.example"}), 403),
            (Request(self.server.url + "../runner.py"), 404),
        ]
        for request, status in requests:
            with self.subTest(url=request.full_url), self.assertRaises(HTTPError) as error:
                self.opener.open(request)
            self.assertEqual(error.exception.code, status)
            error.exception.close()


if __name__ == "__main__":
    unittest.main()
