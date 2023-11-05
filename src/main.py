from tabulate import tabulate
from csv import writer, reader
import math
from util.workday_util import WorkdayUtils

# Constants
SHIFT = "Shift\n"
ON_CALL = "On Call"
NORMAL = "normal"
DOUBLE = "double"
ON_CALL_SHIFT = ("19:00", "22:00")
MAX_HARD_SHIFTS_PER_WEEK = 2
DAY_OFF_START_SHIFT_INDEX = 0
DAY_OFF_END_SHIFT_INDEX = 1
DAY_OFF_TEAM_MEMBERS_INDEX = 2
SPACE_ON_CALL = -5

# Team members' names
HADAR = "Hadar"
MATASAS = "Matasas"
OFER = "Ofer"
NISSAN = "Nissan"
OR = "Or"
MICHAL = "Michal"
EYLON = "Eylon"
PAVEL = "Pavel"
IDO = "Ido"
STEFANOV = "Stefanov"
WEISS = "Weiss"
SHAPIRA = "Shapira"
ASSAF = "Assaf"

# Define the shifts (24 hours divided into 3-hour shifts)
shifts = [(f"{hour:02}:00", f"{(hour + 3) % 24:02}:00") for hour in range(1, 24, 3)]

# List of team members and their shifts space
team_members = [HADAR, MATASAS, OFER, NISSAN, OR, MICHAL, EYLON, PAVEL, IDO]
hard_shifts_count = {key: 0 for key in team_members}
on_call_count = {key: 0 for key in team_members}
hard_shifts_hours = [("01:00", "04:00"), ("04:00", "07:00")]
shifts_space = {key: 0 for key in team_members}

# Define the work days
workday_seq = WorkdayUtils().create_workday_sequence()
work_days = workday_seq.day_names
work_days_dates = workday_seq.day_dates

# Define the days off
days_off = [
    # [(START_DAY, (SHIFT_START, SHIFT_END)), (END_DAY, (SHIFT_START, SHIFT_END)), [TEAM_MEMBERS]],
    # [(MONDAY, ("22:00", "01:00")), (TUESDAY, ("22:00", "01:00")), [HADAR, MATASAS]],
]
team_members_on_day_off = []
on_call = []

# Create a schedule for 7 days
schedule = {day: {} for day in work_days}


def remove_team_members_if_day_off_is_on(day, shift):
    '''
    Check if the current shift is a start of a day off.
    If so - add the team members to the team_members_on_day_off list and remove them from the team_members list
    '''

    for day_off in days_off:
        if (day, shift) == day_off[DAY_OFF_START_SHIFT_INDEX]:
            for member in day_off[DAY_OFF_TEAM_MEMBERS_INDEX]:
                if member in team_members:
                    team_members_on_day_off.append(member)
                    shifts_space.pop(member)
                    hard_shifts_count.pop(member)
                    team_members.remove(member)


def add_team_members_if_day_off_is_over(day, shift):
    '''
    Check if the current shift is an end of a day off.
    If so - add the team members back to the team_members list and remove them from the team_members_on_day_off list
    '''

    global team_members_on_day_off

    for day_off in days_off:
        if (day, shift) == day_off[DAY_OFF_END_SHIFT_INDEX]:
            team_members.reverse()

            for member in day_off[DAY_OFF_TEAM_MEMBERS_INDEX]:
                if member not in team_members:
                    team_members.append(member)
                    shifts_space[member] = 100
                    hard_shifts_count[member] = 0
                    on_call_count[member] = 0

            team_members.reverse()
            team_members_on_day_off = []


def set_shift_to_relevant_team_member(day, shift):
    '''
    Set the current shift to the team member with the maximum amount of shifts space,
    as long as they didn't have 2 hard shifts already earlier this week
    '''

    member_index = 0

    if shift in hard_shifts_hours:
        while True:
            if 0 <= hard_shifts_count[team_members[member_index]] < MAX_HARD_SHIFTS_PER_WEEK:
                break
            member_index += 1

        hard_shifts_count[team_members[member_index]] += 1

    if schedule[day][shift] == "":
        schedule[day][shift] = team_members[member_index]
    else:
        schedule[day][shift] = f"{schedule[day][shift]}, {team_members[member_index]}"


def update_shift_space(day, shift):
    '''
    Update shifts space for each team member
    '''

    for member in schedule[day][shift].split(", "):
        shifts_space[member] = -1

    for member in team_members:
        shifts_space[member] += 1


def set_on_call_for_team_member(shift):
    '''
    Set a team member to be on call according to his shift space and past on-call duties
    '''

    if shift == ON_CALL_SHIFT and choice == NORMAL:
        member_index = 0

        team_members.sort(key=lambda member: shifts_space[member], reverse=True)

        while member_index < len(team_members):
            if on_call_count[team_members[member_index]] == 0:
                break
            member_index += 1

        on_call_count[team_members[member_index]] += 1
        on_call.append(team_members[member_index])
        shifts_space[team_members[member_index]] = SPACE_ON_CALL


def print_shifts_schedule():
    table = [[SHIFT] + [f'{work_days[i]}\n{work_days_dates[i]}' for i in range(0, len(work_days))]]

    for shift in shifts:
        table.append([f"{shift[0]} - {shift[1]}"] + [schedule[day][shift] for day in work_days])

    if choice == NORMAL:
        table.append([f"{ON_CALL}"] + [member for member in on_call])

    print(tabulate(table, headers="firstrow", tablefmt="pretty"))


def build_shifts_schedule():
    number_of_people_per_shift = 1 if choice == NORMAL else 2

    for day in work_days:
        for shift in shifts:

            remove_team_members_if_day_off_is_on(day, shift)
            add_team_members_if_day_off_is_over(day, shift)

            schedule[day][shift] = ""

            for _ in range(number_of_people_per_shift):
                team_members.sort(key=lambda member: shifts_space[member], reverse=True)

                set_shift_to_relevant_team_member(day, shift)

                update_shift_space(day, shift)

            set_on_call_for_team_member(shift)


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

    with open("schedule.csv", "w", newline="") as file:
        csv_writer = writer(file)
        csv_writer.writerow([SHIFT] + work_days)

        for shift in shifts:
            csv_writer.writerow([f"{shift[0]} - {shift[1]}"] + [schedule[day][shift] for day in work_days])

        if choice == NORMAL:
            csv_writer.writerow([f"{ON_CALL}"] + [member for member in on_call])


def load_old_schedule_fron_csv_file_and_initialize_shift_according_to_old_schedule():
    global on_call, schedule

    with open("schedule.csv", "r", newline="") as file:
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
    get_user_choice()

    # load_old_schedule_fron_csv_file_and_initialize_shift_according_to_old_schedule()
    initialize_shift_according_to_old_schedule_hard_coded()
    build_shifts_schedule()
    print_shifts_schedule()
    write_to_csv_file()


if __name__ == "__main__":
    start_script()
