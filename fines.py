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

# convert string time into datetime.time type
def str_to_time(time):
    try:
        time = datetime.datetime.strptime(time, "%H:%M:%S").time()
        return time
    except:
        try:
            time = datetime.datetime.strptime(time, "%H:%M").time()
            return time
        except:
            pass
        raise Exception("Time in incorrect format")
        return None

# convert datetime.time into integer value
def time_to_int_mins(time):
    total_seconds = int(time.total_seconds())
    return total_seconds/60

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


# specify return type as datetime.time type
def calculate_duration(time_in, time_out) -> datetime.time:
    min_date = datetime.date.min
    # if the time out is before the time in, then add 60 minutes (daylight savings)
    if time_out < time_in:
        new_time_out = datetime.datetime.combine(
            min_date, time_out) + datetime.timedelta(hours=1)
        return datetime.datetime.combine(min_date, new_time_out.time()) - datetime.datetime.combine(min_date, time_in)
    else:
        return datetime.datetime.combine(min_date, time_out) - datetime.datetime.combine(min_date, time_in)


def calculate_avg_speed(duration_mins, tunnel_len):
    return (tunnel_len / 1000) / (duration_mins / 60)

# fines are calculated by reversing through the fine range list until the speed is met
def calculate_fines(speed, speed_limit):
    over = speed - speed_limit
    if over <= 0:
        return None # no fine if they are within speed limit
    elif over > fine_ranges[len(fine_ranges)-1][0]:
        return fines[len(fines)-1]    # return the last fine in the list
    else:
        for i, x in reversed(list(enumerate(fine_ranges))):
            if over >= fine_ranges[i][0]:
                return fines[i]
                break

# method to see calculate fine or see if vehicle is error
def generate_fines(rtimes_list_in, speed_limit, exit_threshold, tunnel_len):
    rds_list_out = []   # reg, duration, speed
    for i, item in enumerate(rtimes_list_in):
        duration = calculate_duration(str_to_time(item[1]), str_to_time(item[2]))
        speed = calculate_avg_speed(time_to_int_mins(duration), tunnel_len)
        fine = calculate_fines(speed, speed_limit)

        if speed < 0:
            errors.append(item)
            errors[len(errors)-1].append("Vehicle did not exit")
        elif time_to_int_mins(duration) >= exit_threshold:
            errors.append(item)
            errors[len(errors)-1].append(
                "Vehicle did not leave after {} minute exit threshold!".format(exit_threshold))

        if fine is None:
            continue

        new_list = item
        new_list.append(str(duration))
        new_list.append(round(speed, 2))
        new_list.append(fine)

        rds_list_out.append(new_list)

    return rds_list_out


def generate(file_path_in, speed_limit, exit_threshold, tunnel_len):
    try:
        read_file(file_path_in)
    except Exception as exc:
        return exc

    try:
        # defined as global since we are assigning it in the function (read LEGB scope)
        global buffer
        buffer = generate_fines(remove_duplicates(find_time_in_out(
            reg_time)), speed_limit, exit_threshold, tunnel_len)
        return None
    except Exception as exc:
        return exc


def write_txt(file_path, data_list):
    write_file = open(file_path, "w+")
    write_file.write(
        "Plate\t Time In\t Time Out\t Duration\t Speed\t\t Fine\n")
    for i, item in enumerate(data_list):
        str_out = "{}\t {}\t {}\t {}\t {:.2f}km/h\t ${}\n".format(
            item[0], item[1], item[2], item[3], item[4], item[5])
        write_file.write(str_out)


def write_csv(file_path, data_list):
    write_file = open(file_path, "w+")
    write_file.write("Plate,Time In,Time Out,Duration,Speed,Fine\n")
    for i, item in enumerate(data_list):
        new_item = [str(x) for x in item]
        str_out = ",".join(new_item)+"\n"
        write_file.write(str_out)


def write_errors(file_path, data):
    write_file = open(file_path, "w+")
    write_file.write("Plate,Time In,Time Out,Error\n")
    for i, item in enumerate(data):
        new_item = [str(x) for x in item]
        str_out = ",".join(new_item)+"\n"
        write_file.write(str_out)
