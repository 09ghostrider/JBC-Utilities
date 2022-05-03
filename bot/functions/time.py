def Plural(seconds=None, minutes=None, hours=None, days=None, years=None):
    if seconds:
        if seconds > 1:
            return f"{seconds} seconds"
        return f"{seconds} second"
    elif minutes:
        if minutes > 1:
            return f"{minutes} minutes"
        return f"{minutes} minute"
    elif hours:
        if hours > 1:
            return f"{hours} hours"
        return f"{hours} hour"
    elif days:
        if days > 1:
            return f"{days} days"
        return f"{days} day"
    elif years:
        if years > 1:
            return f"{years} years"
        return f"{years} year"
    return "Invalid time provided"

def blizzard_time(time:int):
    hours, remainder = divmod(time, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)

    if years:
        if days:
            return f"{Plural(years=years)} and {Plural(days=days)}"
        return f"{Plural(years=years)}"

    if days:
        if hours:
            return f"{Plural(days=days)} and {Plural(hours=hours)}"
        return f"{Plural(days=days)}"

    if hours:
        if minutes:
            return f"{Plural(hours=hours)} and {Plural(minutes=minutes)}"
        return f"{Plural(hours=hours)}"

    if minutes:
        if seconds:
            return f"{Plural(minutes=minutes)} and {Plural(seconds=seconds)}"
        return f"{Plural(minutes=minutes)}"
    return f"{Plural(seconds=seconds)}"