from datetime import datetime, timedelta
import os
import sys
import readline
from typing import List

# Data structure to hold the entries
entries = []

# Options
WEEK_START_IS_MONDAY = False
FULL_DATE_STRING_FORMATTER = "%m/%d/%Y"
SHORT_DATE_STRING_FORMATTER = "%m/%d"
DAYS_PER_WEEK = 7

def date_to_str(date: datetime, formatter=FULL_DATE_STRING_FORMATTER) -> str:
    return date.strftime(formatter)

def sort_entries():
    global entries  # Declare entries as a global variable
    if entries and len(entries) != 0:
        entries = sorted(entries, key=lambda x: x['date'])

def exit(options: List[str]):
    if len(options) > 0:
        print(f"Invalid options: {' '.join(options)}")
        return
    
    save_entries()
    sys.exit(0)

# Function to add an entry

def print_help(options: List[str]):
    if len(options) > 0:
        print(f"Invalid options: {' '.join(options)}")
        return

    print("Here's how you can interact with this shell:")
    print("- See all the commmands and their arguments: help")
    print("- Clear the screen: clear (Aliases: clr)")
    print("- Exit the program: exit (Aliases: quit, q)")
    print("- Add a new entry: add [date] [duration] (e.g., add 2 30 01/15/2022)")
    print("- Remove an entry: remove [index] (e.g., remove 1) (Aliases: rm)")
    print("- List all entries: list [-b] (Use '-b' for basic listing) (Aliases: ls)")


def clear_screen(options: List[str]):
    if len(options) > 0:
        print(f"Invalid options: {' '.join(options)}")
        return

    os.system('cls' if os.name == 'nt' else 'clear')


def add_entry(options: List[str]):
    hours = int(options.pop(0))
    minutes = int(options.pop(0))
    date = options.pop(0)

    verbose = True
    
    if "-nv" in options:
        options.remove("-nv")
        verbose = False
    if len(options) > 0:
        print(f"Invalid options: {' '.join(options)}")
        return

    entry = {'hours': hours, 'minutes': minutes,
             'date': datetime.strptime(date, '%m/%d/%Y')}
    entries.append(entry)
    sort_entries()
    save_entries()
    if (verbose):
        print(f"Entry added: {entry['hours']} hours {entry['minutes']} minutes on {date}")

# Function to remove an entry


def remove_entry(options: List[str]):
    index = int(options.pop(0))

    if len(options) > 0:
        print(f"Invalid options: {' '.join(options)}")
        return

    if index < len(entries):
        entry = entries.pop(index)
        index = entry['index']
        hours = entry['hours']
        minutes = entry['minutes']
        date = entry['date']
        date_str = date_to_str(date)
        sort_entries()
        save_entries()
        print(f"Entry removed: {hours} hours {minutes} minutes on {date_str}")
    else:
        print("Invalid index.")

def get_weekday_index(date: datetime) -> int:
    if WEEK_START_IS_MONDAY:
        return date.weekday()
    else:
        return (date.weekday() + 1) % DAYS_PER_WEEK

def get_week_range(date: datetime) -> tuple:
    weekday_index = get_weekday_index(date)
    start_date = date - timedelta(days=weekday_index)
    end_date = start_date + timedelta(days=6)
    
    # Set the time for start_date to the first moment of the day
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    # Set the time for end_date to the last moment of the day
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return start_date, end_date

# def generate_strut()

# Function to list all entries


def list_entries(options: List[str]):
    global entries
    basic = False
    output = False
    output_path = None
    
    while options:
        option = options.pop(0)
        
        if option == '-b':
            basic = True
        elif option in ('-o', '-output'):
            output = True
            if options:
                output_path = options.pop(0)
            else:
                print("-output option is missing a file path.")
                return
        else:
            print(f"Invalid option: {option}")
            return

    total_minutes = 0
    if (basic):
        prev_date = None

        for entry in entries:
            index = entry['index']
            hours = entry['hours']
            minutes = entry['minutes']
            date = entry['date']
            date_str = date_to_str(date)

            # Insert a blank line if the date has changed
            if prev_date and prev_date != date_str:
                print()

            index_str = f"{index+1}.".ljust(4)
            print(f"{index_str} {hours:<2} hours {minutes:>2} minutes on {date_str}")

            prev_date = date_str
            total_minutes += hours * 60 + minutes

        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60
        print(f"\nTotal: {total_hours} hours {total_minutes} minutes ({total_hours + total_minutes / 60:.2f} hours)")
    else:
        prev_week = None
        week_entries = {}
        for entry in entries:
            date = entry['date']
            current_week = get_week_range(date)

            if current_week == prev_week:
                week_entries[current_week].append(entry)
            else:
                week_entries[current_week] = []
                week_entries[current_week].append(entry)
                prev_week = current_week
        
        final_output = ""
        # Iterate over every week
        for week in week_entries.keys():
            # Get entries for this week
            current_entries = week_entries[week]
            # Get the start and end date of the week
            start_date, end_date = week

            # Sort entries into jagged 2D array by the day of week while also tallying the total hours and minutes for that week
            entry_table = [[] for _ in range(DAYS_PER_WEEK)]
            
            week_total_minutes = 0
            for entry in current_entries:
                hours = entry['hours']
                minutes = entry['minutes']
                date = entry['date']
                weekday_index = get_weekday_index(date)
                entry_table[weekday_index].append(entry)
                week_total_minutes += hours * 60 + minutes
                total_minutes += hours * 60 + minutes
            
            lines = []
            for r in range(0, max(len(x) for x in entry_table)):
                line = []
                for c in range(0, DAYS_PER_WEEK):
                    try:
                        entry = entry_table[c][r]
                        duration_str = entry['duration_str']
                        line.append(duration_str)
                    except IndexError:
                        line.append("-".center(10, " "))
                
                lines.append(f"│ {' │ '.join(line)} │")
            
            inner_column_length = 12
            inner_length = DAYS_PER_WEEK * (inner_column_length + 1) - 1
            final_output += f"┌{'─' * inner_length}┐\n"

            week_range_str = f"{date_to_str(start_date)} - {date_to_str(end_date)}".center(inner_length, " ")
            final_output += f"│{week_range_str}│\n"

            weeks_total_str = f"Week's Total: {week_total_minutes // 60} hr {week_total_minutes % 60} m ({week_total_minutes / 60:.2f} hr)".center(inner_length, " ")
            final_output += f"│{weeks_total_str}│\n"
            
            temp_lines = []
            for c in range(0, DAYS_PER_WEEK):
                temp_lines.append("─" * inner_column_length)
            final_output += f"├{'┬'.join(temp_lines)}┤\n"
            temp_lines = []
            for c in range(0, DAYS_PER_WEEK):
                temp_lines.append(date_to_str(start_date + timedelta(days=c), SHORT_DATE_STRING_FORMATTER).center(inner_column_length, " "))
            final_output += f"│{'│'.join(temp_lines)}│\n"
            
            temp_lines = []
            for c in range(0, DAYS_PER_WEEK):
                temp_lines.append("─" * inner_column_length)
            final_output += f"├{'┼'.join(temp_lines)}┤\n"
            final_output += "\n".join(lines) + '\n'
            temp_lines = []
            for c in range(0, DAYS_PER_WEEK):
                temp_lines.append("─" * inner_column_length)
            final_output += f"└{'┴'.join(temp_lines)}┘\n"

        raw_total_hours = total_minutes / 60
        total_hours = total_minutes // 60
        total_minutes = total_minutes % 60
        final_output += f"Total: {total_hours} hr {total_minutes} m ({raw_total_hours:.2f} hr)\n"
        if (output):

            html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Your Output</title>
    <style>
        pre {{
            font-family: "Cascadia Mono", "Courier New", monospace;
        }}
    </style>
</head>
<body>
    <pre>
{}
    </pre>
</body>
</html>
'''.format(final_output)

            with open(output_path, 'w') as file:
                file.write(html_content)
        else:
            print(final_output, end="")




            
                




            


        # date = datetime.strptime('2023-09-20', '%Y-%m-%d')
        # start_date, end_date = get_week_range(date)
        # print(f"Week starts on {start_date.strftime('%m/%d/%Y %H:%M:%S')} and ends on {end_date.strftime('%m/%d/%Y %H:%M:%S')}")

        # date = entries[0]['date']
        # start_date, end_date = get_week_range(date)
        # print(f"Week starts on {start_date.strftime('%m/%d/%Y %H:%M:%S')} and ends on {end_date.strftime('%m/%d/%Y %H:%M:%S')}")

# Function to save entries to a file


def save_entries():
    with open('data/time_entries.txt', 'w') as file:
        for entry in entries:
            file.write(f"{entry['hours']} {entry['minutes']} {entry['date'].strftime('%m/%d/%Y')}\n")

# Function to load entries from a file


def load_entries():
    try:
        with open('data/time_entries.txt', 'r') as file:
            index = 0
            for line in file:
                hours, minutes, date = line.strip().split()
                entry = {'index': index, 'hours': int(hours), 'minutes': int(minutes),
                         'date': datetime.strptime(date, '%m/%d/%Y'), 'duration_str': f"{hours:>2} hr {minutes:>2} m"}
                entries.append(entry)
                index += 1
        sort_entries()  # Sort entries after loading
    except FileNotFoundError:
        print("No saved entries found.")

def parse_command(raw_input: str):
    parts = raw_input.split()
    return parts[0], parts[1:]

def run_command(raw_input: str):
    command, options = parse_command(raw_input)
    if command == "exit" or command == "q" or command == "quit":
        exit(options)
    elif command == "clear" or command == "clr":
        clear_screen(options)
    elif command == "help":
        print_help(options)
    elif command == "add":
        add_entry(options)
    elif command == "remove" or command == "rm":
        remove_entry(options)
    elif command == "list" or command == "ls":
        list_entries(options)
    else:
        print("Invalid command.\n")
        print_help(options)


def main(argc: int, argv: list):
    load_entries()
    if (argc > 1):
        raw_input = " ".join(argv[1:])
        run_command(raw_input)
    else:
        # Shell-like interface
        while True:
            raw_input = input("> ")
            run_command(raw_input)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
