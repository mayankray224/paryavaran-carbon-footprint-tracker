"""
Carbon calculator service for the Paryavaran application.
Implements calculations of carbon footprint based on standard environmental coefficients.
"""
from typing import Dict, Any


class CarbonCalculatorService:
    """
    Provides functions to calculate greenhouse gas emissions in kilograms of CO2 equivalent (kg CO2e)
    for various activities (transportation, energy, food, water, waste).
    """

    # Emission factors in kg CO2e per unit
    TRANSPORT_FACTORS: Dict[str, float] = {
        "petrol_car": 0.20,      # per km
        "diesel_car": 0.17,      # per km
        "electric_car": 0.05,    # per km (average grid charging intensity)
        "motorbike": 0.10,       # per km
        "public_transit": 0.04,  # per km (bus/train average)
        "bicycle_or_walk": 0.00  # zero emissions
    }

    # Grid electricity emission factor: kg CO2e per kWh
    ELECTRICITY_FACTOR: float = 0.82

    # Diet emission factors: kg CO2e per day of adherence
    DIET_FACTORS: Dict[str, float] = {
        "heavy_meat": 7.20,
        "flexitarian": 4.00,
        "vegetarian": 2.50,
        "vegan": 1.50
    }

    # Water consumption emission factor: kg CO2e per liter (processing & distribution energy)
    WATER_FACTOR: float = 0.0003

    # Waste generation emission factor: kg CO2e per kg of municipal waste
    WASTE_FACTOR: float = 0.50
    # Waste reduction factor if composting/recycling is active (50% reduction)
    RECYCLING_DISCOUNT: float = 0.50

    @classmethod
    def calculate_transport(cls, distance_km: float, vehicle_type: str) -> float:
        """
        Calculates transport emissions.
        :param distance_km: Distance traveled in kilometers.
        :param vehicle_type: Type of vehicle used.
        :return: Emissions in kg CO2e.
        """
        if distance_km < 0:
            raise ValueError("Distance cannot be negative")
        factor = cls.TRANSPORT_FACTORS.get(vehicle_type, 0.20)  # default to petrol car
        return round(distance_km * factor, 2)

    @classmethod
    def calculate_electricity(cls, kwh_used: float) -> float:
        """
        Calculates electricity emissions.
        :param kwh_used: Electricity consumed in kilowatt-hours.
        :return: Emissions in kg CO2e.
        """
        if kwh_used < 0:
            raise ValueError("Electricity usage cannot be negative")
        return round(kwh_used * cls.ELECTRICITY_FACTOR, 2)

    @classmethod
    def calculate_food(cls, diet_type: str, days: int) -> float:
        """
        Calculates diet-related emissions.
        :param diet_type: Primary dietary pattern.
        :param days: Number of days in the period.
        :return: Emissions in kg CO2e.
        """
        if days < 0:
            raise ValueError("Days cannot be negative")
        factor = cls.DIET_FACTORS.get(diet_type, 2.50)  # default to vegetarian
        return round(days * factor, 2)

    @classmethod
    def calculate_water(cls, liters_used: float) -> float:
        """
        Calculates water emissions.
        :param liters_used: Water consumed in liters.
        :return: Emissions in kg CO2e.
        """
        if liters_used < 0:
            raise ValueError("Water usage cannot be negative")
        return round(liters_used * cls.WATER_FACTOR, 2)

    @classmethod
    def calculate_waste(cls, waste_kg: float, recycles_or_composts: bool) -> float:
        """
        Calculates waste-related emissions.
        :param waste_kg: Quantity of waste generated in kilograms.
        :param recycles_or_composts: Whether the user actively recycles or composts.
        :return: Emissions in kg CO2e.
        """
        if waste_kg < 0:
            raise ValueError("Waste quantity cannot be negative")
        factor = cls.WASTE_FACTOR
        if recycles_or_composts:
            factor *= cls.RECYCLING_DISCOUNT
        return round(waste_kg * factor, 2)

    @classmethod
    def calculate_total_footprint(cls, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes the complete carbon footprint breakdown from standard input dict.
        Expected keys:
            - transport_distance (float)
            - vehicle_type (str)
            - electricity_kwh (float)
            - diet_type (str)
            - diet_days (int)
            - water_liters (float)
            - waste_kg (float)
            - recycles_or_composts (bool)
        """
        try:
            transport = cls.calculate_transport(
                float(inputs.get("transport_distance", 0)),
                str(inputs.get("vehicle_type", "petrol_car"))
            )
            electricity = cls.calculate_electricity(
                float(inputs.get("electricity_kwh", 0))
            )
            food = cls.calculate_food(
                str(inputs.get("diet_type", "vegetarian")),
                int(inputs.get("diet_days", 0))
            )
            water = cls.calculate_water(
                float(inputs.get("water_liters", 0))
            )
            waste = cls.calculate_waste(
                float(inputs.get("waste_kg", 0)),
                bool(inputs.get("recycles_or_composts", False))
            )

            total = round(transport + electricity + food + water + waste, 2)

            return {
                "transport_emissions": transport,
                "electricity_emissions": electricity,
                "food_emissions": food,
                "water_emissions": water,
                "waste_emissions": waste,
                "total_emissions": total
            }
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid input data type: {str(e)}")
