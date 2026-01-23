import os
import psycopg2
from flask import Flask, request, jsonify
from psycopg2.extras import RealDictCursor

app = Flask(__name__)


def get_db_connection():
    db_host = os.environ.get('DATABASE_HOST', 'db')
    try:
        conn = psycopg2.connect(
            host=db_host,
            database="frostbyte_logistics",
            user="root",
            password="root"
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database not reachable")
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(query, params)
        if fetch_one:
            result = cur.fetchone()
            conn.commit()
            return result
        if fetch_all:
            result = cur.fetchall()
            return result
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


@app.route('/locations', methods=['POST'])
def create_location():
    data = request.get_json()
    try:
        query = """
            INSERT INTO locations (name, type, city) 
            VALUES (%s, %s, %s) RETURNING id, name, type, city;
        """
        new_loc = execute_query(query, (data['name'], data['type'], data['city']), fetch_one=True)
        return jsonify(new_loc), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/locations', methods=['GET'])
def get_locations():
    try:
        locs = execute_query("SELECT * FROM locations;", fetch_all=True)
        return jsonify(locs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    try:
        query = """
            INSERT INTO products (name, min_temperature, max_temperature) 
            VALUES (%s, %s, %s) RETURNING id, name, min_temperature, max_temperature;
        """
        new_prod = execute_query(query, (data['name'], data['minTemperature'], data['maxTemperature']), fetch_one=True)
        return jsonify(new_prod), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/products', methods=['GET'])
def get_products():
    try:
        prods = execute_query("SELECT * FROM products;", fetch_all=True)
        return jsonify(prods), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/storage-units', methods=['POST'])
def create_storage_unit():
    data = request.get_json()
    try:
        # Check if location is WAREHOUSE
        loc = execute_query("SELECT type FROM locations WHERE id = %s", (data['locationId'],), fetch_one=True)
        if not loc:
            return jsonify({"error": "Location not found"}), 404
        if loc['type'] != 'WAREHOUSE':
            return jsonify({"error": "Storage units can only be created at WAREHOUSE locations"}), 400

        query = """
            INSERT INTO storage_units (location_id, min_temperature, max_temperature, capacity) 
            VALUES (%s, %s, %s, %s) RETURNING id, location_id, min_temperature, max_temperature, capacity;
        """
        new_unit = execute_query(query, (data['locationId'], data['minTemperature'], data['maxTemperature'], data['capacity']), fetch_one=True)
        return jsonify(new_unit), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/storage-units', methods=['GET'])
def get_storage_units():
    try:
        units = execute_query("SELECT * FROM storage_units;", fetch_all=True)
        return jsonify(units), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/routes', methods=['POST'])
def create_route():
    data = request.get_json()
    try:
        query = """
            INSERT INTO routes (from_location_id, to_location_id, capacity, min_shipment) 
            VALUES (%s, %s, %s, %s) RETURNING id, from_location_id, to_location_id, capacity, min_shipment;
        """
        new_route = execute_query(query, (data['fromLocationId'], data['toLocationId'], data['capacity'], data['minShipment']), fetch_one=True)
        return jsonify(new_route), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/routes', methods=['GET'])
def get_routes():
    try:
        routes = execute_query("SELECT * FROM routes;", fetch_all=True)
        return jsonify(routes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/demands', methods=['POST'])
def create_demand():
    data = request.get_json()
    try:
        query = """
            INSERT INTO demands (location_id, product_id, date, min_quantity, max_quantity) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id, location_id, product_id, date, min_quantity, max_quantity;
        """
        new_demand = execute_query(query, (data['locationId'], data['productId'], data['date'], data['minQuantity'], data['maxQuantity']), fetch_one=True)
        return jsonify(new_demand), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/demands', methods=['GET'])
def get_demands():
    try:
        demands = execute_query("SELECT * FROM demands;", fetch_all=True)
        return jsonify(demands), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/network/summary', methods=['GET'])
def get_network_summary():
    try:
        summary = {
            "locations": execute_query("SELECT * FROM locations;", fetch_all=True),
            "products": execute_query("SELECT * FROM products;", fetch_all=True),
            "storageUnits": execute_query("SELECT * FROM storage_units;", fetch_all=True),
            "routes": execute_query("SELECT * FROM routes;", fetch_all=True),
            "demands": execute_query("SELECT * FROM demands;", fetch_all=True)
        }
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/temps/validate', methods=['POST'])
def validate_temps():
    data = request.get_json()
    if not data or 'date' not in data:
        return jsonify({"error": "Missing date"}), 400
    
    target_date = data['date']
    
    try:
        query = """
            SELECT d.id, d.location_id, p.name, p.min_temperature, p.max_temperature
            FROM demands d
            JOIN products p ON d.product_id = p.id
            WHERE d.date = %s
        """
        demands = execute_query(query, (target_date,), fetch_all=True)
        
        issues = []
        for d in demands:
            check_query = """
                SELECT id FROM storage_units 
                WHERE location_id = %s 
                AND min_temperature <= %s 
                AND max_temperature >= %s
            """
            valid_unit = execute_query(check_query, (d['location_id'], d['min_temperature'], d['max_temperature']), fetch_one=True)
            
            if not valid_unit:
                issues.append(f"Product {d['name']} requires temp {d['min_temperature']}-{d['max_temperature']} but no suitable storage found at location.")

        if issues:
            return jsonify({"valid": False, "issues": issues}), 200
        else:
            return jsonify({"valid": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/network/validate', methods=['POST'])
def validate_network():
    data = request.get_json()
    if not data or 'date' not in data:
        return jsonify({"error": "Missing date"}), 400
    
    target_date = data['date']
    issues = []
    
    try:
        demands = execute_query(
            "SELECT location_id, SUM(max_quantity) as total_demand FROM demands WHERE date = %s GROUP BY location_id",
            (target_date,),
            fetch_all=True
        )
        
        if not demands:
            return jsonify({"feasible": True}), 200

        for d in demands:
            loc_id = d['location_id']
            total_needed = d['total_demand']
            
            storage = execute_query(
                "SELECT SUM(capacity) as total_cap FROM storage_units WHERE location_id = %s",
                (loc_id,),
                fetch_one=True
            )
            
            total_capacity = storage['total_cap'] if storage and storage['total_cap'] else 0
            
            if total_needed > total_capacity:
                issues.append(f"MAX_CAPACITY_VIOLATION: Location {loc_id} needs {total_needed} capacity but only has {total_capacity}")

        if issues:
            return jsonify({"feasible": False, "issues": issues}), 200
        else:
            return jsonify({"feasible": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)