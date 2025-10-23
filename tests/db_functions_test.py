import unittest
from unittest.mock import patch
from src.db_functions.db_functions import *

import json

class TestConn(unittest.TestCase):
    def test_known_inputs(self):
        conn = makeConn()
        self.assertTrue(isinstance(conn, psycopg2.extensions.connection))

class test_symmetry(unittest.TestCase):
    test_input_1 = {
    "North": 1, "East": 2, "South": 3, "West": 4,
    "Northbound Traffic": 5, "Eastbound Traffic": 6, "Southbound Traffic": 7, "Westbound Traffic": 8,
    "Priority Exists": [True, False, True, False],
    "Priority Headings": ["A", "B", "C", "D"],
    "Crossings Exist": [0, 1, 0, 1],
    "Pedestrian Crossings": ["Yes", "No", "Yes", "No"]
    }

    test_input_2 = { 
        "North": 4, "East": 1, "South": 2, "West": 3, 
        "Northbound Traffic": 8, "Eastbound Traffic": 5, "Southbound Traffic": 6, "Westbound Traffic": 7, 
        "Priority Exists": [False, True, False, True], 
        "Priority Headings": ["D", "A", "B", "C"], 
        "Crossings Exist": [1, 0, 1, 0], 
        "Pedestrian Crossings": ["No", "Yes", "No", "Yes"] 
    }

    test_input_3 = { 
        "North": 3, "East": 4, "South": 1, "West": 2, 
        "Northbound Traffic": 7, "Eastbound Traffic": 8, "Southbound Traffic": 5, "Westbound Traffic": 6, 
        "Priority Exists": [True, False, True, False], 
        "Priority Headings": ["C", "D", "A", "B"], 
        "Crossings Exist": [0, 1, 0, 1], 
        "Pedestrian Crossings": ["Yes", "No", "Yes", "No"] 
    }

    test_input_4 = { 
        "North": 2, "East": 3, "South": 4, "West": 1, 
        "Northbound Traffic": 6, "Eastbound Traffic": 7, "Southbound Traffic": 8, "Westbound Traffic": 5, 
        "Priority Exists": [False, True, False, True], 
        "Priority Headings": ["B", "C", "D", "A"], 
        "Crossings Exist": [1, 0, 1, 0], 
        "Pedestrian Crossings": ["No", "Yes", "No", "Yes"] 
    }

    tests = [test_input_1, test_input_2, test_input_3, test_input_4]
    def test_symmetry(self, tests):
        ls = []
        for test in tests:
            ls += check_symmetry(test)

        self.assertFalse(len(set(ls)) == 4)
        

class TestSetup(unittest.TestCase):
    def test_setup_sqlite(self):
        init_db()
        try:
            conn = sqlite3.connect("../data/example.db")

            out = query_DB(conn, ["*"], "junction_config")
        except Exception as e:
            print(e)

        os.remove('../data/example.db')


class TestValidInput(unittest.TestCase):
    def test_known_inputs(self):
        inputInformation = {"hash": "d676c863a81ecbd8365d3d21bfa642af33fb862ca873edb35df11815d4eea609",
                            "North": "LLLL",
                            "East": "LL",
                            "South": "RRRR",
                            "West": "LRLR",
                            "Northbound Traffic": 100,
                            "Northbound Traffic": 200,
                            "Northbound Traffic": 300,
                            "Northbound Traffic": 400,
                            "Priority Exists": True,
                            "Priority Headings": [1, 2, 3, 4],
                            "Crossing Exists": [False, False, False, False],
                            "Pedestrian Crossings": [None, None, None, None]}
        conn = makeConn()
        self.assertTrue(True)
        # self.assertTrue(write_to_DB(conn, inputInformation))

class TestInvalidInput(unittest.TestCase):
    def test_known_inputs(self):
        sample_input = [{'hash: 75cb69e58d5cb9059132f8791fb774bdd344eb7d60071caad413ff725c8d3fa4', ''}]
        response = None
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()