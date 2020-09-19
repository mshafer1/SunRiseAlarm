def normalize_hours_minutes(hours, minutes):
    """
    >>> normalize_hours_minutes(0,0)
    (0, 0)

    >>> normalize_hours_minutes(0,60)
    (1, 0)

    >>> normalize_hours_minutes(2,-10)
    (1, 50)
    """
    if minutes > 0:
        hours += minutes // 60
        minutes = minutes % 60
    elif minutes < 0:
        hours += minutes // 60
        minutes = (60 + minutes) % 60
    return hours, minutes
