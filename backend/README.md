***VENTAURA BACKEND OVERVIEW***

The Ventaura backend provides an API-driven service for event discovery, user account management, event ranking, and integration with external event APIs. Built with ASP.NET Core and Entity Framework Core, the backend connects to a PostgreSQL database, communicates with external APIs, and supports Stripe payment integration. This document explains the overall architecture, the purposes of each file, and how the components work together.

ventaura-backend/
├─ Controllers/
│  ├─ UsersController.cs
│  ├─ EventsController.cs
│  ├─ CombinedEventsController.cs
│  └─ GlobalEventsController.cs
│
├─ Data/
│  ├─ DatabaseContext.cs
│
├─ Models/
│  ├─ User.cs
│  ├─ HostEvent.cs
│  ├─ CombinedEvent.cs
│
├─ Services/
│  ├─ TicketmasterService.cs
│  ├─ AmadeusService.cs
│  ├─ CombinedAPIService.cs
│  ├─ GoogleGeocodingService.cs
│  ├─ YelpFusionService.cs
│  └─ RankingService.cs
│
├─ Utils/
│  ├─ DistanceCalculator.cs
│
├─ Program.cs (or main entry file)
└─ Other supporting files (e.g., DTOs, configuration, etc.)

***KEY DIRECTORIES***

Controllers/: Contains all API controllers that handle HTTP requests and responses.
Data/: Holds the database context for Entity Framework Core, defining how the database is accessed.
Models/: Contains the entity classes that map directly to database tables and represent domain objects.
Services/: Provides business logic or external API integration functionality, keeping controllers lean.
Utils/: Contains utility classes for tasks like distance calculation.

***FILE-BY-FILE EXPLANATION***

Program.cs (Main Entry Point)
Purpose:
This file configures and starts the web application. It sets up:

Services: Registers services like the database context, external API services, and CORS policies.
Middleware: Adds middleware for routing, error handling, and Swagger for API documentation.
Stripe Integration: Configures Stripe payment settings and endpoints.
Startup Logic: At the end, app.Run() starts the server, making the API endpoints available.
How It Fits In:
It’s the launch point of the backend application. Once started, it uses the registered controllers and services to respond to incoming HTTP requests.

***CONTROLLERS***

1. UsersController.cs

Purpose:
Handles user-related operations:

Account Creation (POST /api/users/create-account): Creates new user accounts, storing securely hashed passwords.
User Retrieval (GET /api/users/{id}): Fetches user details by ID.
Login (POST /api/users/login): Authenticates users, updates their location if provided, and sets their logged-in status.
Update Preferences (PUT /api/users/updatePreferences): Allows updating user profile fields like email, preferences, and location.
How It Fits In:
Manages user onboarding, authentication, and profile management, ensuring a personalized event experience for each user.

2. EventsController.cs

Purpose:
Handles event ranking operations:

Ranking Endpoint (POST /api/events/rank/{userId}): Invokes the RankingService to compute event rankings for a given user.
How It Fits In:
Provides a gateway to the internal logic that sorts or prioritizes events based on the user’s preferences or other criteria.

3. CombinedEventsController.cs

Purpose:
Integrates external events (from APIs like Ticketmaster or Amadeus) with locally hosted events:

Fetch Combined Events (GET /api/combined-events/fetch?userId=...): Retrieves user’s location, fetches both external and host events, calculates distances, and stores them in a CSV file.
Logout (POST /api/combined-events/logout?userId=...): Logs out the user and cleans up their associated CSV file.
Create Host Event (POST /api/combined-events/create-host-event): Adds new host events to the database.
How It Fits In:
Merges multiple event sources into a unified feed, enabling the application to provide comprehensive event listings tailored to the user’s location and preferences.

4. GlobalEventsController.cs

Purpose:
Searches for events globally based on a city query:

Search Events (GET /api/global-events/search?city=...&userId=...): Geocodes the city, fetches events near that location, assigns unique IDs, and calculates distance from the user’s coordinates.
How It Fits In:
Extends the application’s capability to allow users to search events in any city, integrating with geocoding and event APIs for a location-based experience.

***MODELS***

1. User.cs 

Represents application users with fields for name, email, password hash, preferences, and location.

2. HostEvent.cs

Purpose:
Represents events created by a host user. Stores details like title, description, location, start time, pricing, and host user ID.

How It Fits In:
Host events are stored locally in the database and can be combined with external events, offering a unified event experience.

3. CombinedEvent.cs

Purpose:
A unified model for displaying events from various sources in a consistent format. Contains fields for title, description, location, time, cost, URL, and distance.

How It Fits In:
Facilitates merging host and external events into a single list for display and processing.

***SERVICES***

TicketmasterService and AmadeusService

Purpose:
Integrate with external event provider APIs (e.g., Ticketmaster, Amadeus) to fetch events based on location or other parameters.

How It Fits In:
Feed external event data into the CombinedAPIService, which merges them with host events for the user.

2. CombinedAPIService

Purpose:
Calls other services (e.g., Ticketmaster, Amadeus) and the database to produce a combined list of events.
How It Fits In:
Centralizes logic for fetching and merging different event sources, simplifying the controllers’ responsibilities.
3. GoogleGeocodingService and YelpFusionService

Purpose:
External API integrations for geocoding (converting city names to coordinates) and retrieving data from Yelp if needed.

How It Fits In:
Used by controllers (e.g., GlobalEventsController) to resolve user input (like city names) into coordinates, enabling location-based queries.

4. RankingService

Purpose:
Provides business logic to rank events for a user based on their preferences, dislikes, or other factors.

How It Fits In:
Invoked by EventsController to provide a sorted list of events tailored to the user’s interests.

***DATA***

DatabaseContext.cs

Purpose:
Defines the Entity Framework Core context that maps models (e.g., User, HostEvent) to the PostgreSQL database. Handles database connectivity and migrations.

How It Fits In:
Serves as the data layer, enabling controllers and services to query and store data through a consistent and type-safe interface.

***UTILS***

DistanceCalculator.cs

Purpose:
Calculates the geographic distance between two coordinates (e.g., user’s location and event location).

How It Fits In:
Supports location-based filtering and sorting by providing a common utility for distance calculations.

***HOW IT WORKS (HIGH LEVEL  FLOW)***

User Onboarding & Authentication:

A user creates an account (UsersController), enters credentials, and logs in.
Upon login, their location can be updated to enable location-based event recommendations.
Fetching and Combining Events:

The user requests events via CombinedEventsController or GlobalEventsController.
The controllers query external APIs (through services like TicketmasterService) and local host events from the database.
Events are merged into CombinedEvent objects, distances from the user’s location are calculated (DistanceCalculator), and the results are optionally saved as a CSV file.
Ranking & Preferences:

The user’s preferences can be updated (UsersController) and events can be ranked (EventsController), providing a personalized event experience.
Stripe Integration:

The Program.cs configures endpoints for creating and handling Stripe checkout sessions.
Allows monetization of events or premium features if required.

This backend architecture is modular, separating concerns between controllers, services, models, and utilities. Controllers handle HTTP requests, services encapsulate logic and external integrations, models define data structures, and utilities provide shared logic. Together, they form a scalable, maintainable, and testable backend solution that supports dynamic event discovery, user management, and personalized recommendations.