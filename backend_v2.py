import base64
from io import BytesIO
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from matplotlib import pyplot as plt
import pandas as pd


app = FastAPI()

# To process and summarize the uploaded CSV file
@app.post("/csv-overview/")
async def csv_overview(file: UploadFile = File(...)):
    try:
        # I used pandas to load the uploaded CSV file into a DataFrame for easy analysis.
        df = pd.read_csv(file.file)

        # I calculated the number of rows and columns to give a quick overview of the data.
        num_rows, num_columns = df.shape

        # I used the `describe()` function to generate summary statistics for numeric columns, which is helpful for an initial data analysis.
        numeric_summary = df.describe().to_dict()

        # I extracted the column names and their data types to give more detailed information about the structure of the data.
        column_types = df.dtypes.apply(lambda x: x.name).to_dict()

        # I compiled the response data into a dictionary to return a structured overview of the dataset.
        response_data = {
            "num_rows": num_rows,
            "num_columns": num_columns,
            "numeric_summary": numeric_summary,
            "column_types": column_types,  
            "columns": df.columns.tolist()
        }

        return JSONResponse(content=response_data)
    
    except Exception as e:
        # I used a try-except block to catch any errors and return them as part of the response, ensuring robust error handling.
        return JSONResponse(content={"error": str(e)}, status_code=400)
    
# To analyze missing values in the uploaded CSV file
@app.post("/missing-values/")
async def missing_values(file: UploadFile = File(...)):
    try:
        # I used pandas to load the CSV into a DataFrame to analyze missing values.
        df = pd.read_csv(file.file)

        # I used `isnull().sum()` to get the count of missing values for each column, which helps identify which columns have missing data.
        missing_data = df.isnull().sum()

        # I selected only the columns that have missing values to focus on the relevant data.
        missing_columns = missing_data[missing_data > 0]

        # I converted the missing values count into a dictionary format to make it easier to process in the response.
        missing_values_count = missing_columns.to_dict()

        # I included the distribution of missing values to provide more insight into how missing data is spread across columns.
        response_data = {
            "missing_values_count": missing_values_count,
            "missing_data_distribution": missing_columns.to_dict()  # Include the distribution of missing values
        }

        return JSONResponse(content=response_data)
    
    except Exception as e:
        # I included error handling to catch and return any issues during the process.
        return JSONResponse(content={"error": str(e)}, status_code=400)


# To visualize data from the uploaded CSV file
@app.post("/visualize/")
async def visualize_data(file: UploadFile = File(...), 
                         categorical_column: str = "Manufacturer", 
                         numeric_column: str = "Sales_in_thousands", 
                         top_n: int = 10):
    # I used FastAPI's `await` function to read the file asynchronously, improving efficiency.
    contents = await file.read()
    df = pd.read_csv(BytesIO(contents))

    # I selected the top `top_n` categories in the specified categorical column to focus on the most significant data.
    top_categories = df[categorical_column].value_counts().head(top_n).index
    filtered_df = df[df[categorical_column].isin(top_categories)]

    # I created a bar chart visualization using matplotlib to represent the data in a clear and understandable way.
    plt.figure(figsize=(10, 6))
    filtered_df.groupby(categorical_column)[numeric_column].sum().sort_values(ascending=False).plot(kind='bar')
    plt.title(f"Top {top_n} Categories in {categorical_column}")
    plt.ylabel(numeric_column)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # I saved the chart to a byte stream, as FastAPI returns binary data when sending images in the response.
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    # I returned the image as a StreamingResponse, allowing the user to view the chart directly in the browser.
    return StreamingResponse(buffer, media_type="image/png")


DATABASE_FILE = "cleaned_data.db"

# To clean the data and handle missing values
@app.post("/clean-data/")
async def clean_data(
    file: UploadFile = File(...),
    missing_value_strategy: str = Form(...),  # Strategy for handling missing values ("drop", "fill", "fill with mode/median")
    fill_value: str = Form(None),             # Value to use if the strategy is "fill"
    categorical_fill_strategy: str = Form(None),  # Strategy for categorical fill ("Mode" or "Median")
):
    import pandas as pd
    from io import BytesIO
    import sqlite3
    import os

    try:
        # I loaded the CSV file into a pandas DataFrame to facilitate cleaning.
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))

        # I checked the missing value strategy and applied the corresponding method.
        if missing_value_strategy == "drop":
            # I used `dropna()` to remove rows with any missing values, as this strategy is commonly used when you can afford to lose data.
            df = df.dropna()
        elif missing_value_strategy == "fill":
            # I ensured that the user provides a value to fill the missing data, making the fill strategy functional.
            if fill_value is None:
                return JSONResponse(
                    content={"error": "Fill value is required for missing value strategy 'fill'."},
                    status_code=400,
                )
            df = df.fillna(fill_value)
        elif missing_value_strategy == "fill with mode/median":
            # I verified that the categorical fill strategy is selected to guide how the missing data should be handled (either by Mode or Median).
            if not categorical_fill_strategy:
                return JSONResponse(
                    content={"error": "Categorical fill strategy ('Mode' or 'Median') is required."},
                    status_code=400,
                )
            if categorical_fill_strategy == "Mode":
                # I filled missing categorical values with the mode (most frequent value) as this is a common strategy.
                for column in df.select_dtypes(include=['object', 'category']).columns:
                    df[column].fillna(df[column].mode()[0], inplace=True)
            elif categorical_fill_strategy == "Median":
                # I filled missing numeric values with the median, which is more robust against outliers than the mean.
                for column in df.select_dtypes(include=['number']).columns:
                    df[column].fillna(df[column].median(), inplace=True)
            else:
                
                return JSONResponse(
                    content={"error": "Invalid categorical fill strategy."},
                    status_code=400,
                )
        else:
            # I returned an error if the missing value strategy was invalid, ensuring only supported strategies are used.
            return JSONResponse(
                content={"error": "Invalid missing value strategy."},
                status_code=400,
            )
        
        # I saved the cleaned data to a SQLite database for later use.
        conn = sqlite3.connect(DATABASE_FILE)
        df.to_sql("cleaned_data", conn, if_exists="replace", index=False)
        conn.close()

        # I returned the cleaned data in SQLite format, allowing the user to download the result.
        return FileResponse(
            path=DATABASE_FILE,
            media_type="application/x-sqlite3",
            filename=DATABASE_FILE,
        )
    except Exception as e:
        # I included error handling to provide meaningful feedback in case of an issue during the data cleaning process.
        return JSONResponse(content={"error": str(e)}, status_code=500)
