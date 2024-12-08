***VENTAURA APPLICATION SETUP***

**Table of Contents**
- Overview
- Technologies Used
- System Requirements
- Project Structure
- Setting Up the Backend
- Environment Variables
- Database Setup
- Running the Backend
- Setting Up the Frontend
- Stripe Integration
- Additional Notes
- Common Troubleshooting

**Overview**

The Ventaura application consists of two main parts: a backend (ASP.NET Core) and a frontend (React). The backend provides a RESTful API for user management, event retrieval and merging, geocoding, and event ranking. It connects to external services (such as Ticketmaster and Amadeus APIs) and a PostgreSQL database (Supabase) to store user data and host events. The frontend consumes the backend API to deliver a responsive, user-friendly interface for viewing and interacting with events.

**Technologies Used**

***Backend:***

ASP.NET Core / C#: For building APIs and implementing business logic.

Entity Framework Core: For database operations and migrations.

PostgreSQL: The relational database used to store users and host events (Managed by Supabase).

Stripe: For payment handling and checkout sessions.

External APIs: Ticketmaster, Amadeus, Google Geocoding, Yelp Fusion.

***Frontend:***

React (JavaScript/TypeScript): For building a modern, interactive, and responsive web UI.

Axios or Fetch API: To communicate with the backend services.

Development Tools:

Swagger: For API documentation and testing.

CORS Policies: To allow the frontend to communicate with the backend during development.

**System Requirements**

.NET 7.0 SDK or compatible (for backend development)

Node.js (v14 or later) and npm or yarn (for frontend development)

PostgreSQL database (Supabase instance or local Postgres)

Git (for version control)

A modern browser (for running the frontend)

Stripe account (optional, if you plan to use payment functionality)

API keys for external services like Ticketmaster, Amadeus, Google Maps Geocoding, and Yelp Fusion (if required).

**TO RUN**

1. In a terminal, change into the backend/ventaura_backend directory.
   
   Run the following:
   
                      dotnet restore
   
                      dotnet build
   
                      dotnet run

3. In a new terminal, change into the backend/Ranking directory.
   
   Run the following:
   
                      pip install fastapi
   
                      pip install uvicorn
   
                      python app.py

5. In a new terminal, change into the frontend directory.
   
   Run the following:

                      npm start

Access the website at: http://localhost:3000/

Enjoy!

FOR DEVELOPER: SUPABASE: https://supabase.com/dashboard/project/lzrnyahwsvygmcdqofkm