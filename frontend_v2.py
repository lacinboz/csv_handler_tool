import streamlit as st
import pandas as pd
import requests
from io import StringIO
import matplotlib.pyplot as plt

# API endpoints for different functionalities
# I included these API URLs because they allow communication with the backend for CSV file processing and analytics.
API_URL_OVERVIEW = "http://127.0.0.1:8000/csv-overview/"
API_URL_MISSING = "http://127.0.0.1:8000/missing-values/"
API_URL_VISUALIZE = "http://127.0.0.1:8000/data-visualization/"

# Setting the page title and layout
# I customized the page to make it user-friendly with a descriptive title and responsive layout.
st.set_page_config(page_title="CSV File Overview", layout="wide")

# Styling the main header
# I used custom HTML and CSS to enhance the appearance of the app's title and make it more visually appealing.
st.markdown("<h1 style='color:#2C6B2F;'>CSV File Overview</h1>", unsafe_allow_html=True)

# Customizing sidebar appearance
# I styled the sidebar to ensure consistency with the main theme and improve the overall user experience.
st.markdown(
    """
    <style>
    .css-1d391kg {
        background-color: #1abc9c;
        color: white;
    }
    body {
        background-color: #e8f7f1;
    }
    .stButton>button {
        background-color: #1abc9c;
        color: white;
        font-size: 16px;
        height: 40px;
        width: 150px;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar menu options
# I added these options to let users easily navigate between different features of the app.
st.sidebar.title("Option Menu")
sidebar_option = st.sidebar.radio("Select an option:", ("Home and Overview", "Missing Values", "Data Visualization", "Clean Data"))

# Section 1: Home and Overview
if sidebar_option == "Home and Overview":
    st.title("Home and Overview")

    # File upload functionality
    # I added a file uploader to let users upload their own CSV files for analysis.
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Sending the uploaded file to the backend for processing
            # I used the POST method to send the file and retrieve an overview of the data.
            with st.spinner("Uploading file and retrieving overview..."):
                response = requests.post(API_URL_OVERVIEW, files={"file": uploaded_file.getvalue()})
            
            if response.status_code == 200:
                # Parsing the backend response to display data insights
                overview_data = response.json()

                # Displaying general information about the dataset
                st.subheader("Overview")
                st.write(f"Number of Rows: {overview_data['num_rows']}")
                st.write(f"Number of Columns: {overview_data['num_columns']}")

                # Showing summary statistics for numerical columns
                st.subheader("Summary of Numerical Columns")
                numeric_summary = pd.DataFrame(overview_data["numeric_summary"])
                st.dataframe(numeric_summary)

                # Displaying column data types
                st.subheader("Column Data Types")
                column_types = pd.DataFrame(list(overview_data["column_types"].items()), columns=["Column", "Data Type"])
                st.dataframe(column_types)

            else:
                # Error handling for unsuccessful requests
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            # General error handling for unexpected issues
            st.error(f"An error occurred: {e}")
    else:
        # Prompting the user to upload a file if none is uploaded
        st.info("Please upload a CSV file to start.")

# Section 2: Missing Values Analysis
elif sidebar_option == "Missing Values":
    st.title("Missing Values Analysis")

    # File upload functionality
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            # Sending the file to the backend for missing values analysis
            with st.spinner("Uploading file and retrieving missing values information..."):
                response = requests.post(API_URL_MISSING, files={"file": uploaded_file.getvalue()})

            if response.status_code == 200:
                # Processing the backend response for missing data insights
                missing_data = response.json()

                # Displaying the count of missing values
                st.subheader("Missing Values Count")
                missing_values_count = missing_data["missing_values_count"]
                st.write(missing_values_count)

                # Visualizing missing values distribution
                st.subheader("Missing Values Distribution")
                missing_data_distribution = missing_data["missing_data_distribution"]

                # Creating a bar chart to represent missing values
                missing_columns = list(missing_data_distribution.keys())
                missing_counts = list(missing_data_distribution.values())

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.bar(missing_columns, missing_counts, color='salmon')
                ax.set_xlabel('Columns')
                ax.set_ylabel('Number of Missing Values')
                ax.set_title('Missing Values Distribution')
                plt.xticks(rotation=45, ha='right')
                st.pyplot(fig)

            else:
                # Handling errors from the backend
                st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            # General error handling
            st.error(f"An error occurred: {e}")
    else:
        # Prompt for file upload
        st.info("Please upload a CSV file to start.")

# Section 3: Data Visualization
elif sidebar_option == "Data Visualization":
    st.title("Visualization")

    # File upload functionality
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        # Reading the uploaded file and displaying the first few rows
        df = pd.read_csv(uploaded_file)
        st.write("Uploaded Data:")
        st.dataframe(df.head())

        # Dropdown menus for selecting columns
        categorical_column = st.selectbox("Select a categorical column:", df.select_dtypes(include=["object", "category"]).columns)
        numeric_column = st.selectbox("Select a numerical column:", df.select_dtypes(include=["int", "float"]).columns)

        # Slider for selecting the number of top categories
        top_n = st.slider("Number of top categories to display:", min_value=5, max_value=30, value=10)

        if st.button("Visualize"):
            # Filtering the top N categories and creating a bar chart
            top_categories = df[categorical_column].value_counts().head(top_n).index
            filtered_df = df[df[categorical_column].isin(top_categories)]

            fig, ax = plt.subplots(figsize=(10, 6))
            filtered_df.groupby(categorical_column)[numeric_column].sum().sort_values(ascending=False).plot(kind="bar", ax=ax)
            ax.set_title(f"Top {top_n} {categorical_column} by {numeric_column}")
            ax.set_ylabel(numeric_column)
            ax.set_xlabel(categorical_column)
            plt.xticks(rotation=45)

            # Displaying the chart
            st.pyplot(fig)

# Section 4: Data Cleaning
elif sidebar_option == "Clean Data":
    st.title("Clean Data")

    # File upload and missing value handling strategy
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    missing_value_strategy = st.selectbox(
        "Select a strategy for handling missing values:",
        ["drop", "fill", "fill with mode/median"]
    )

    # Allowing the user to input a fill value
    fill_value = None
    categorical_fill_strategy = None  # Variable to store categorical strategy

    if missing_value_strategy == "fill":
        fill_value = st.text_input("Enter a value to fill missing data:")
    elif missing_value_strategy == "fill with mode/median":
        categorical_fill_strategy = st.selectbox(
            "Select strategy for categorical variables:",
            ["Mode", "Median"]
        )
        fill_value = None  # Disable fill_value input for this strategy

    # Triggering the cleaning process
    if st.button("Clean Data"):
        if uploaded_file:
            # Sending the file and cleaning parameters to the backend
            response = requests.post(
                "http://127.0.0.1:8000/clean-data/",
                files={"file": uploaded_file.getvalue()},
                data={
                    "missing_value_strategy": missing_value_strategy,
                    "fill_value": fill_value,
                    "categorical_fill_strategy": categorical_fill_strategy,  # Send the categorical strategy
                },
            )
            if response.status_code == 200:
                # Allowing the user to download the cleaned data as an SQLite database
                with open("cleaned_data.db", "wb") as f:
                    f.write(response.content)
                st.success("Data cleaned and saved to SQLite database.")
                st.download_button(
                    "Download SQLite Database",
                    data=response.content,
                    file_name="cleaned_data.db",
                    mime="application/x-sqlite3",
                )
            else:
                # Handling errors during the cleaning process
                st.error(response.json().get("error", "An error occurred."))
        else:
            # Prompting the user to upload a file if none is provided
            st.error("Please upload a CSV file.")
