/* This file is the main entry point for the Ventaura application's backend, 
configuring and starting the web server. It sets up services, middleware, and the application's 
routing. It ensures proper integration of database, API services, CORS policies, and development 
tools like Swagger for API documentation. */

using Microsoft.EntityFrameworkCore;
using ventaura_backend.Data; // For DatabaseContext 
using ventaura_backend.Services; // For TicketmasterService, AmadeusService, and CombinedAPIService

//for Stripe things
using Microsoft.Extensions.FileProviders;
using Microsoft.Extensions.Options;
using Stripe;
using Stripe.Checkout;
using System.IO;

//Loads .env for Stripe
DotNetEnv.Env.Load();

var builder = WebApplication.CreateBuilder(args);

// Load environment variables into the configuration, this is for Stripe
builder.Services.Configure<StripeOptions>(options =>
{
    options.PublishableKey = Environment.GetEnvironmentVariable("STRIPE_PUBLISHABLE_KEY");
    options.SecretKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY");
    options.WebhookSecret = Environment.GetEnvironmentVariable("STRIPE_WEBHOOK_SECRET");
    options.Price = Environment.GetEnvironmentVariable("PRICE");
    options.Domain = Environment.GetEnvironmentVariable("DOMAIN");
});

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

//Allows access of this for our frontend
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactApp", builder =>
    {
        builder.WithOrigins("http://localhost:3000") // React development server URL
               .AllowAnyMethod()
               .AllowAnyHeader();
    });
});

var app = builder.Build();

// Use the configured CORS policy.
app.UseCors("AllowAll");

// Stripe secret key to enable functionality
StripeConfiguration.ApiKey = Environment.GetEnvironmentVariable("STRIPE_SECRET_KEY");

//Get price variable from .env
var price = Environment.GetEnvironmentVariable("PRICE");

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

//ALL OF THE BELOW UNTIL ALL CAPS IS FOR STRIPE, NEWLY ADDED BY SAM
// Serve static files (if applicable)
app.UseStaticFiles(new StaticFileOptions()
{
    FileProvider = new PhysicalFileProvider(
        Path.Combine(Directory.GetCurrentDirectory(),
        Environment.GetEnvironmentVariable("STATIC_DIR"))
    ),
    RequestPath = new PathString("")
});

// Serve the HTML for the frontend
app.MapGet("/", () => Results.Redirect("index.html"));

// Get session details from Stripe
app.MapGet("checkout-session", async (string sessionId) =>
{
    var service = new SessionService();
    var session = await service.GetAsync(sessionId);
    return Results.Ok(session);
});

// Handle creating a checkout session
app.MapPost("/api/create-checkout-session", async (IOptions<StripeOptions> options, HttpContext context) =>
{
    var sessionOptions = new SessionCreateOptions
    {
        SuccessUrl = $"{options.Value.Domain}/success.html?session_id={{CHECKOUT_SESSION_ID}}",
        CancelUrl = $"{options.Value.Domain}/canceled.html",
        Mode = "payment",
        LineItems = new List<SessionLineItemOptions>
        {
            new SessionLineItemOptions
            {
                Quantity = 1,
                Price = options.Value.Price,
            },
        },
    };

    var service = new SessionService();
    var session = await service.CreateAsync(sessionOptions);
    context.Response.Headers.Add("Location", session.Url);
    return Results.StatusCode(303);
});

app.UseCors("AllowReactApp");

//THIS IS THE END OF WHAT SAM NEWLY ADDED

app.UseRouting(); // Enable endpoint routing.
app.UseAuthorization(); // Enable authorization middleware (if required).

app.MapControllers(); // Map controller routes.

app.Run(); // Start the application.