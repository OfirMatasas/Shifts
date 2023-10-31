import datetime
import sys
import unittest
sys.path.append("../..")

from src.util.workday_util import WorkdayUtils

class WorkdayUtilsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.utils = WorkdayUtils()
        return super().setUp()

    def test_is_valid_date_string_success(self):
        print('Running test_is_valid_date_string_success')
        valid_string = '12-2-1990'
        result = self.utils.is_valid_date_string(valid_string)

        self.assertEqual(result, True)

    def test_is_valid_date_string_failure_empty_date(self):
        print('Running test_is_valid_date_string_failure_empty_date')
        invalid_string = ''
        result = self.utils.is_valid_date_string(invalid_string)

        self.assertEqual(result, False)
    
    def test_is_valid_date_string_failure_null_date(self):
        print('Running test_is_valid_date_string_failure_null_date')
        invalid_string = None
        result = self.utils.is_valid_date_string(invalid_string)

        self.assertEqual(result, False)
    
    def test_create_workday_sequence_success(self):
        print('test_create_workday_sequence_success')
        result = self.utils.create_workday_sequence(starting_day='1-1-2023', ending_day='10-1-2023')
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual(len(result[0]), 10)
        self.assertEqual(len(result[1]), 10)
        self.assertEqual(result[0][0], 'Sunday')
        self.assertEqual(result[1][0], '01-01-2023')
        self.assertEqual(result[0][9], 'Tuesday')
        self.assertEqual(result[1][9], '10-01-2023')
    
    def test_create_workday_sequence_bad_date_format(self):
        print('test_create_workday_sequence_bad_date_format')
        result = self.utils.create_workday_sequence('31-2-2023')

        self.assertIsNotNone(result)
        self.assertEqual(result, ())
    
    def test_create_workday_sequence_no_input_at_all(self):
        print('test_create_workday_sequence_no_input_at_all')
        result = self.utils.create_workday_sequence()

        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual(len(result[0]), 5)
        self.assertEqual(len(result[1]), 5)
    
    def test_create_workday_sequence_no_start_date(self):
        print('test_create_workday_sequence_no_start_date')
        end_date = str((datetime.datetime.today() + datetime.timedelta(2)).strftime(self.utils.DATE_FORMAT))
        result = self.utils.create_workday_sequence(ending_day=end_date)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual(len(result[0]), 3)
        self.assertEqual(len(result[1]), 3)
    
    def test_create_workday_sequence_no_start_date_ending_date_invalid(self):
        print('test_create_workday_sequence_no_start_date_ending_date_invalid')
        end_date = str((datetime.datetime.today() - datetime.timedelta(2)).strftime(self.utils.DATE_FORMAT))
        result = self.utils.create_workday_sequence(ending_day=end_date)

        self.assertIsNotNone(result)
        self.assertEqual(result, ([], []))
    

    def test_create_workday_sequence_no_end_date(self):
        print('test_create_workday_sequence_no_end_date')
        start_date = str(datetime.datetime.today().strftime(self.utils.DATE_FORMAT))
        result = self.utils.create_workday_sequence(starting_day=start_date)

        self.assertIsNotNone(result)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual(len(result[0]), self.utils.DEFAULT_DAYS_COUNT)
        self.assertEqual(len(result[1]), self.utils.DEFAULT_DAYS_COUNT)
    

        