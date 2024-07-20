def time_to_seconds(seconds: int = 0, minutes: int = 0, hours: int = 0):
    return (
        seconds
        + minutes * 60
        + hours * 3600
    )
