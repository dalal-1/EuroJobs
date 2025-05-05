from app import create_app  # Import the function to create the app instance

# This allows for the app to be run in different environments (development/production)
app = create_app()  # Initialize the app using the create_app function

if __name__ == "__main__":
    # Running the Flask application
    app.run(host="0.0.0.0", port=5000, debug=True)
