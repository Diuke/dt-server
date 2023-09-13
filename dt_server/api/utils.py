import datetime

#Function to separate generic time intervals
def format_time_intervals(time_list):
    complete_list = []
    for element in time_list:
        split_interval = element.strip().split("/")
        if len(split_interval) > 1:
            interval_list = []
            first_date = None
            end_date = None
            format_suffix = ""
            try:
                #Extract dates with timezone as it comes from the service -- Format: 2021-10-28T23:30:00.000Z
                first_date = datetime.datetime.strptime(split_interval[0], "%Y-%m-%dT%H:%M:%S.000Z")
                end_date = datetime.datetime.strptime(split_interval[1], "%Y-%m-%dT%H:%M:%S.000Z")
                format_suffix = "00.000Z"
            except Exception as ex:
                #Some services have different formats... Format: 2021-10-28T23:30:00Z
                first_date = datetime.datetime.strptime(split_interval[0], "%Y-%m-%dT%H:%M:%SZ")
                end_date = datetime.datetime.strptime(split_interval[1], "%Y-%m-%dT%H:%M:%SZ")
                format_suffix = "00Z"
            
            if first_date is None or end_date is None:
                raise ValueError("Date format incorrect")
            
            interval = str(split_interval[2])
            #Define the interval step
            #"PXDTXHXM"
            if "P" in interval:
                #remove the P
                interval = interval[1:]
                interval_days = 0
                interval_hours = 0
                interval_minutes = 0
                if "T" in interval and not "D" in interval:
                    interval_parts = interval.split("T")
                    interval_time = interval_parts[1]
                    if "H" in interval_time: #hours present
                        interval_hours = interval_time.split("H")[0]
                        if "M" in interval_time: #hours and minutes
                            interval_minutes = interval_time.split("M")[1]
                    else: #only minutes
                        interval_minutes = interval_time.split("M")[0]

                elif "T" in interval and "D" in interval: #days and time
                    interval_parts = interval.split("T")
                    interval_date = interval_parts[0]
                    interval_time = interval_parts[1]

                    interval_days = interval_date.split("D")[0]
                    if "H" in interval_time: #hours present
                        interval_hours = interval_time.split("H")[0]
                        if "M" in interval_time: #hours and minutes
                            interval_minutes = interval_time.split("M")[1]
                    else: #only minutes
                        interval_minutes = interval_time.split("M")[0]
                    
                
                else: #only days
                    interval_days = interval.split("D")[0]

            interval_days = int(interval_days)
            interval_hours = int(interval_hours)
            interval_minutes = int(interval_minutes)

            while first_date <= end_date: 
                month = f'0{first_date.month}' if len(str(first_date.month)) == 1 else f'{first_date.month}'
                day = f'0{first_date.day}' if len(str(first_date.day)) == 1 else f'{first_date.day}'
                hours = f'0{first_date.hour}' if len(str(first_date.hour)) == 1 else f'{first_date.hour}'
                minutes = f'0{first_date.minute}' if len(str(first_date.minute)) == 1 else f'{first_date.minute}'
                date_to_add = f'{first_date.year}-{month}-{day}T{hours}:{minutes}:{format_suffix}'
                interval_list.append(date_to_add)
                first_date = first_date + datetime.timedelta(hours=(interval_days*24)+interval_hours, minutes=interval_minutes)

            complete_list += interval_list 
        else: 
            complete_list.append(element)  

    return complete_list
