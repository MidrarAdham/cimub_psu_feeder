import pandas as pd

nodes_3ph = ["680","633","632","692","675","671","684","645","652", "611"]
phases_3 = ["A", "B", "C"]
def dss_3ph(nodes_3ph,  phases_3):
    counter = 40
    for k in  phases_3:
        for i in nodes_3ph:
            j = 1
            if i == "652" and k == "A": # Single phase A node 652
                while j <= counter:
                    # print(f"New Load.trip_load_{i}_{k}_h_{j} Bus1=trip_load_{i}_{k}_h_{j}.1.2 phases=2 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
                    print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.1 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    j= j+1
            if i == "611" and k == "C": # Single phase C node 611
                while j <= counter:
                    # print(f"New Load.trip_load_{i}_{k}_h_{j} Bus1=trip_load_{i}_{k}_h_{j}.1.2 phases=2 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
                    print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.3 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    j= j+1
            if i == "684" and (k == "A" or k == "C"): # Two-phase A,C node 684
                while j <= counter:
                    # print(f"New Load.trip_load_{i}_{k}_h_{j} Bus1=trip_load_{i}_{k}_h_{j}.1.2 phases=2 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
                    if k == "A":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.1 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    if k == "C":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.3 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    j= j+1
            if i == "645" and (k == "B" or k == "C"): # Two-phase A,C node 684
                while j <= counter:
                    # print(f"New Load.trip_load_{i}_{k}_h_{j} Bus1=trip_load_{i}_{k}_h_{j}.1.2 phases=2 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
                    if k == "B":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.2 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    if k == "C":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.3 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    j= j+1
            if not i == "652" and not i == "611" and not i == "684" and not i == "645":
                while j <= counter:
                    if k == "A":
                    # print(f"New Load.trip_load_{i}_{k}_h_{j} Bus1=trip_load_{i}_{k}_h_{j}.1.2 phases=2 Conn=Wye kV=0.208 kW=3.0 kvar=0.0")
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.1 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    if k == "B":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.2 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    if k == "C":
                        print(f"New Load.trip_load_{i}_{k}_{j} Bus1=trip_load_{i}_{k}_h_{j}.3 phases=1 Conn=Wye kV=0.12 kW=3.0 kvar=0.0")
                    j= j+1


def main(nodes_3ph,  phases_3):
    loads = dss_3ph(nodes_3ph,  phases_3)

main(nodes_3ph,  phases_3)



# k = range(40)
# i = 1
# while i <= 40:
#     print(i) 
#     i+=1
