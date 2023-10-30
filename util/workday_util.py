
import datetime
import logging

class WorkdayUtils:
    """
    Static class for working with workdays
    """

    _date_format = '%d-%m-%Y'

    @classmethod
    def is_valid_date_string(cls, date: str) -> bool:
        """
        date: The date we validate

        This method validates a string of format dd-MM-YYYY
        
        Returns True if the date is validated, otherwise false
        """
        is_valid = True

        if date == '' or date == None:
            logging.warning('Date is empty')
            is_valid = False

        if len(date.split('-')) != 3:
            logging.warning('Date should be of format day-month-year')
            is_valid = False
        
        return is_valid
        

    @classmethod
    def create_workday_sequence(cls, starting_day: str = '' , ending_day: str = '') -> (list[str], list[datetime.date]):
        """
        starting_date: The date that we wish to start from
        ending_date: The date until we wish the data to be included

        Returns (The name of the weekday, The date of the weekday), () if the process of enumeration fails
        """

        weekdays_names = []
        weekdays_dates = []

        if not cls.is_valid_date_string(starting_day):
            starting_day = datetime.datetime.today().strftime(cls._date_format)
        if not cls.is_valid_date_string(ending_day):
            ending_day = (datetime.datetime.now() + datetime.timedelta(5)).strftime(cls._date_format)
            

        begin_date = ''
        end_date = ''

        separate_date = lambda x: [int(i) for i in x.split('-')]

        try:
            start_date_data = separate_date(starting_day)
            end_date_data = separate_date(ending_day)
            begin_date = datetime.date(start_date_data[2], start_date_data[1], start_date_data[0])
            end_date = datetime.date(end_date_data[2], end_date_data[1], end_date_data[0])

        except ValueError as ve:
            logging.error(f'Error while parsing date: {ve}')
        except Exception as e:
            logging.error(f'Unexpected error: {e}')

        if begin_date == '' or end_date == '':
            logging.error('Could not parse dates...')
            return ()

        logging.info(f'good..... {begin_date} to {ending_day}')
        
        delta_date = datetime.timedelta(1)

        while begin_date <= end_date:
            weekdays_dates.append(begin_date.strftime(cls._date_format))
            weekdays_names.append(begin_date.strftime('%A'))
            begin_date += delta_date

        return (weekdays_names, weekdays_dates)
        

