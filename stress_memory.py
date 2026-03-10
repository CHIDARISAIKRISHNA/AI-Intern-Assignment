import time
data = []
print("Creating controlled memory stress...")
while True:
    data.append("memory_stress" * 100000)  
    time.sleep(0.1)