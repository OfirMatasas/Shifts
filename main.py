from tabulate import tabulate

# List of team members
team_members = ["Hadar", "Matasas", "Ofer", "Nissan", "Or", "Michal", "Eylon", "Pavel", "Ido"]
hard_shifts_count = {key: 0 for key in team_members}
hard_shifts_hours = [("01:00", "04:00"), ("04:00", "07:00")]
shifts_space = {key: 0 for key in team_members}

# Define the days off
first_day_off = [("Sunday", ("22:00", "01:00")), ("Tuesday", ("22:00", "01:00")), ["Ofer", "Nissan"]]
second_day_off = [("Tuesday", ("22:00", "01:00")), ("Thursday", ("22:00", "01:00")), ["Or", "Michal"]]
third_day_off = [("Thursday", ("22:00", "01:00")), ("Saturday", ("22:00", "01:00")), ["Matasas", "Pavel"]]
days_off = [first_day_off, second_day_off, third_day_off]
team_members_on_day_off = []

# Define the shifts (24 hours divided into 3-hour shifts)
shifts = [(f"{hour:02}:00", f"{(hour + 3) % 24:02}:00") for hour in range(1, 24, 3)]

# Create a schedule for 7 days
days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
schedule = {day: {} for day in days_of_week}

for day in days_of_week:
    for shift in shifts:

        # Check if the current shift is a start of a day off. If so - add the team members to the team_members_on_day_off list and remove them from the team_members list
        for day_off in days_off:
            if (day, shift) == day_off[0]:
                for member in day_off[2]:
                    if member in team_members:
                        team_members_on_day_off.append(member)
                        shifts_space.pop(member)
                        hard_shifts_count.pop(member)
                        team_members.remove(member)

        # Check if the current shift is an end of a day off. If so - add the team members back to the team_members list and remove them from the team_members_on_day_off list
        for day_off in days_off:
            if (day, shift) == day_off[1]:
                team_members.reverse()

                for member in day_off[2]:
                    if member not in team_members:
                        team_members.append(member)
                        shifts_space[member] = 0
                        hard_shifts_count[member] = 0

                team_members.reverse()
                team_members_on_day_off = []

        # Get the team member with the maximum amount of shifts space
        team_members.sort(key=lambda member: shifts_space[member], reverse=True)

        # Set the current shift to the team member with the maximum amount of shifts space
        # But, if the current shift is a hard shift, set it to the team member with the maximum amount of shifts space, as long as he didn't have a hard shift in the last 2 weeks
        if shift in hard_shifts_hours:
            member_index = 0
            while True:
                if hard_shifts_count[team_members[member_index]] == 2:
                    member_index += 1
                else:
                    break

            hard_shifts_count[team_members[member_index]] += 1
            schedule[day][shift] = team_members.pop(member_index)
        else:
            schedule[day][shift] = team_members.pop(0)

        # Update the shifts space for each team member
        shifts_space[schedule[day][shift]] = -1
        for member in team_members:
            shifts_space[member] += 1

        # Add the team member back to the team_members list
        team_members.append(schedule[day][shift])




        # Check if the current shift is a hard shift.
        # If so - add the team member with the maximum amount of shift_space, as long as he didn't have a hard shift in the last 2 weeks
        # if shift in hard_shifts_hours:
        #     team_members.sort(key=lambda member: hard_shifts_count[member])
        #     hard_shifts_count[team_members[0]] += 1
        #     schedule[day][shift] = team_members.pop(0)
        # else:
        #     schedule[day][shift] = team_members.pop(0)
        #
        # shifts_space[schedule[day][shift]] = -1
        # for member in team_members:
        #     shifts_space[member] += 1
        # team_members.append(schedule[day][shift])

# Print the schedule using tabulate
table = [["Shift"] + days_of_week]
for shift in shifts:
    table.append([f"{shift[0]} - {shift[1]}"] + [schedule[day][shift] for day in days_of_week])

print(tabulate(table, headers="firstrow", tablefmt="pretty"))
