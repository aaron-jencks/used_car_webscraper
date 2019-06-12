
def remove_dollar_and_comma(data: str) -> int:
    """Removes the $ and , from the labels on the display for the price sliders."""
    return int(data.replace('$', '').replace(',', ''))
