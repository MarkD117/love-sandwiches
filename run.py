import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')

def get_sales_data():
    """
    Get sales figures input from the user.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of 6 numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:
        print("Please enter sales data from the last market.")
        print("Data should be six numbers, separated by commas.")
        print("Example: 10,20,30,40,50,60\n")


        data_str = input("Enter your data here:\n")
    
        sales_data = data_str.split(",") # Split() method returns the broken up values as a list

        if validate_data(sales_data):
            print("Data is valid!")
            break

    return sales_data


def validate_data(values):
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if strings cannot be converted into int,
    or if there aren't exactly 6 values.
    """
    try:
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f"Exactly 6 values required, you provided {len(values)}"
            )
    except ValueError as e:
        print(f"Invalid data: {e}, please try again.\n")
        return False

    return True


def update_worksheet(data, worksheet):
    """
    Receives a list of integers to be inserted into a worksheet
    Update the relevant worksheet with the data provided
    """
    print(f"Updating {worksheet} worksheet...\n")
    # Uses 'SHEET' variable assigned above with the gspread worksheet() method to access worksheet.
    # Value passed to worksheet() method relates to name of the current worksheet page.
    worksheet_to_update = SHEET.worksheet(worksheet)
    # Uses gspread append_row() method to pass our data to the spreadsheet.
    # The append_row method adds a new row to the  end of our data in the worksheet selected.
    worksheet_to_update.append_row(data)
    print(f"{worksheet} worksheet updated successfully.\n")

def calulate_surplus_data(sales_row):
    """
    Compare sales with stock and calculate the surplus for each item type.

    The surplus is defined as the sales figure subtracted from the stock:
    - Positive surplus indicates waste
    - Negative surplus indicates extra made when stock was sold out.
    """
    print("Calculating surplus data...\n")
    # gspread get_all_values() method gets all of the cells from the 'stock' worksheet
    stock = SHEET.worksheet("stock").get_all_values()
    stock_row = stock[-1] # Slice the final item of the list and return it to the stock_row variable
    
    """
    When used with a for loop, the zip() method allows  us to iterate through two or more iterable data 
    structures in a single loop. In this case, our iterable data structures, are lists.
    """
    surplus_data = []
    for stock, sales in zip(stock_row, sales_row):
        surplus = int(stock) - sales
        surplus_data.append(surplus)
    
    return surplus_data


def get_last_5_entries_sales():
    """
    Collects columns of data from sales worksheet, collecting
    the last 5 entries for each sandwich and returns the data
    as a list of lists.
    """
    sales = SHEET.worksheet("sales")

    columns = []
    for ind in range(1, 7):
        # gspread col_values() method used to get columns from worksheet. 
        # Number in method specifies column number.
        column = sales.col_values(ind)
        # List is sliced to get the last 5 values. Colon used for multiple values.
        columns.append(column[-5:])
        
    return columns


def calculate_stock_data(data):
    """
    Calculate the average stock for each item type, adding 10%
    """
    print("Calculating stock data...\n")
    new_stock_data = []

    for column in data:
        int_column = [int(num) for num in column] # Converting column values into integers
        # Calculating average by dividing sum of list by length or the number of elements in the list
        average = sum(int_column) / len(int_column)
        # Adding 10% to new stock to account for additional sales
        stock_num = average * 1.1
        # Round() method used to round stock numbers to whole numbers
        new_stock_data.append(round(stock_num))

    return new_stock_data


def main():
    """
    Run all program functions
    """
    data = get_sales_data()
    sales_data = [int(num) for num in data] # List comprehension used to convert entered values to integers
    update_worksheet(sales_data, "sales")
    new_surplus_data = calulate_surplus_data(sales_data)
    update_worksheet(new_surplus_data, "surplus")
    sales_columns = get_last_5_entries_sales()
    stock_data = calculate_stock_data(sales_columns)
    update_worksheet(stock_data, "stock")


print("Welcome to Love Sandwiches Data Automation")
main()

