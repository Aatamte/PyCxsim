
# test_string_to_dict.py

import unittest
from cxsim.utilities.convert_string_to_json import string_to_dict  # Make sure to import your function


class TestStringToDict(unittest.TestCase):
    def test_valid_python_dict_string(self):
        s = "{'action': 'skip', 'reason': 'I will skip...'}"
        expected = {'action': 'skip', 'reason': 'I will skip...'}
        self.assertEqual(string_to_dict(s), expected)

    def test_valid_json_string(self):
        s = '{"action": "skip", "reason": "I will skip..."}'
        expected = {'action': 'skip', 'reason': 'I will skip...'}
        self.assertEqual(string_to_dict(s), expected)

    def test_single_quotes_json_like_string(self):
        s = "{'action': 'skip', 'reason': 'I will skip...'}"
        expected = {'action': 'skip', 'reason': 'I will skip...'}
        self.assertEqual(string_to_dict(s), expected)

    def test_invalid_string(self):
        s = "this is not a dict string"
        with self.assertRaises(ValueError):
            string_to_dict(s)


if __name__ == '__main__':
    unittest.main()




