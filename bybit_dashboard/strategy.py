def get_entry_levels(base_price, levels=3):
    """
    Divide capital em 3 entradas com descontos progressivos
    """
    steps = [0, -1.5, -3.5]  # percentuais abaixo do preço atual
    return [round(base_price * (1 + s / 100), 2) for s in steps]
