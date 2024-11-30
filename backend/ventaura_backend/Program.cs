/* This file is the main entry point for the Ventaura application's backend, 
configuring and starting the web server. It sets up services, middleware, and the application's 
routing. It ensures proper integration of database, API services, CORS policies, and development 
tools like Swagger for API documentation. */

using Microsoft.EntityFrameworkCore;
using ventaura_backend.Data; // For DatabaseContext
using ventaura_backend.Services; // For TicketmasterService, AmadeusService, and CombinedAPIService

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers(); // Enables the use of controllers in the application.

// Register DatabaseContext to use PostgreSQL with the specified connection string.
builder.Services.AddDbContext<DatabaseContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// Register application services for dependency injection.
builder.Services.AddScoped<TicketmasterService>(); // Service for Ticketmaster API interactions.
builder.Services.AddScoped<AmadeusService>(); // Service for Amadeus API interactions.
builder.Services.AddScoped<CombinedAPIService>(); // Service for combining API results.

// Add CORS policy to allow cross-origin requests (useful for frontend-backend integration).
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin() // Allow requests from any origin.
              .AllowAnyMethod() // Allow any HTTP method (e.g., GET, POST).
              .AllowAnyHeader(); // Allow any HTTP headers.
    });
});

// Register HttpClient for making HTTP requests to external APIs.
builder.Services.AddHttpClient();
builder.Services.AddHttpClient<GoogleGeocodingService>();

// Register Swagger for API documentation and testing.
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddHttpClient("RankingAPI", client =>
{
    client.BaseAddress = new Uri("http://localhost:8000");
});


var app = builder.Build();

// Use the configured CORS policy.
app.UseCors("AllowAll");

// Configure the HTTP request pipeline for development and production environments.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage(); // Show detailed error pages in development mode.
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger(); // Enable Swagger for API documentation.
    app.UseSwaggerUI(); // Serve Swagger UI for easy API testing.
}

app.UseRouting(); // Enable endpoint routing.
app.UseAuthorization(); // Enable authorization middleware (if required).

app.MapControllers(); // Map controller routes.

app.Run(); // Start the application.
