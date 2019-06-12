
def remove_dollar_and_comma(data: str) -> int:
    """Removes the $ and , from the labels on the display for the price sliders."""
    return int(data.replace('$', '').replace(',', ''))


def insert_dollar_sign_and_commas(data: int) -> str:
    """Takes a string of numbers and inserts the '$' and ','"""
    return '${:,}'.format(data)
