/* This file defines the CombinedAPIService, a service that aggregates data from multiple APIs 
(Amadeus and Ticketmaster) in the Ventaura application. It acts as a unified interface to fetch 
and combine event and activity data based on a user's location, enabling seamless integration 
of multiple data sources for personalized recommendations. */

using ventaura_backend.Models;

public class CombinedAPIService
{
    // Services for interacting with Amadeus and Ticketmaster APIs.
    private readonly ventaura_backend.Services.AmadeusService _amadeusService;
    private readonly ventaura_backend.Services.TicketmasterService _ticketmasterService;

    // Constructor to inject the Amadeus and Ticketmaster services.
    public CombinedAPIService(ventaura_backend.Services.AmadeusService amadeusService, ventaura_backend.Services.TicketmasterService ticketmasterService)
    {
        _amadeusService = amadeusService;
        _ticketmasterService = ticketmasterService;
    }

    // Method to fetch and combine events from Amadeus and Ticketmaster APIs.
    public async Task<List<UserContent>> FetchEventsAsync(double latitude, double longitude, int userId)
    {
        // Fetch events from the Amadeus API.
        var amadeusEvents = await _amadeusService.FetchAmadeusEventsAsync(latitude, longitude, userId);

        // Fetch events from the Ticketmaster API.
        var ticketmasterEvents = await _ticketmasterService.FetchTicketmasterEventsAsync(latitude, longitude, userId);

        var events = amadeusEvents.Concat(ticketmasterEvents).ToList();

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
