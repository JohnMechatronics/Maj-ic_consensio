#
#  Backtesting CSV price data and calculate the % Change
#

# Reads data from smp_data.csv
# Writes data to smp_output.csv

input_filename = "smp_data.csv"
output_filename = "smp_output.csv"

date = ""
close = 0
previous_close = 0
change = 0.0
#buy_and_hold = int(input("Enter the initial investment: "),"10000") # the default is $10000
buy_and_hold = 10000 
cash = 0
POS = buy_and_hold

# Set the length of the 3 mmoving averages in weeks
ma_short_length = int(input("Enter the short term MA in weeks: ")) #3
ma_medium_length = int(input("Enter the medium term MA in weeks: ")) #7
ma_long_length = int(input("Enter the long term MA in weeks: ")) #30

#ma_short_length = 3
sma_value_out = 0
sma_list = []

#vma_medium_length = 7
mma_value_out = 0
mma_list = []

##ma_long_length = 30
lma_value_out = 0
lma_list = []

#used to calculate slope
slope_weeks = 1 
previous_mma = 0 
mma_slope = 0
previous_lma = 0 
lma_slope = 0 

current_sub_condition = 0
previous_sub_condition = 1




# ++++++++++++ functions ++++++++++++

# function to calculate Moving averages         
def calculate_moving_average(ma_length, ma_list, Close, first_Pass):
    if first_Pass == False:
        # Move all vaues to the right, loose the last one
        for i in range(ma_length-1, 0, -1):
            ma_list[i] = ma_list[i-1]
        ma_list[0] = Close
        
    # scroll through the list and calculate the MA   
    ma_total = 0
    for var in ma_list:
        ma_total += var
    ma = ma_total//ma_length
    return ma

# function to re-calculate for change  
def recalculate_for_change(Change, val):
    val = round(((val//100)*Change) + val, 2)
    return val

# function to calculate the current sub-contition   
def sub_contition(SMA,MMA,LMA):
    SC = 0
    if SMA > MMA and SMA > LMA and MMA > LMA:
        SC = 1 #"A"
    elif SMA == MMA and SMA > LMA and MMA > LMA:
        SC = 2 #"B"
    elif SMA < MMA and SMA > LMA and MMA > LMA:
        SC = 3 #"C"
    elif SMA < MMA and SMA == LMA and MMA > LMA:
        SC = 4 #"D"
    elif SMA < MMA and SMA < LMA and MMA > LMA:
        SC = 5 #"E"
    elif SMA < MMA and SMA < LMA and MMA == LMA: #bear
        SC = 6 #"F"
    elif SMA < MMA and SMA < LMA and MMA < LMA: 
        SC = 7 #"G"
    elif SMA == MMA and SMA < LMA and MMA < LMA: 
        SC = 8 #"H"
    elif SMA > MMA and SMA < LMA and MMA < LMA: 
        SC = 9 #"I"
    elif SMA > MMA and SMA == LMA and MMA < LMA: 
        SC = 10 #"J"
    elif SMA > MMA and SMA > LMA and MMA < LMA: 
        SC = 11 #"K"
    elif SMA > MMA and SMA > LMA and MMA == LMA: 
        SC = 12 #"L"
    elif SMA == MMA and SMA == LMA and MMA == LMA: 
        SC = 13 #"M"
    else:
        SC = 0
    return SC

# sell a percentage  
def sell(Percentage):
    global POS
    global cash
    percent_pos = (POS/100) * Percentage
    POS = POS - percent_pos
    cash += percent_pos

# buy a percentage  
def buy(Percentage):
    global POS
    global cash
    percent_cash = (cash/100) * Percentage
    POS += percent_cash
    cash = cash - percent_cash

# function to take action based on the sub-contition  
def action(Previous_sub_condition, Current_sub_condition):

    #AB
    if Current_sub_condition == 1 and Current_sub_condition != Previous_sub_condition:
        buy(100)
    #CS - sell 25%
    elif Current_sub_condition == 3  and Current_sub_condition > Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        sell(25)
    #CB - buy 25%
    elif Current_sub_condition == 3  and Current_sub_condition < Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        buy(25)
    #ES - sell 25%
    elif Current_sub_condition == 5  and Current_sub_condition > Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        sell(25)
    #EB - buy 50%  
    elif Current_sub_condition == 5  and Current_sub_condition < Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        buy(50)
    #GS
    elif Current_sub_condition == 7  and Current_sub_condition != Previous_sub_condition:
        sell(100)
    #IS
    elif Current_sub_condition == 9  and Current_sub_condition < Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        sell(25)
    #IB
    elif Current_sub_condition == 9  and Current_sub_condition > Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        buy(25)
    #KS
    elif Current_sub_condition == 11  and Current_sub_condition < Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        sell(25)    
    #KB
    elif Current_sub_condition == 11  and Current_sub_condition > Previous_sub_condition and Current_sub_condition != Previous_sub_condition:
        buy(25)
        
# delta  
def delta(BH_out,consensio):
    delta = consensio - BH_out 
    return delta

# calculate slope 
def slope(y2,y1,weeks):
    m = (y2-y1)//(weeks)
    return m


# ++++++++++++ Main Program ++++++++++++

import csv

with open(output_filename, mode='w') as output_file:
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    output_writer.writerow(['Date', 'Close', 'Change', 'Buy_and_Hold', 'SMA (price)', 'MMA', 'MMA-Slope', 'LMA', 'LMA-Slope','sub_condition', 'CASH', 'POS', 'Consensio', 'Delta'])
    # Open input file
    with open(input_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # Reads header file from CSV
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            # Need two close data before calculating change
            elif line_count == 1:
                date = row[0]
                close = int(row[1])
                previous_close = close
                sma_list.append(close)
                mma_list.append(close)
                lma_list.append(close)
                line_count += 1
                output_writer.writerow([date, close, change, 0, 0,0,0,0,0, current_sub_condition, 0, 0,0,0])
                print(date, close)
            # from row 2
            else:
                date = row[0]
                close = int(row[1])
                
                # calculate % change
                change = round(((close - previous_close)/previous_close)*100, 2)
                previous_close = close
                
                # calculate short MA (price)
                if line_count < ma_short_length: # Dont calculat ma until all the values are loaded
                    sma_list.insert(0, close)
                elif line_count == ma_short_length:
                    sma_list.insert(0, close)
                    sma_value_out = calculate_moving_average(ma_short_length, sma_list, close, True)
                else:
                    sma_value_out = calculate_moving_average(ma_short_length, sma_list, close, False)
                    
                # calculate medium MA
                if line_count < ma_medium_length:
                    mma_list.insert(0, close)
                elif line_count == ma_medium_length:
                    mma_list.insert(0, close)
                    mma_value_out = calculate_moving_average(ma_medium_length, mma_list, close, True)
                else:
                    mma_value_out = calculate_moving_average(ma_medium_length, mma_list, close, False)
                    # Calculate mma slope
                    mma_slope = slope(mma_value_out,previous_mma,slope_weeks)
             
                # calculate long MA 
                if line_count < ma_long_length:
                    lma_list.insert(0, close)
                elif line_count == ma_long_length:
                    lma_list.insert(0, close)
                    lma_value_out = calculate_moving_average(ma_long_length, lma_list, close, True)
                else:
                    lma_value_out = calculate_moving_average(ma_long_length, lma_list, close, False)  
                    # Calculate lma slope
                    lma_slope = slope(lma_value_out,previous_lma,slope_weeks)
                   
                # calculate Buy and Hold and POS - start at MA long
                if line_count == ma_long_length: # enter trade
                    buy_and_hold_OUT = buy_and_hold
                    POS_OUT = POS
                    
                elif line_count > ma_long_length:
                    buy_and_hold = recalculate_for_change(change, buy_and_hold)
                    POS = recalculate_for_change(change, POS)
                    buy_and_hold_OUT = int(buy_and_hold)
                    POS_OUT = POS
                else:
                    buy_and_hold_OUT = 0
                    POS_OUT = 0
                   
                # Calculate the current sub-contition
                if line_count >= ma_long_length:
                    current_sub_condition = sub_contition(sma_value_out,mma_value_out,lma_value_out)

                # Call action function 
                action(previous_sub_condition, current_sub_condition)
                POS_OUT = int(POS)
                cash_out = int(cash)
                
                # Calculate Consensio (POS + Cash)
                consensio_OUT = POS_OUT + cash_out
                
                # Calculate delta
                delta_OUT = delta(buy_and_hold_OUT, consensio_OUT) 
                
                
                # print data to the ouput file
                print(date, close, change, buy_and_hold_OUT, sma_value_out, mma_value_out, mma_slope, lma_value_out, lma_slope, current_sub_condition, cash_out, POS_OUT, consensio_OUT, delta_OUT)
                output_writer.writerow([date, close, change, buy_and_hold_OUT, sma_value_out, mma_value_out, mma_slope, lma_value_out, lma_slope, current_sub_condition, cash_out, POS_OUT, consensio_OUT, delta_OUT])
                
                # Move to the next line of the input file
                previous_sub_condition = current_sub_condition
                previous_mma = mma_value_out
                previous_lma = lma_value_out
 
                line_count += 1
            
            
        print(f'Processed {line_count} lines.')
