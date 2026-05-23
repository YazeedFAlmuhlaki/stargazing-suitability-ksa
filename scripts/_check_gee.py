from reusable_functions import initialize_earth_engine 
import ee 


initialize_earth_engine() 

print("Test 1:",ee.Number(305).getInfo()) 

print("Test 2:", ee.Image("USGS/SRTMGL1_003").getInfo())




