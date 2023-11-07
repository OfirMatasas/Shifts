import datetime
from src.util.workday_util import WorkdayConst, WorkdayUtils

def test_create_workday_sequence_both_inputs():
    starting_day: datetime.date = datetime.date.today()
    ending_day: datetime.date = starting_day + datetime.timedelta(4)
    workday_sequence = WorkdayUtils.create_workday_sequence(starting_day=starting_day, ending_day=ending_day)

    assert workday_sequence is not None
    assert len(workday_sequence.day_names) == 5
    assert len(workday_sequence.day_dates) == 5

def test_create_workday_sequence_only_starting_date():
    starting_day: datetime.date = datetime.date.today()
    workday_sequence = WorkdayUtils.create_workday_sequence(starting_day=starting_day)

    assert workday_sequence is not None
    assert len(workday_sequence.day_names) == WorkdayConst.DEFAULT_DAYS_COUNT
    assert len(workday_sequence.day_dates) == WorkdayConst.DEFAULT_DAYS_COUNT

def test_create_workday_sequence_only_ending_date():
    ending_day: datetime.date = datetime.date.today() + datetime.timedelta(2)
    workday_sequence = WorkdayUtils.create_workday_sequence(ending_day=ending_day)

    assert workday_sequence is not None
    assert len(workday_sequence.day_names) == 3
    assert len(workday_sequence.day_dates) == 3

def test_create_workday_sequence_no_dates_provided():
    workday_sequence = WorkdayUtils.create_workday_sequence()

    assert workday_sequence is not None
    assert workday_sequence.day_names[0] == datetime.date.today().strftime('%A')
    assert workday_sequence.day_names[len(workday_sequence.day_names) - 1] == (datetime.date.today() + datetime.timedelta(WorkdayConst.DEFAULT_DAYS_COUNT - 1)).strftime('%A')
    assert len(workday_sequence.day_names) == WorkdayConst.DEFAULT_DAYS_COUNT
    assert len(workday_sequence.day_dates) == WorkdayConst.DEFAULT_DAYS_COUNT

def test_create_workday_sequence_end_day_before_start_day():
    ending_day: datetime.date = datetime.date.today()
    starting_day: datetime.date = ending_day + datetime.timedelta(4)
    workday_sequence = WorkdayUtils.create_workday_sequence(starting_day=starting_day, ending_day=ending_day)

    assert workday_sequence is not None
    assert len(workday_sequence.day_names) == 0
    assert len(workday_sequence.day_dates) == 0

def test_create_workday_sequence_month_ahead():
    starting_day: datetime.date = datetime.date.today()
    ending_day: datetime.date = starting_day + datetime.timedelta(30)
    workday_sequence = WorkdayUtils.create_workday_sequence(starting_day=starting_day, ending_day=ending_day)

    assert workday_sequence is not None
    assert len(workday_sequence.day_names) == 31
    assert len(workday_sequence.day_dates) == 31