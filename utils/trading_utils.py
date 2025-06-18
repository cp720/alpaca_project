def calculate_position_size(price, allocation, account_cash):
    
    buy_quantity = int((account_cash * allocation) / price)
    return buy_quantity
