**Ventaura Application Setup**

Welcome to the Ventaura project! Follow this guide to set up the application on your local machine and start both the backend and frontend servers.

**Overview**

Ventaura is a full-stack web application with the following components:

Backend: Built with C# and ASP.NET Core, using PostgreSQL as the database.

Frontend: Built with React.

The default database connection string is preconfigured in appsettings.json as:

"ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=ventaura;Username=postgres;Password=password;"
}

This guide ensures the database and application setup match this configuration.

**Prerequisites**

Before starting, ensure the following are installed on your system:

- .NET SDK (6.0 or higher)

- Node.js (18.x or higher) and npm (8.x or higher)

- PostgreSQL (14.x or higher)

- A terminal or command-line tool (e.g., Bash, Git Bash, or Command Prompt).

**Step-by-Step Setup**

_1. Clone the Repository_
   
Open a terminal.

Run the following commands:

git clone https://github.com/your-repo-url/Ventaura.git

cd Ventaura

_2. Set Up the PostgreSQL Database_

To automate the database setup:

Open the setup.sh script in the backend.

Run the setup script: bash setup.sh

This script will:

Create a database named ventaura.

Create a user (postgres) with the password password.

Grant all privileges on the ventaura database to the postgres user.

Verify the Setup

After running the script, verify the database was created successfully:

psql -h localhost -p 5432 -U postgres -d ventaura -W

When prompted, enter the password password (which is 'password'). If the connection is successful, the setup is complete.

_3. Apply Database Migrations_

Navigate to the backend/ventaura_backend directory and run:

dotnet ef database update

This command applies the database schema to your ventaura database.

_4. Start the Backend Server_

From the backend directory, run:

dotnet run

The backend server will start and be available at: http://localhost:5152

_5. Set Up and Start the Frontend_

Navigate to the frontend directory: cd ../frontend

Install the required dependencies: npm install

Start the React development server: npm start

The frontend will start and be available at: http://localhost:3000

Navigate to this link to test the application which will be connected to the backend. 
