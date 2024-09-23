# John Paul Larkin
# C00001754
# Scripting Lab two - 21/9/24

import math

def poundToKilogram(pounds):
    # Create a constant for the conversion factor
    POUND_TO_KG_CONVERSION = 0.45359237
    # Convert from pounds to kilograms
    kilograms = pounds * POUND_TO_KG_CONVERSION
    return kilograms

def printTime(time,timezone=0):
    # Add the timezone to the time
    time= time + timezone
    # 00:00 to 11:59 on a 12-hour clock is am period
    meridiem = " am" if time<12 else " pm"
    # Convert to 12-hour clock by subtracting 12 if time is greater than 13
    time = time if time < 13 else time - 12
    # If the time is a whole number, pad the float with an extra zero 
    if(time-math.floor(time)==0): 
       return str(time) + "0" + meridiem
        
    return str(time) + meridiem


def distanceInKilometers(miles,hours):
    # Create a constant for the conversion factor
    MILES_TO_KM_CONVERSION = 1.609344
    # miles and hours are strings, so first convert to float
    miles=float(miles)
    hours=float(hours)
    # Convert from miles kilometers
    kilometers = miles * MILES_TO_KM_CONVERSION
    # Calculate the speed in kilometers per hour
    kilometersPerHour = kilometers / hours
    # Round the speed to one decimal place
    kilometersPerHour = round(kilometersPerHour, 1)
    # Convert float to string, and print the speed in kilometers per hour
    print(str(kilometersPerHour)+"kph")
    
def inchToCentimetre(*inches):
    # Create a constant for the conversion factor
    INCH_TO_CM_CONVERSION = 2.54
    # Create an empty string to store the output
    output = ''
    # Loop through each of the input arguments
    for inch in inches:
        # Convert the inch to centimeters
        centimeter = inch * INCH_TO_CM_CONVERSION
        # Convert to a string and add to the output string
        output += str(centimeter)+'cm '
    # Finally, print the output string
    print(output)
    
# Create a constant for the conversion factor 
STONES_TO_POUNDS_CONVERSION = 14
# Create a lambda function to convert stones to pounds
convertWeight = lambda stones: stones * STONES_TO_POUNDS_CONVERSION
    
    
if __name__ == "__main__":
    kilograms = poundToKilogram(3)
    kilograms = round(kilograms, 3)
    print(kilograms)                               # should return 1.361

    print(printTime(12.36) )                       # should print 12.36pm
    print(printTime(16.00,4))                      # should print 8.00pm
    print(printTime(13.15,-3))                     # should print 10.15am
    
    distanceInKilometers(miles="12.5",hours="3")   # should print 6.7kph
    distanceInKilometers(hours="4.5", miles="23")  # should print 8.2kph

    inchToCentimetre(2,4,52)                       # should print 5.08cm 10.16cm 132.08cm
    inchToCentimetre(45,23,3,1,2)                  # should print 114.3cm 58.42cm 7.62cm 2.54cm 5.08cm   
      
    print(convertWeight(3))                        # should print 42
    