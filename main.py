from app import create_app  # Import the function to create the app instance
import os  # Import os to handle environment variables

# This allows for the app to be run in different environments (development/production)
app = create_app()  # Initialize the app using the create_app function

if __name__ == "__main__":
    # Set the port dynamically, defaulting to 5000 if the environment variable is not set
    port = int(os.environ.get("PORT", 5000))
    # Running the Flask application with debug mode enabled
    app.run(host="0.0.0.0", port=port, debug=True)
