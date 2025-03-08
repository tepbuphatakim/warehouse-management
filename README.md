# Warehouse Management System

A simple warehouse management system for managing inventory, sales, and returns.

## Getting Started

1. Install dependencies

For Window double click on the setup.bat file to execute and install dependencies or execute command.

```bash
start setup.bat
```

For MacOS / Linux from the root of project.

```bash
./setup.sh
```

2. Start the application:

Activate virtual environment.

For Window:

```bash
venv\Scripts\activate
```

For MacOS / Linux:

```bash
source venv/bin/activate
```

In the virtual environment:

```bash
python main.py
```

3. Seed the database with initial data, this will reset data in warehouse.db to initial state base on seed.py data:

```bash
cd database
python seed.py
```

## Features

- Inventory Management
- Sales Processing
- Returns Handling 
- Business Analytics Dashboard
