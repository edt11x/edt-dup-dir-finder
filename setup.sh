#!/bin/bash
# setup.sh - Creates a virtual environment and installs dependencies

VENV_DIR="venv"

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# Create venv
echo "Creating virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"

if [ $? -eq 0 ]; then
    echo "Virtual environment created successfully."
    
    # Activate and update pip
    source "$VENV_DIR/bin/activate"
    echo "Updating pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        echo "Installing requirements from requirements.txt..."
        pip install -r requirements.txt
    fi
    
    echo "--------------------------------------------------"
    echo "Setup complete. To start using the tool:"
    echo "1. Activate the environment:  source $VENV_DIR/bin/activate"
    echo "2. Run the tool:               python3 dup_dir_finder.py [path]"
    echo "--------------------------------------------------"
else
    echo "Error: Failed to create virtual environment."
    echo "You may need to install the venv package (e.g., sudo apt install python3-venv)"
    exit 1
fi
