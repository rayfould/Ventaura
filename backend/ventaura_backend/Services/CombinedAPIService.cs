/* This file defines the CombinedAPIService, a service that aggregates data from multiple APIs 
(Amadeus and Ticketmaster) in the Ventaura application. It acts as a unified interface to fetch 
and combine event and activity data based on a user's location, enabling seamless integration 
of multiple data sources for personalized recommendations. */

using ventaura_backend.Models;
using ventaura_backend.Services;

public class CombinedAPIService
{
    // Services for interacting with Amadeus, Yelp and Ticketmaster APIs.
    private readonly TicketmasterService _ticketmasterService;
    private readonly YelpFusionService _yelpFusionService;
    // private readonly AmadeusService _amadeusService;



    // Constructor to inject the Amadeus and Ticketmaster services.
    public CombinedAPIService(TicketmasterService ticketmasterService, YelpFusionService yelpFusionService)
    {
        _ticketmasterService = ticketmasterService;
        _yelpFusionService = yelpFusionService;
        // _amadeusService = amadeusService;

    }

    // Method to fetch and combine events from Amadeus and Ticketmaster APIs.
    public async Task<List<UserContent>> FetchEventsAsync(double latitude, double longitude, int userId)
    {
        // Fetch events from the Amadeus API.
        // var amadeusEvents = await _amadeusService.FetchAmadeusEventsAsync(latitude, longitude, userId);

        // Fetch events from the Ticketmaster API.
        var ticketmasterEvents = await _ticketmasterService.FetchTicketmasterEventsAsync(latitude, longitude, userId);

        // Fetch events from the Yelp API.
        // var yelpEvents = await _yelpFusionService.FetchYelpEventsAsync(latitude, longitude, userId);

        // Combine the results of the API calls.
        // var events = ticketmasterEvents.Concat(yelpEvents).ToList();

        Console.WriteLine($"Fetched {ticketmasterEvents.Count} events from Ticketmaster.");
        // Console.WriteLine($"Fetched {yelpEvents.Count} events from Yelp.");

        var events = ticketmasterEvents.ToList();

        /* // Log each event's details for debugging.
        foreach (var e in events)
        {
            Console.WriteLine($"List of events and their values for Content ID {e.ContentId}: Title: {e.Title}, Description: {e.Description}, Location: {e.Location}, " +
                            $"Start: {e.Start}, Source: {e.Source}, Type: {e.Type}, " +
                            $"CurrencyCode: {e.CurrencyCode}, Amount: {e.Amount}, URL: {e.URL}");
        }*/

        // Combine the events from both APIs into a single list and return it.
        return events;
    }
}
