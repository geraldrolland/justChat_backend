from datetime import datetime

class FormatDate:
    @classmethod
    def format_date(cls, date):
        month_map = {
            "01": "January",
            "02": "February",
            "03": "March",
            "04": "April",
            "05": "May",
            "06": "June",
            "07": "July",
            "08": "August",
            "09": "September",
            "10": "October",
            "11": "November",
            "12": "December"
        }

        time_map = {
            "12": ["12","pm"],
            "13": ["1", "pm"],
            "14": ["2", "pm"],
            "15": ["3", "pm"],
            "16": ["4", "pm"],
            "17": ["5", "pm"],
            "18": ["6", "pm"],
            "19": ["7", "pm"],
            "20": ["8", "pm"],
            "21": ["9", "pm"],
            "22": ["10", "pm"],
            "23": ["11", "pm"],
            "0": ["12", "am"],
            "1": ["1", "am"],
            "2": ["2", "am"],
            "3": ["3", "am"],
            "4": ["4", "am"],
            "5": ["5", "am"],
            "6": ["6", "am"],
            "7": ["7", "am"],
            "8": ["8", "am"],
            "9": ["9", "am"],
            "10": ["10", "am"],
            "11": ["11", "am"]
        }

        if datetime.now().year == date.year:
            if datetime.now().day == date.day and datetime.now().month == date.month:
                return f"Today, {time_map[str(date.hour)][0]}.{date.minute if date.minute > 9 else {"0"} + str(date.minute)} {time_map[str(date.hour)][1]}"
            elif date.day == datetime.now().day - 1 and datetime.now().month == date.month:
                return f"Yesterday, {time_map[str(date.hour)][0]}.{date.minute if date.minute > 9 else "0"+str(date.minute)}  {time_map[str(date.hour)][1]}"
            elif date.day < datetime.now().day - 1 and date.day > datetime.now().day - 7 and datetime.now().month == date.month:
                return f"{date.strftime("%a")}, {time_map[str(date.hour)][0]}.{date.minute if date.minute > 9 else "0"+str(date.minute)} {time_map[str(date.hour)][1]}"
            else:
                return f"{date.day}/{date.month}/{date.year}, {time_map[str(date.hour)][0]}.{date.minute if date.minute > 9 else "0"+str(date.minute)} {time_map[str(date.hour)][1]}"
        else:
            return f"{date.day}/{date.month}/{date.year}, {time_map[str(date.hour)][0]}.{date.minute if date.minute > 9 else "0"+str(date.minute)}  {time_map[str(date.hour)][1]}"