import datetime

# speed ranges for fines
fine_ranges = [[0, 10], [11, 15], [16, 20], [
    21, 25], [26, 31], [31, 35], [36, 40], [41, 45]]
# fine in dollars, assigned per fine bracket
fines = [30, 80, 120, 170, 230, 300, 400, 510, 630]

# has to be predefined lists not globals
errors = []
buffer = []

# function takes param of file path as string
# and stores each line of the file in a 2d list
def read_file(file_path):
    global reg_time
    reg_time = []
    errors.clear()
    file_read = open(file_path, "r", encoding="ascii", errors="ignore")

    if file_path.endswith("txt"):
        for line in file_read.readlines():
            line_data = line.split()
            check_plate(line_data)
    elif file_path.endswith("csv"):
        for line in file_read.readlines():
            line_data = line.split(",")
            check_plate(line_data)
        for i, item in enumerate(reg_time):
            # strip the newline register of the end of the string
            item[1] = item[1].strip("\n")

    file_read.close()


# function to check the plate of a vehicle from the list
def check_plate(file_data):
    if len(file_data) == 1:
        file_data.append(None)
        file_data.append(None)
        file_data.append("No time associated with vehicle")
        errors.append(file_data)
    elif len(file_data[0]) <= 6 and file_data[0].isalnum():
        reg_time.append(file_data)
    else:
        file_data.pop(1)
        file_data.append(None)
        file_data.append(None)
        file_data.append("Invalid License Plate")
        errors.append(file_data)


# helper functions
# find the time in and time out of any vehicle
def find_time_in_out(reg_list):
    new_reg_list = []
    for i, reg in enumerate(reg_list):
        plate = reg[0]
        time_in = reg[1]
        for x in range(i+1, len(reg_list)):
            if reg_list[x][0] in plate:
                if time_in != reg_list[x][1]:
                    time_out = reg_list[x][1]
                    break
                else:
                    time_out = "00:00:00"
            else:
                time_out = "00:00:00"
        new_reg_list.append([plate, time_in, time_out])

    return new_reg_list

# strip any duplicate entries that could be generated
# by the find_time_in_out function
def remove_duplicates(list):
    new_list = list

    for i, item in enumerate(new_list):
        for x in range(i+1, len(new_list)):
            if new_list[x][0] in item[0]:
                new_list.pop(x)
                break

    return new_list