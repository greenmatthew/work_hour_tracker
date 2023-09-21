import datetime
import os
import sys
import readline

# Data structure to hold the entries
entries = []


def sort_entries():
    global entries  # Declare entries as a global variable
    if entries and len(entries) != 0:
        entries = sorted(entries, key=lambda x: x['date'])

# Function to add an entry


def print_help():
    print("Here's how you can interact with this shell:")
    print("- See all the commmands and their arguments: help")
    print("- Clear the screen: clear (Aliases: clr)")
    print(
        "- Add an Entry: add [hours] [minutes] [date] (e.g., add 2 30 01/15/2022)")
    print("- Remove an Entry: remove [index] (e.g., remove 1) (Aliases: rm)")
    print("- List Entries: list (Aliases: ls)")
    print("- Exit and Save: exit (Aliases: quit, q)")


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def add_entry(hours, minutes, date, verbose=True):
    entry = {'hours': hours, 'minutes': minutes,
             'date': datetime.datetime.strptime(date, '%m/%d/%Y')}
    entries.append(entry)
    sort_entries()
    save_entries()
    if (verbose):
        print(
            f"Entry added: {entry['hours']} hours {entry['minutes']} minutes on {date}")

# Function to remove an entry


def remove_entry(index):
    if index < len(entries):
        entry = entries.pop(index)
        sort_entries()
        save_entries()
        print(
            f"Entry removed: {entry['hours']} hours {entry['minutes']} minutes on {entry['date'].strftime('%m/%d/%Y')}")
    else:
        print("Invalid index.")

# Function to list all entries


def list_entries():
    total_hours = 0
    total_minutes = 0
    prev_date = None

    for (index, entry) in enumerate(entries):
        total_hours += entry['hours']
        total_minutes += entry['minutes']
        date_str = entry['date'].strftime('%m/%d/%Y')

        # Insert a blank line if the date has changed
        if prev_date and prev_date != date_str:
            print()

        index_str = f"{index+1}.".ljust(4)
        print(
            f"{index_str} {entry['hours']:<2} hours {entry['minutes']:>2} minutes on {date_str}")

        prev_date = date_str

    total_hours += total_minutes // 60
    total_minutes = total_minutes % 60
    print(
        f"\nTotal: {total_hours} hours {total_minutes} minutes ({total_hours + total_minutes / 60:.2f} hours)")


# Function to save entries to a file


def save_entries():
    with open('data/time_entries.txt', 'w') as file:
        for entry in entries:
            file.write(
                f"{entry['hours']} {entry['minutes']} {entry['date'].strftime('%m/%d/%Y')}\n")

# Function to load entries from a file


def load_entries():
    try:
        with open('data/time_entries.txt', 'r') as file:
            for line in file:
                hours, minutes, date = line.strip().split()
                entry = {'hours': int(hours), 'minutes': int(minutes),
                         'date': datetime.datetime.strptime(date, '%m/%d/%Y')}
                entries.append(entry)
        sort_entries()  # Sort entries after loading
    except FileNotFoundError:
        print("No saved entries found.")


def run_command(command: str):
    if command == "exit" or command == "q" or command == "quit":
        save_entries()
        sys.exit(0)  # Exit the program after executing the command
    elif command == "clear" or command == "clr":
        clear_screen()
    elif command == "help":
        print_help()
    elif command.startswith("add "):
        _, hours, minutes, date = command.split()
        add_entry(int(hours), int(minutes), date)
    elif command.startswith("remove ") or command.startswith("rm "):
        _, index = command.split()
        remove_entry(int(index) - 1)
    elif command == "list" or command == "ls":
        list_entries()
    else:
        print("Invalid command.\n")
        print_help()


def main(argc: int, argv: list):
    load_entries()
    if (argc > 1):
        command = " ".join(argv[1:])
        run_command(command)
    else:
        # Shell-like interface
        while True:
            command = input("> ")
            run_command(command)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
