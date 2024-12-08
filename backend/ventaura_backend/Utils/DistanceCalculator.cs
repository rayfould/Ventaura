// This file defines a static utility class responsible for calculating the geographical distance between two coordinates.
// It uses the Haversine formula to compute the distance between two latitude-longitude pairs, returning the result in kilometers.
// The DistanceCalculator class is frequently used when combining event data to determine how far events are from the user's location,
// enabling location-based sorting, filtering, or recommendations.

namespace ventaura_backend.Utils
{
    public static class DistanceCalculator
    {
        // Calculates the distance (in kilometers) between two points on the Earth's surface 
        // specified by their latitude and longitude coordinates.
        public static double CalculateDistance(double lat1, double lon1, double lat2, double lon2)
        {
            const double EarthRadius = 6371; // Earth's average radius in kilometers

            // Convert differences in latitude and longitude to radians for the Haversine formula.
            var dLat = DegreesToRadians(lat2 - lat1);
            var dLon = DegreesToRadians(lon2 - lon1);

            // Apply the Haversine formula:
            // a: the square of half the chord length between the points
            // c: the angular distance in radians
            var a = Math.Sin(dLat / 2) * Math.Sin(dLat / 2) +
                    Math.Cos(DegreesToRadians(lat1)) * Math.Cos(DegreesToRadians(lat2)) *
                    Math.Sin(dLon / 2) * Math.Sin(dLon / 2);

            var c = 2 * Math.Atan2(Math.Sqrt(a), Math.Sqrt(1 - a));

            // Multiply by Earth's radius to get distance in kilometers.
            return EarthRadius * c;
        }

        // Converts degrees to radians since trigonometric functions require inputs in radians.
        private static double DegreesToRadians(double degrees)
        {
            return degrees * (Math.PI / 180);
        }
    }
}