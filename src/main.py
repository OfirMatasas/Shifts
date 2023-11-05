import logging as log
from typing import Final
from tabulate import tabulate
from csv import writer, reader
import math
from shift.shift import Shift
from datetime import datetime
from util.workday_util import WorkdayUtils

# Constants
SHIFT: Final[str] = "Shift\n"
ON_CALL: Final[str] = "On Call"
NORMAL: Final[str] = "normal"
NUM_OF_MEMBERS_PER_NORMAL_SHIFT: Final[int] = 1
DOUBLE: Final[str] = "double"
NUM_OF_MEMBERS_PER_DOUBLE_SHIFT: Final[int] = 2
ON_CALL_SHIFT: Final[Shift] = Shift(start_time=datetime(year=2023, month=1, day=1, hour=19))
MAX_HARD_SHIFTS_PER_WEEK = 1
DAY_OFF_START_SHIFT_INDEX: Final[int] = 0
DAY_OFF_END_SHIFT_INDEX: Final[int] = 1
DAY_OFF_TEAM_MEMBERS_INDEX: Final[int] = 2
SPACE_ON_CALL: Final[int] = -5
DEFAULT_SHIFT_DURATION: Final[int] = 3
DEFAULT_FIRST_SHIFT_START_TIME: Final[int] = 1
HOURS_IN_DAY: Final[int] = 24
READ_FILE_NAME: Final[str] = "schedule.csv"
WRITE_FILE_NAME: Final[str] = "schedule.csv"

# Team members' names
HADAR: Final[str] = "Hadar"
MATASAS: Final[str] = "Matasas"
OFER: Final[str] = "Ofer"
NISSAN: Final[str] = "Nissan"
OR: Final[str] = "Or"
MICHAL: Final[str] = "Michal"
EYLON: Final[str] = "Eylon"
PAVEL: Final[str] = "Pavel"
IDO: Final[str] = "Ido"
STEFANOV: Final[str] = "Stefanov"
WEISS: Final[str] = "Weiss"
SHAPIRA: Final[str] = "Shapira"
ASSAF: Final[str] = "Assaf"

# Define the shifts (24 hours divided into 3-hour shifts)
shifts_hours = [hour for hour in range(DEFAULT_FIRST_SHIFT_START_TIME, HOURS_IN_DAY, DEFAULT_SHIFT_DURATION)]

# List of team members and their shifts space
team_members = [HADAR, MATASAS, OFER, NISSAN, OR, MICHAL, EYLON, PAVEL, IDO, STEFANOV, WEISS, SHAPIRA, ASSAF]
hard_shifts_count = {key: 0 for key in team_members}
on_call_count = {key: 0 for key in team_members}
hard_shifts_hours = (Shift(start_time=datetime(year=2023, month=1, day=1, hour=1)), Shift(start_time=datetime(year=2023, month=1, day=1, hour=4)))
shifts_space = {key: 0 for key in team_members}

# Define the work days
workday_seq = WorkdayUtils().create_workday_sequence()
work_days = workday_seq.day_names
work_days_dates = workday_seq.day_dates

# Define the days off
days_off = (
    # (START_SHIFT, END_SHIFT, [TEAM_MEMBERS]),
    # (Shift(day=SUNDAY, start_time=datetime(year=2023, month=1, day=1, hour=22)), Shift(day=WEDNESDAY, start_time=datetime(year=2023, month=1, day=1, hour=22)), [HADAR, MATASAS]),
)
team_members_on_day_off = []
on_call = []

# Create a schedule dictionary
schedule = {day: {} for day in work_days}


def remove_team_members_if_day_off_is_on(shift: Shift):
    '''
    Check if the current shift is a start of a day off.
    If so - add the team members to the team_members_on_day_off list and remove them from the team_members list
    '''

    for day_off in days_off:
        if shift == day_off[DAY_OFF_START_SHIFT_INDEX]:
            log.info(f"Day off started: {shift.day}, {shift}. Removing team members {day_off[DAY_OFF_TEAM_MEMBERS_INDEX]} from team_members list")
            for member in day_off[DAY_OFF_TEAM_MEMBERS_INDEX]:
                if member in team_members:
                    log.debug(f"Adding {member} to team_members_on_day_off")
                    team_members_on_day_off.append(member)

                    log.debug(f"Removing {member} from shifts spaces list")
                    shifts_space.pop(member)

                    log.debug(f"Removing {member} from hard shifts count list")
                    hard_shifts_count.pop(member)

                    log.debug(f"Removing {member} from team members list")
                    team_members.remove(member)
            log.info(f"Team members on day off: {team_members_on_day_off}")
            break


def add_team_members_if_day_off_is_over(shift: Shift):
    '''
    Check if the current shift is an end of a day off.
    If so - add the team members back to the team_members list and remove them from the team_members_on_day_off list
    '''

    global team_members_on_day_off

    for day_off in days_off:
        if shift == day_off[DAY_OFF_END_SHIFT_INDEX]:
            log.info(f"Day off ended: {shift.day}, {shift}. Adding team members {day_off[DAY_OFF_TEAM_MEMBERS_INDEX]} back to team_members list")
            team_members.reverse()

            for member in day_off[DAY_OFF_TEAM_MEMBERS_INDEX]:
                if member not in team_members:
                    log.debug(f"Adding {member} to team members list")
                    team_members.append(member)

                    log.debug(f"Set {member} shifts space to math.inf")
                    shifts_space[member] = math.inf

                    log.debug(f"Set {member} hard shifts count to 0")
                    hard_shifts_count[member] = 0

                    log.debug(f"Set {member} on call count to 0")
                    on_call_count[member] = 0

            team_members.reverse()
            team_members_on_day_off = []
            break


def look_for_team_member_with_minimal_hard_shifts_count(shift: Shift):
    '''
    Set the current shift to the team member with the maximum amount of shifts space,
    as long as they didn't have 2 hard shifts already earlier this week
    '''

    member_index = 0

    log.debug(f"Looking for a team member to set hard shift {shift} on {shift.day}")
    while True:
        current_member = team_members[member_index]
        current_member_hard_shifts_count = hard_shifts_count[current_member]

        if 0 <= current_member_hard_shifts_count < MAX_HARD_SHIFTS_PER_WEEK:
            log.debug(f"Set {shift} to {current_member} (hard shifts count: {current_member_hard_shifts_count} out of {MAX_HARD_SHIFTS_PER_WEEK})")
            break

        log.debug(f"Skipping {current_member} (hard shifts count: {current_member_hard_shifts_count} out of {MAX_HARD_SHIFTS_PER_WEEK})")
        member_index += 1

    return member_index


def set_team_member_to_shift(shift: Shift):
    '''
    Set the current shift to the team member with the maximum amount of shifts space, as long as they didn't have {MAX_HARD_SHIFTS_PER_WEEK} hard shifts already earlier this week
    '''

    log.debug(f"Looking for a team member to set {shift} on {shift.day}")

    member_index = 0
    
    for hard_shift in hard_shifts_hours:
        if shift.is_same_time(hard_shift):
            log.info(f"Hard shift {shift} found")
            member_index = look_for_team_member_with_minimal_hard_shifts_count(shift)

            log.info(f"Set hard shift {shift} to {team_members[member_index]} (hard shifts count: {hard_shifts_count[team_members[member_index]]} out of {MAX_HARD_SHIFTS_PER_WEEK})")
            hard_shifts_count[team_members[member_index]] += 1
            log.debug(f"{team_members[member_index]} new hard shifts count: {hard_shifts_count[team_members[member_index]]}")

            break

    if schedule[shift.day][str(shift)] == None:
        schedule[shift.day][str(shift)] = team_members[member_index]
        log.info(f"Set {shift.day} {str(shift)} to {schedule[shift.day][str(shift)]}")
    else:
        schedule[shift.day][str(shift)] = f"{schedule[shift.day][str(shift)]}, {team_members[member_index]}"
        log.info(f"Set {shift.day} {str(shift)} to {schedule[shift.day][str(shift)]}")


def update_shift_space(shift: Shift):
    '''
    Update shifts space for each team member
    '''

    for member in schedule[shift.day][str(shift)].split(", "):
        shifts_space[member] = -1

    for member in team_members:
        shifts_space[member] += 1

    log.debug(f"Shifts space: {shifts_space}")


def set_on_call_for_team_member(shift: Shift):
    '''
    Set a team member to be on call according to his shift space and past on-call duties
    '''

    if shift.is_same_time(ON_CALL_SHIFT) and choice == NORMAL:
        log.info(f"Looking for a team member to be on call for {shift.day} {str(shift)}")
        member_index = 0

        team_members.sort(key=lambda member: shifts_space[member], reverse=True)

        while member_index < len(team_members):
            if on_call_count[team_members[member_index]] == 0:
                log.debug(f"Set {team_members[member_index]} to be on call for {shift.day} {str(shift)} (on call count: {on_call_count[team_members[member_index]]})")
                break
            member_index += 1

        log.info(f"Set {team_members[member_index]} to be on call for {shift.day} {str(shift)} (on call count: {on_call_count[team_members[member_index]]})")
        on_call_count[team_members[member_index]] += 1
        on_call.append(team_members[member_index])
        shifts_space[team_members[member_index]] += SPACE_ON_CALL
        log.debug(f"{team_members[member_index]} new shifts space has changed from {shifts_space[team_members[member_index]] - SPACE_ON_CALL} to {shifts_space[team_members[member_index]]}")


def print_shifts_schedule():
    table = [[SHIFT] + [f'{work_days[i]}\n{work_days_dates[i]}' for i in range(0, len(work_days))]]

    for shift_hours in shifts_hours:
        table.append([f"{shift_hours:02}:00-{(shift_hours + 3)%24:02}:00"] + [schedule[day][str(Shift(day, datetime(year=2023, month=1, day=1, hour=shift_hours)))] for day in work_days])

    if choice == NORMAL:
        table.append([f"{ON_CALL}"] + [member for member in on_call])

    print(tabulate(table, headers="firstrow", tablefmt="pretty"))


def build_shifts_schedule():
    number_of_people_per_shift = NUM_OF_MEMBERS_PER_NORMAL_SHIFT if choice == NORMAL else NUM_OF_MEMBERS_PER_DOUBLE_SHIFT

    for day in work_days:
        log.debug(f"Building schedule for {day}")
        for shift_hours in shifts_hours:
            current_shift = Shift(day, datetime(year=2023, month=1, day=1, hour=shift_hours))
            log.debug(f"Building schedule for {day}, {current_shift}")

            remove_team_members_if_day_off_is_on(current_shift)
            add_team_members_if_day_off_is_over(current_shift)

            schedule[current_shift.day][str(current_shift)] = None

            for _ in range(number_of_people_per_shift):
                team_members.sort(key=lambda member: shifts_space[member], reverse=True)

                set_team_member_to_shift(current_shift)

                update_shift_space(current_shift)

            set_on_call_for_team_member(current_shift)


def initialize_shift_according_to_old_schedule_hard_coded():
    '''
    Initialize the shifts schedule according to old schedule,
    including on-call duties, shifts space and hard shifts count for each team member since their last day off
    '''

    global on_call, hard_shifts_count, shifts_space

    # Initialize on-call duties
    # For instance: on_call_count[MATASAS] = 1

    # Initialize shifts space
    # For instance:
    #   shifts_space[MATASAS] = 2
    #   shifts_space[PAVEL] = 1
    #   shifts_space[OFER] = 3

    # Initialize hard shifts count
    # For instance:
    #   hard_shifts_count[MATASAS] = 2
    #   hard_shifts_count[OR] = 1

    # Remove team members which are on off day
    # For instance:
    #   team_members.remove(PAVEL)
    #   team_members.remove(MICHAL)


def write_to_csv_file():
    # write the scehdule to a csv file   
    with open(WRITE_FILE_NAME, "w", newline="") as file:
        csv_writer = writer(file)
        csv_writer.writerow([SHIFT] + work_days)

        for shift in shifts_hours:
            csv_writer.writerow([f"{shift:02}:00-{(shift + 3)%24:02}:00"] + [schedule[day][str(Shift(day, datetime(year=2023, month=1, day=1, hour=shift)))] for day in work_days])

        if choice == NORMAL:
            csv_writer.writerow([f"{ON_CALL}"] + [member for member in on_call])


def load_old_schedule_fron_csv_file_and_initialize_shift_according_to_old_schedule():
    global on_call, schedule

    with open(READ_FILE_NAME, "r", newline="") as file:
        csv_reader = reader(file)

        for row in csv_reader:
            if row[0] == SHIFT:
                continue

            if row[0] == ON_CALL:
                on_call = row[1:]
                continue

            for day in work_days:
                schedule[day][tuple(row[0].split(" - "))] = row[work_days.index(day) + 1]

    # initialize_shift_according_to_old_schedule()


def get_user_choice():
    global choice, MAX_HARD_SHIFTS_PER_WEEK

    print("Welcome to the shift script.")
    print('''
Choose the type of shifts you'd like to create:
    1. Normal (one officer)
    2. Double (two officers)
''')

    while True:
        choice = input("Your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= 2:
            break
        else:
            print("Invalid input. Please try again.")

    choice = NORMAL if choice == "1" else DOUBLE
    MAX_HARD_SHIFTS_PER_WEEK = MAX_HARD_SHIFTS_PER_WEEK if choice == NORMAL else math.inf

    print(f"You chose to create {choice} shifts schedule.")


def start_script():
    log.getLogger().setLevel(log.INFO)
    get_user_choice()

    # load_old_schedule_fron_csv_file_and_initialize_shift_according_to_old_schedule()
    initialize_shift_according_to_old_schedule_hard_coded()
    build_shifts_schedule()
    print_shifts_schedule()
    write_to_csv_file()


if __name__ == "__main__":
    start_script()
