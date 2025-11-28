import httpx
from typing import Optional, Dict, Any


class NHTSAService:
    """Service for validating vehicles against NHTSA API."""
    
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"
    
    @staticmethod
    async def decode_vin(vin: str) -> Dict[str, Any]:
        """
        Decode a VIN using NHTSA API.
        Returns vehicle information if valid, or error info if invalid.
        """
        url = f"{NHTSAService.BASE_URL}/DecodeVin/{vin}?format=json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("Results", [])
                
                # Check for error codes in results
                error_code = None
                make = None
                model = None
                year = None
                body_class = None
                
                for item in results:
                    var = item.get("Variable", "")
                    value = item.get("Value")
                    
                    if var == "Error Code":
                        error_code = value
                    elif var == "Make" and value:
                        make = value
                    elif var == "Model" and value:
                        model = value
                    elif var == "Model Year" and value:
                        year = value
                    elif var == "Body Class" and value:
                        body_class = value
                
                # Error codes: 0 = no error, 1-4 = minor issues, 5+ = invalid
                if error_code and error_code not in ["0", "1", "6"]:
                    return {
                        "valid": False,
                        "error": f"Invalid VIN. Please check and try again."
                    }
                
                if not make:
                    return {
                        "valid": False,
                        "error": "Could not decode VIN. Please verify it's correct."
                    }
                
                return {
                    "valid": True,
                    "make": make,
                    "model": model,
                    "year": year,
                    "body_class": body_class
                }
                
            except httpx.TimeoutException:
                return {
                    "valid": False,
                    "error": "Vehicle verification service timed out. Please try again."
                }
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Error verifying vehicle: {str(e)}"
                }
    
    @staticmethod
    async def validate_year_make(year: int, make: str) -> Dict[str, Any]:
        """
        Validate that a make exists for a given year using NHTSA API.
        """
        url = f"{NHTSAService.BASE_URL}/GetMakesForVehicleType/car?format=json"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("Results", [])
                makes = [r.get("MakeName", "").upper() for r in results]
                
                if make.upper() in makes:
                    return {"valid": True}
                
                # Also check against all makes
                all_makes_url = f"{NHTSAService.BASE_URL}/GetAllMakes?format=json"
                response = await client.get(all_makes_url, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("Results", [])
                all_makes = [r.get("Make_Name", "").upper() for r in results]
                
                if make.upper() in all_makes:
                    return {"valid": True}
                
                return {
                    "valid": False,
                    "error": f"'{make}' doesn't appear to be a valid vehicle make. Please check the spelling."
                }
                
            except httpx.TimeoutException:
                # On timeout, assume valid to not block user
                return {"valid": True, "warning": "Could not verify make, proceeding anyway."}
            except Exception:
                return {"valid": True, "warning": "Could not verify make, proceeding anyway."}

