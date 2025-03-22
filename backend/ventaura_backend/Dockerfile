# Base image for runtime
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

# Build image with SDK
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ventaura_backend.csproj .
RUN dotnet restore
COPY . .
RUN dotnet build -c Release -o /app/build

# Publish the app
FROM build AS publish
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

# Final runtime image
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
# Copy .env file (if needed, though Fly.io secrets are preferred)
COPY .env ./
# Ensure DotNetEnv loads the .env file (optional if using Fly.io secrets)
ENV ASPNETCORE_ENVIRONMENT=Production
ENTRYPOINT ["dotnet", "ventaura_backend.dll"]