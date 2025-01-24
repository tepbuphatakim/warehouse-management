#!/bin/bash

# Step 1: Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Step 3: Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

# Step 4: Run your Python script
echo "Running the project..."
python3 your_script.py
if [ $? -ne 0 ]; then
    echo "Failed to run the script."
    exit 1
fi

echo "Setup and execution completed successfully!"
