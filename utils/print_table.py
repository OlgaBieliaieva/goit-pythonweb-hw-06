from tabulate import tabulate

def print_table(data, headers):    
    print(tabulate(data, headers=headers, tablefmt="grid"))