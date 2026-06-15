"""
Insights and recommendations service for the Paryavaran application.
Analyzes user carbon footprints and generates personalized reduction tips.
"""
from typing import Dict, List, Any, Optional
from src.models.database import CarbonLog


class InsightsService:
    """
    Service layer containing carbon footprint analytics, comparison against target metrics
    (e.g., Paris Agreement goals), and targeted recommendations based on category breakdown.
    """

    # Annual target footprint per person under Paris Agreement: 2000 kg CO2 (2 tonnes)
    # Monthly target scaled down: ~166.67 kg CO2
    MONTHLY_TARGET_KG: float = 166.67

    @classmethod
    def get_footprint_summary(cls, log: CarbonLog) -> Dict[str, Any]:
        """
        Creates a summary breakdown of a specific carbon log, including percentage composition.
        """
        total = log.total_emissions or 0.1  # Avoid division by zero
        
        breakdown = {
            "transportation": {
                "emissions": log.transport_emissions,
                "percentage": round((log.transport_emissions / total) * 100, 1)
            },
            "electricity": {
                "emissions": log.electricity_emissions,
                "percentage": round((log.electricity_emissions / total) * 100, 1)
            },
            "food": {
                "emissions": log.food_emissions,
                "percentage": round((log.food_emissions / total) * 100, 1)
            },
            "water": {
                "emissions": log.water_emissions,
                "percentage": round((log.water_emissions / total) * 100, 1)
            },
            "waste": {
                "emissions": log.waste_emissions,
                "percentage": round((log.waste_emissions / total) * 100, 1)
            }
        }

        # Compare against Paris Agreement monthly target
        difference = log.total_emissions - cls.MONTHLY_TARGET_KG
        meets_target = difference <= 0

        return {
            "total_emissions": log.total_emissions,
            "logged_at": log.logged_at,
            "breakdown": breakdown,
            "target_comparison": {
                "target": cls.MONTHLY_TARGET_KG,
                "difference": round(difference, 2),
                "meets_target": meets_target,
                "percent_of_target": round((log.total_emissions / cls.MONTHLY_TARGET_KG) * 100, 1)
            }
        }

    @classmethod
    def generate_recommendations(cls, log: CarbonLog, summary: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """
        Generates targeted reduction advice based on which categories dominate the user's footprint.
        """
        if summary is None:
            summary = cls.get_footprint_summary(log)
        breakdown = summary["breakdown"]
        recommendations = []

        # Find highest category
        sorted_categories = sorted(
            breakdown.items(), 
            key=lambda item: item[1]["emissions"], 
            reverse=True
        )
        highest_cat, highest_info = sorted_categories[0]

        # Add primary warning/tip based on highest contributor
        if highest_cat == "transportation" and highest_info["emissions"] > 0:
            recommendations.append({
                "category": "Transportation",
                "priority": "High",
                "tip": "Transportation is your largest emissions source. Consider carpooling, switching to public transit, or cycling/walking for short trips to drastically lower this footprint.",
                "action_type": "commute_bicycle"
            })
        elif highest_cat == "electricity" and highest_info["emissions"] > 0:
            recommendations.append({
                "category": "Electricity",
                "priority": "High",
                "tip": "Electricity usage dominates your footprint. Try unplugging standby devices, upgrading to LED lightbulbs, or looking into local community solar options.",
                "action_type": "unplug_appliances"
            })
        elif highest_cat == "food" and highest_info["emissions"] > 0:
            recommendations.append({
                "category": "Food & Diet",
                "priority": "High",
                "tip": "Dietary choices are leading your footprint. Incorporating vegan or vegetarian days into your weekly routine is one of the most effective personal actions you can take.",
                "action_type": "eat_vegan"
            })
        elif highest_cat == "waste" and highest_info["emissions"] > 0:
            recommendations.append({
                "category": "Waste Management",
                "priority": "High",
                "tip": "Waste generation is your leading contributor. Starting to compost organic waste and actively sorting recyclables can reduce waste emissions by 50% immediately.",
                "action_type": "compost_organic"
            })

        # General supporting recommendations
        if breakdown["transportation"]["percentage"] > 30 and highest_cat != "transportation":
            recommendations.append({
                "category": "Transportation",
                "priority": "Medium",
                "tip": "Your transport emissions are substantial. Opting for public transport over a private petrol car cuts emissions by up to 80% per kilometer.",
                "action_type": "commute_public_transit"
            })

        if breakdown["food"]["percentage"] > 25 and highest_cat != "food":
            recommendations.append({
                "category": "Food & Diet",
                "priority": "Medium",
                "tip": "Switching even just a few meals from red meat to plant-based alternatives significantly reduces agricultural greenhouse gas impact.",
                "action_type": "eat_vegetarian"
            })

        if breakdown["electricity"]["percentage"] > 25 and highest_cat != "electricity":
            recommendations.append({
                "category": "Electricity",
                "priority": "Medium",
                "tip": "Save power by turning off idle appliances and cooling/heating rooms only when occupied.",
                "action_type": "unplug_appliances"
            })

        if breakdown["waste"]["percentage"] > 15 and highest_cat != "waste":
            recommendations.append({
                "category": "Waste Management",
                "priority": "Medium",
                "tip": "Help divert methane-producing waste from landfills by starting a simple backyard or indoor compost system.",
                "action_type": "compost_organic"
            })

        # Add a default recommendation if list is too short
        if len(recommendations) < 2:
            recommendations.append({
                "category": "General",
                "priority": "Medium",
                "tip": "Log your sustainable habits daily to earn bonus points and maintain your eco-streak!",
                "action_type": "recycle_items"
            })

        return recommendations
