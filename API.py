# importing Flask and other modules
from flask import Flask, request, render_template
import pandas as pd
import pickle

import requests
import pandas as pd
import base64


#Load the model
with open('Model.pkl','rb') as f:
    Model = pickle.load(f)


# Flask constructor
app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
        customer_id = request.form.get("fcustomerid")
        customer_name = request.form.get("fcustomername")
        customer_age = request.form.get("fcustomerage")
        customer_sub_plan = request.form.get("fcustomerplan")
        customer_bill = request.form.get("fcustomerbill")
        customer_usage = request.form.get("fcustomerusage")
        customer_gender = request.form.get("fcustomergender")
        customer_location = request.form.get("fcustomerlocation")

        l1 = ['CustomerID', 'Name', 'Age', 'Gender', 'Location','Subscription_Length_Months', 'Monthly_Bill', 'Total_Usage_GB']
        l2 = [customer_id,customer_name,customer_age,customer_gender.title(),customer_location.title(),customer_sub_plan, customer_bill,customer_usage]

        i = dict(zip(l1,l2))
        
        Test_data = pd.DataFrame()
        Test_data = Test_data.append(i,ignore_index=True)

        Data_A = pd.read_csv("https://raw.githubusercontent.com/Sharathkumar0/SUNBASE/main/Data_A.csv")
        

        Encoding_Gender = {'Female': 0.4966372126491822, 'Male': 0.5009816139202232}
        Encoding_Location = {'Chicago': 0.5023632271000893,'Houston': 0.4932437180240546,'Los Angeles': 0.4880537354475553,
                             'Miami': 0.5057768054012094,'New York': 0.5049853126124199}


        Test_data.drop(['CustomerID','Name'],axis=1,inplace=True)

        Categorical_Features = Test_data.columns[Test_data.dtypes == "object"]
        for variable in Categorical_Features:
            if variable == 'Gender':
                Test_data.loc[Test_data.index,'Gender'] = Test_data['Gender'].map(Encoding_Gender)
            elif variable == 'Location':
                Test_data.loc[Test_data.index,'Location'] = Test_data['Location'].map(Encoding_Location)
        
        Test_data.rename(columns={'Gender':'KFold_Target_Encoding_Gender','Location':'KFold_Target_Encoding_Location'},inplace=True)

        Test_data = Test_data.loc[:,['Age','Subscription_Length_Months','Monthly_Bill',
                             'Total_Usage_GB','KFold_Target_Encoding_Gender','KFold_Target_Encoding_Location']]
        
        #Predictions
        ypredictions = Model.predict(Test_data)
        
        if ypredictions[0] == 1:
            res = "Customer is going to stop the subscription plan"
        else:
            res = "Customer is enjoying the subscription plan and going to continue"
        

        # Define your GitHub repository information
        github_username = "Sharathkumar0"
        github_repo = "SUNBASE"
        github_token = "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"

        # Set the file information
        file_path = "Data_A.csv"

        # Check if the file already exists in the repository
        api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{file_path}"
        headers = {"Authorization": f"token {github_token}"}

        response = requests.get(api_url, headers=headers)

        # Check if the file exists
        if response.status_code == 200:
            # The file exists; let's update it
            # Get the current content of the file
            current_file = response.json()
            current_sha = current_file['sha']

            # Create or update the content of the CSV file
            last_index = Data_A.tail(1).index[0]
            Data_A.loc[last_index,'Churn'] = Model.predict(Test_data)[0]
    
            # Convert the DataFrame to a CSV string
            csv_content = Data_A.to_csv(index=False)

            # Base64 encode the CSV content
            content_bytes = csv_content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')

            # Create the request payload
            payload = {"message": "Update CSV file via API","content": content_base64,"sha": current_sha}

            # Make the PUT request to update the file
            update_response = requests.put(api_url, headers=headers, json=payload)

            if update_response.status_code == 200:
                print("CSV file updated successfully")
            else:
                print(f"Error updating the file: {update_response.status_code}\n{update_response.text}")

        elif response.status_code == 404:
            
            # Create or update the content of the CSV file
            last_index = Data_A.tail(1).index[0]
            Data_A.loc[last_index,'Churn'] = Model.predict(Test_data)[0]

            # Base64 encode the CSV content
            content_bytes = Data_A.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')

            # Create the request payload
            payload = {"message": "Create CSV file via API","content": content_base64}

            # Make the PUT request to create the file
            create_response = requests.put(api_url, headers=headers, json=payload)

            if create_response.status_code == 201:
                print("CSV file created successfully")
            else:
                print(f"Error creating the file: {create_response.status_code}\n{create_response.text}")
        else:
            print(f"Error: {response.status_code}\n{response.text}")

    return render_template('index.html',result=res)

if __name__ == "__main__":
     app.run(debug=True)
