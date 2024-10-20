import sqlite3
from flask import Flask,render_template ,jsonify, send_from_directory
from wsgiref import simple_server
from flask import request
from flask import Response
import os
from flask_cors import CORS, cross_origin
from prediction_Validation_Insertion import pred_validation
from trainingModel import trainModel
from training_Validation_Insertion import train_validation
import flask_monitoringdashboard as dashboard
from predictFromModel import prediction

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
dashboard.bind(app)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/home/')
def home():
    return render_template('index.html')





@app.route('/train/',methods = ["GET"])
def train():
    return render_template('train.html')

@app.route('/trained/',methods = ["POST","GET"])
@cross_origin()
def trainRouteClient():

    try:
        files = request.files.getlist('files')
        # Clear previously existing files in the batchfiles directory
        batchfiles_dir = 'Training_Batch_Files'
        if os.path.exists(batchfiles_dir):
            existing_files = os.listdir(batchfiles_dir)
            for file_name in existing_files:
                os.remove(os.path.join(batchfiles_dir, file_name))

        # Create the directory if it doesn't exist
        if not os.path.exists(batchfiles_dir):
            os.makedirs(batchfiles_dir)

        # Save the files to the batchfiles directory
        for file in files:
            file.save(os.path.join(batchfiles_dir, file.filename))        
            train_valObj = train_validation(batchfiles_dir) #object initialization
            train_valObj.train_validation()#calling the training_validation function
            trainModelObj = trainModel() #object initialization
            trainModelObj.trainingModel() #training the model for the files in the table

    except Exception as e:
        error_message = 'Error occurred: {}'.format(str(e))
        return Response(error_message, status=500, content_type='text/plain')

    return jsonify({'message': 'Model trained successfully'})

@app.route('/predict/',methods = ["POST","GET"])
def predict():
    return render_template('predict.html')

@app.route("/predicted/", methods=["POST", "GET"])
@cross_origin()
def predictRouteClient():
    try:
        # Check if files are part of the request
        if 'files' in request.files:
            files = request.files.getlist('files')
            # Create a directory to store the files
            directory = 'Prediction_Batch_Files'

            # Clear existing files in the directory
            if os.path.exists(directory):
                for file_name in os.listdir(directory):
                    os.remove(os.path.join(directory, file_name))
            else:
                os.makedirs(directory)  # Create directory if it doesn't exist
            
            # Save the uploaded files
            for file in files:
                file.save(os.path.join(directory, file.filename))  # Save each file

            # Perform prediction validation
            pred_val = pred_validation(directory)  # Object initialization
            pred_val.prediction_validation()  # Call the prediction validation function
            
            # Create a prediction object and get predictions
            pred = prediction(directory, None)  # Object initialization
            path = pred.predictionFromModel()  # Call prediction method
            
            # Check if the predictions CSV exists before sending
            prediction_file = 'Predictions.csv'
            prediction_output_dir = 'Prediction_Output_File'

            if os.path.exists(os.path.join(prediction_output_dir, prediction_file)):
                return send_from_directory(prediction_output_dir, prediction_file, as_attachment=True, mimetype='text/csv')
            else:
                return Response("Prediction file not found.", status=404)  # Return error if file doesn't exist

        # Handle website link prediction
        elif 'websiteLink' in request.form:
            weblink = request.form.get("websiteLink")
            pred = prediction(None, weblink)  # Object initialization
            result = pred.predictFromModelForWebsite()  # Get prediction result
            return result  # Return the result for the website link

        # If neither files nor website link is provided
        return Response("No files or website link provided.", status=400)  # Return error for missing input

    except ValueError as ve:
        return Response(f"Error Occurred! {str(ve)}", status=400)  # Return error for ValueError
    except KeyError as ke:
        return Response(f"Error Occurred! {str(ke)}", status=400)  # Return error for KeyError
    except Exception as e:
        return Response(f"Error Occurred! {str(e)}", status=500)  # Return general error








@app.route('/contact/', methods=["POST","GET"])
def contact():
    if request.method == 'POST':
        # Retrieve the form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Get the path to the database file
        db_folder = 'Contact_Database'  # Replace with your desired folder path
        db_file = os.path.join(db_folder, 'contacts.db')

        # Create the database folder if it doesn't exist
        os.makedirs(db_folder, exist_ok=True)

        # Create a connection to the database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Create the 'contacts' table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                message TEXT
            )
        ''')

        # Insert the form data into the 'contacts' table
        cursor.execute('''
            INSERT INTO contacts (name, email, message)
            VALUES (?, ?, ?)
        ''', (name, email, message))

        # Commit the changes and close the database connection
        conn.commit()
        conn.close()

        # Display a success message to the user
        return Response('success')

    # Render the contact form template for GET requests
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug = True)