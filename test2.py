
# def func(a,b):
#     if a == b:
#         return False
#     return True

# def func(a, b):
#     return a != b

# print(func(False,False))
# print(func(False,True))
# print(func(True,False))
# print(func(True,True))

def check_speed(speed):
    if speed >= 80:
        print("You were speeding")
        if speed <= 90:
            print("light warning")
        elif speed <= 100:
            print("going to have to give a ticket")
        else:
            print("you are in serious trouble")

check_speed(110)  

for i in range(10,0,-1):
    print(i)