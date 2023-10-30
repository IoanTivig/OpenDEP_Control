def frequency_int_format(value, no_digits):
    length = len(str(int(value)))
    new_value = int(
        round(value / 10 ** (length - no_digits), 0) * 10 ** (length - no_digits)
    )

    return new_value


def frequency_text_format(value):
    if int(value) < 1000:
        frequency = str(frequency_int_format(value, 2)) + " Hz"
    elif int(value) < 1000000:
        frequency = str(frequency_int_format(value, 2) / 1000) + " kHz"
    elif int(value) < 1000000000:
        frequency = str(frequency_int_format(value, 2) / 1000000) + " MHz"

    return frequency
