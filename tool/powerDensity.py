import math

initRadis = 20


power = 100e6  # 100MW
print("power:{:.2e}MW".format(power*1e-6))
for ii in range(20):
    radis = initRadis + ii * 10
    height = radis * 2
    volum = math.pi * radis**2 * height
    print("r:{:<5d} h:{:<5d} pd:{:<.3f} W/cm3".format(radis, height, power/volum))

power = 200e6  # 100MW
print("power:{:.2e}MW".format(power*1e-6))
for ii in range(20):
    radis = initRadis + ii * 10
    height = radis * 2
    volum = math.pi * radis**2 * height
    print("r:{:<5d} h:{:<5d} pd:{:<.3f} W/cm3".format(radis, height, power/volum))

power = 300e6  # 100MW
print("power:{:.2e}MW".format(power*1e-6))
for ii in range(20):
    radis = initRadis + ii * 10
    height = radis * 2
    volum = math.pi * radis**2 * height
    print("r:{:<5d} h:{:<5d} pd:{:<.3f} W/cm3".format(radis, height, power/volum))