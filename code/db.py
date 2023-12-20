import dotenv, os
import psycopg2
from enum import Enum

dotenv.load_dotenv() # set environment variables

# Set these based on the raspberry pi configuration
MIN_PIN_NUMBER = 1
MAX_PIN_NUMBER = 28

DBError = Enum("DBError", ["FAILED_TO_CONNECT", "NO_ALIAS_FOUND", "INVALID_PIN", "POSTGRES_EXCEPTION"])

class DBResponse:
    success = False
    data = None
    error = None

# Public database methods

# Returns whether or not the pin(s) specified by an alias is enabled
def getPinEnabled(name):
    return _dbAction(func=_getPinEnabled, name=name)

# Turns on/off the pin(s) attached to a specified alias. Returns a list of updated pin numbers
def setPinEnabled(name, enabled):
    return _dbAction(func=_setPinEnabled, name=name, enabled=enabled)

# Set the alias for a pin
def aliasPin(name, pinNumber):
    return _dbAction(func=_aliasPin, name=name, pinNumber=pinNumber)

# Remove a pin from the database
def unsetPin(pinNumber):
    return _dbAction(func=_unsetPin, pinNumber=pinNumber)

# Return a dictionary of configured pins and their on/off status. Used in GPIO setup
def getPinConfig():
    return _dbAction(func=_getPinConfig)

# Add a new log entry from the provided JSON. Format: {"role": "string", "content": "string"}
def addLogEntry(log):
    return _dbAction(func=_addLogEntry, type=log.get("role"), content=log.get("content"))

# Return all log entries in the order they were added as a list of {"role": "string", "content": "string"}. If numberOfLogs is not specified, return all logs
def getLogs(numberOfLogs=None):
    return _dbAction(func=_getLogEntries, n=numberOfLogs)

# ===================================================================================================
# The methods below are not meant to be called directly. They are called by the public methods above.

# This function takes in a pin number and checks if it is a pin that can be set by voice command. For example, 
# the pin attached to the microphone is not a valid pin.
def checkValidPin(pinNumber):
    return pinNumber >= MIN_PIN_NUMBER and pinNumber <= MAX_PIN_NUMBER

# This function is a wrapper for all database actions. It handles connecting to the database, executing the action, and closing the connection
def _dbAction(func, **kwargs):
    response = DBResponse()
    database = None
    cursor = None
    try:
        database = psycopg2.connect(
            host="127.0.0.1",
            user=os.environ.get("DATABASE_USERNAME"),
            password=os.environ.get("DATABASE_PASSWORD"),
            database="main"
        )
        cursor = database.cursor()
        response = func(database=database, cursor=cursor, **kwargs)
    except Exception as e:
        print(f"Exception when connecting to database: {e}")
        response.success = False
        response.error = DBError.FAILED_TO_CONNECT
        response.data = e
    finally:
        if database:
            cursor.close()
            database.close()
        return response
    
def _getPinEnabled(database, cursor, name):
    response = DBResponse()
    try:
        # Select the pin(s) with the specified alias
        cursor.execute(f"SELECT * FROM pins WHERE alias='{name}';")
        (pin_id, alias, enabled) = cursor.fetchone()
        response.success = True
        response.error = None
        response.data = enabled
    except Exception as e:
        response.success = False
        response.error = DBError.NO_ALIAS_FOUND
        response.data = e
    finally:
        return response

def _setPinEnabled(database, cursor, name, enabled):
    response = DBResponse()
    try:
        # Set "on" field for pins with the specified alias
        cursor.execute(f"UPDATE pins SET enabled={enabled} WHERE alias='{name}';")
        database.commit()
        cursor.execute(f"SELECT * FROM pins WHERE alias='{name}';")
        matched = cursor.fetchall()
        updatedPins = []
        for (pin_id, alias, enabled) in matched:
            updatedPins.append(pin_id)
        response.success = True
        response.error = None
        response.data = updatedPins
    except Exception as e:
        response.success = False
        response.error = DBError.NO_ALIAS_FOUND
        response.data = e
    finally:
        return response
    
def _aliasPin(database, cursor, name, pinNumber):
    response = DBResponse()
    if not checkValidPin(pinNumber):
        response.success = False
        response.error = DBError.INVALID_PIN
        response.data = None
        return response
    try:
        # Assign a pin ID to an alias. By default, the pin is off when it is assigned
        cursor.execute(f"INSERT INTO pins (pin_id, alias, enabled) VALUES({pinNumber}, '{name}', false) ON CONFLICT (pin_id) DO UPDATE SET alias='{name}', enabled=false")
        response.success = True
        response.error = None
        response.data = None
        database.commit()
    except Exception as e:
        response.success = False
        response.error = DBError.POSTGRES_EXCEPTION
        response.data = e
    finally:
        return response
    
def _unsetPin(database, cursor, pinNumber):
    response = DBResponse()
    if not checkValidPin(pinNumber):
        response.success = False
        response.error = DBError.INVALID_PIN
        response.data = None
        return response
    try:
        # Remove the pin from the database
        cursor.execute(f"DELETE FROM pins WHERE pin_id='{pinNumber}'")
        response.success = True
        response.error = None
        response.data = None
        database.commit()
    except Exception as e:
        response.success = False
        response.error = DBError.POSTGRES_EXCEPTION
        response.data = e
    finally:
        return response
    
def _getPinConfig(database, cursor):
    response = DBResponse()
    try:
        # Select the pin(s) with the specified alias
        cursor.execute(f"SELECT * FROM pins;")
        fetched = cursor.fetchall()
        results = dict()
        for (pin_id, alias, enabled) in fetched:
            results[str(pin_id)] = enabled
        response.success = True
        response.error = None
        response.data = results
    except Exception as e:
        response.success = False
        response.error = DBError.POSTGRES_EXCEPTION
        response.data = e
    finally:
        return response
    
def _addLogEntry(database, cursor, type, content):
    response = DBResponse()
    try:
        # Add a log entry
        cursor.execute(f"INSERT INTO logs (type, content) VALUES('{type}', '{content}');")
        response.success = True
        response.error = None
        response.data = None
        database.commit()
    except Exception as e:
        response.success = False
        response.error = DBError.POSTGRES_EXCEPTION
        response.data = e
    finally:
        return response
    
def _getLogEntries(database, cursor, n):
    response = DBResponse()
    try:
        # Add a log entry
        if n is not None:
            cursor.execute(f"SELECT * FROM logs ORDER BY id DESC LIMIT {n};")
        else:
            cursor.execute(f"SELECT * FROM logs ORDER BY id DESC;")
        logs = cursor.fetchall()
        response.success = True
        response.error = None
        response.data = []
        for (type, content, id) in reversed(logs):
            response.data.append({"role": type, "content": content})
    except Exception as e:
        response.success = False
        response.error = DBError.POSTGRES_EXCEPTION
        response.data = e
    finally:
        return response

def _setupPinTable(database, cursor):
    try:
        # Pin row format: (numeric pin_id, text alias, bool enabled)
        cursor.execute(
            """
            CREATE TABLE pins (
                pin_id integer PRIMARY KEY NOT NULL,
                alias text,
                enabled boolean NOT NULL DEFAULT false
            );
            """
        )
        database.commit()
        print("Pin table setup successful!")
    except Exception as e:
        print(f"Failed to set up pin table: {e}")
        
def _setupLogTable(database, cursor):
    try:
        # Pin row format: (text type, text content)
        cursor.execute(
            """
            CREATE TABLE logs (
                type text,
                content text
            );
            """
        )
        cursor.execute(
            """
            ALTER TABLE logs ADD COLUMN id SERIAL PRIMARY KEY;
            """
        )
        database.commit()
        print("Log table setup successful!")
    except Exception as e:
        print(f"Failed to set up log table: {e}")

# Only create database table if this module is called directly
if __name__ == "__main__":
    _dbAction(func=_setupPinTable)
    _dbAction(func=_setupLogTable)

    
