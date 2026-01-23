import unittest
import json
from app import app, execute_query

class TestFrostByteAPI(unittest.TestCase):
    def setUp(self):
       
        self.app = app.test_client()
        self.app.testing = True
      
        try:
            execute_query("TRUNCATE TABLE demands, routes, storage_units, products, locations CASCADE;")
        except Exception as e:
            print(f"Setup Error: {e}")


    def post(self, endpoint, data):
        return self.app.post(endpoint, data=json.dumps(data), content_type='application/json')

    def test_create_location(self):
        """Sanity Check: Can we create a location?"""
        res = self.post('/locations', {"name": "Dhaka Hub", "type": "WAREHOUSE", "city": "Dhaka"})
        self.assertEqual(res.status_code, 201)
        self.assertIn('id', json.loads(res.data))

    def test_validate_network_feasible(self):
        """Test: Valid setup (Happy Path)"""
  
        w1 = self.post('/locations', {"name": "Warehouse 1", "type": "WAREHOUSE", "city": "A"}).get_json()
        r1 = self.post('/locations', {"name": "Retailer 1", "type": "RETAILER", "city": "B"}).get_json()
        
     
        self.post('/storage-units', {
            "locationId": w1['id'], "minTemperature": 0, "maxTemperature": 10, "capacity": 100
        })

   
        self.post('/routes', {
            "fromLocationId": w1['id'], "toLocationId": r1['id'], "capacity": 100, "minShipment": 10
        })

        prod = self.post('/products', {"name": "Milk", "minTemperature": 2, "maxTemperature": 5}).get_json()
        self.post('/demands', {
            "locationId": r1['id'], "productId": prod['id'], "date": "2026-01-20",
            "minQuantity": 1, "maxQuantity": 50
        })


        res = self.post('/network/validate', {"date": "2026-01-20"})
        data = res.get_json()
        self.assertTrue(data['feasible'], f"Should be feasible but got: {data.get('issues')}")

    def test_validate_supplier_storage_failure(self):
        """Test: Retailer demand exceeds SUPPLIER'S storage capacity"""
    
        w1 = self.post('/locations', {"name": "Warehouse Small", "type": "WAREHOUSE", "city": "A"}).get_json()
        r1 = self.post('/locations', {"name": "Retailer Big", "type": "RETAILER", "city": "B"}).get_json()
        
      
        self.post('/storage-units', {
            "locationId": w1['id'], "minTemperature": 0, "maxTemperature": 10, "capacity": 10
        })

     
        self.post('/routes', {
            "fromLocationId": w1['id'], "toLocationId": r1['id'], "capacity": 1000, "minShipment": 0
        })


        prod = self.post('/products', {"name": "Milk", "minTemperature": 2, "maxTemperature": 5}).get_json()
        self.post('/demands', {
            "locationId": r1['id'], "productId": prod['id'], "date": "2026-01-21",
            "minQuantity": 1, "maxQuantity": 50
        })

       
        res = self.post('/network/validate', {"date": "2026-01-21"})
        data = res.get_json()
        
        self.assertFalse(data['feasible'])
        self.assertIn("exceeds storage capacity of suppliers", str(data['issues']))

    def test_validate_route_min_capacity_failure(self):
        """Test: Demand is too small for the truck (Min Shipment Violation)"""
        w1 = self.post('/locations', {"name": "W1", "type": "WAREHOUSE", "city": "A"}).get_json()
        r1 = self.post('/locations', {"name": "R1", "type": "RETAILER", "city": "B"}).get_json()
        
       
        self.post('/storage-units', {"locationId": w1['id'], "minTemperature": 0, "maxTemperature": 10, "capacity": 1000})

    
        self.post('/routes', {
            "fromLocationId": w1['id'], "toLocationId": r1['id'], "capacity": 1000, "minShipment": 100
        })

     
        prod = self.post('/products', {"name": "Milk", "minTemperature": 2, "maxTemperature": 5}).get_json()
        self.post('/demands', {
            "locationId": r1['id'], "productId": prod['id'], "date": "2026-01-22",
            "minQuantity": 1, "maxQuantity": 5
        })

        res = self.post('/network/validate', {"date": "2026-01-22"})
        data = res.get_json()
        
        self.assertFalse(data['feasible'])
        self.assertIn("MIN_CAPACITY_VIOLATION", str(data['issues']))

if __name__ == '__main__':
    unittest.main()