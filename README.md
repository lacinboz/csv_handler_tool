# CSV Handler Tool

This application provides an intuitive interface for processing CSV files, allowing users to upload their files, handle missing values, and gain insights into their datasets. It uses **FastAPI** for the backend, **Streamlit** for the frontend, and stores processed data in an **SQLite** database. It includes a sidebar for easy navigation between different features.

## Features

### 1. **CSV Upload:**
- Users can upload their own CSV files for analysis through an easy-to-use file uploader.

### 2. **CSV Overview:**
- Displays the number of rows and columns.
- Provides summary statistics for numerical columns.
- Lists data types for each column.

### 3. **Missing Values Handling:**
- Analyze missing values, including their count and distribution.
- Visualize missing data using bar charts.
- Offers multiple strategies to handle missing data:
  - **Drop rows:** Remove rows containing missing values.
  - **Fill values:** Replace missing values with a user-defined input.
  - **Fill with median:** For numerical columns, replace missing values with the median of the column.
  - **Fill with mode:** For categorical columns, replace missing values with the mode (most frequent value) of the column.

### 4. **Data Visualization:**
- Create bar charts comparing categorical and numerical data.
- Users can:
  - Select the columns (categorical and numerical) to be used for visualization.
  - Specify the number of top categories to display based on their preferences.

### 5. **Data Cleaning:**
- Clean uploaded CSV files by applying the chosen missing-value strategy.
- Save the cleaned dataset to a SQLite database.
- Provide a downloadable SQLite database containing the processed data.

### 6. **Database Checking:**
- Can check the database for missing values using the `check_database.py` script to ensure that they were properly removed.

## How to Work

1. **Start the API (FastAPI Backend):**
   - Run the following command to start the backend API:
     ```bash
     uvicorn backend_v2:app --reload
     ```
   
2. **Start the Streamlit App:**
   - Run the Streamlit app by executing the following command:
     ```bash
     streamlit run frontend_v2.py
     ```

## What You Need

- **Python (version >= 3.7)**
- **Streamlit** for the frontend
- **FastAPI** for the backend
- **SQLite** for data storage
- **pandas**, **matplotlib**, and other necessary libraries for data handling and visualization

## Workflow:

### **Frontend:**
- The user uploads a CSV file, selects options like missing values handling or data visualization, and interacts with the app via **Streamlit**.

### **Backend:**
- The backend, built using **FastAPI**, processes the file (e.g., generating a summary, cleaning the data, or visualizing the data) and returns the results to the frontend.

### **Database:**
- After cleaning the data, the backend stores the cleaned version in an **SQLite** database, which the user can download and verify using Python scripts (check_database.py).
