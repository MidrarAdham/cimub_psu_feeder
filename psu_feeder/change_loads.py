import random
iter = 960

for i in range(iter):
    rand = random.uniform(0,0.5)
    rand_rou = round(rand,2)
    print(f"phases=2 Conn=Wye kV=0.208 kW={rand_rou} kvar=0.0")