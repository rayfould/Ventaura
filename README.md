***Ventaura Application Setup***

Welcome to the Ventaura project! Follow the instructions below to set up the application on your local machine and start running the backend and frontend servers so you can try out our app!

***Prerequisites***
Before you begin, ensure you have the following installed on your system:

_.NET SDK (6.0 or higher)_

_Node.js (18.x or higher) and npm (8.x or higher)_

_PostgreSQL (14.x or higher)_

***Setting Up the Project***

**1. Clone the Repository**
Open a terminal and run:

git clone https://github.com/your-repo/Ventaura.git
cd Ventaura

**2. Set Up PostgreSQL Database**
Open the PostgreSQL Shell or GUI Tool (pgAdmin)
Create the required database and user by running the following SQL commands:

CREATE DATABASE ventaura;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ventaura TO postgres;

Verify Connection String
Ensure the database connection string in backend/appsettings.json is set as follows:

"ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=ventaura;Username=postgres;Password=password;"
}

**3. Run Database Migrations**
Navigate to the backend folder:

cd backend/ventaura_backend

Run the following command to apply the database schema: 

dotnet ef database update

This will create the necessary tables in your ventaura database.

**4. Start the Backend Server**
From the backend folder, start the backend server:

dotnet run

**5. Set Up and Start the Frontend**

Navigate to the frontend folder: cd ../frontend
Install the required dependencies: npm install
Start the React development server: npm start







