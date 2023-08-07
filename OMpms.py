import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
import sqlite3

#Logo ---
logo_image = "logo.png"
logo_width = 100  
st.image(logo_image, width=logo_width)

#sidebar ----
st.sidebar.markdown("## Navigation")
selected_tab = st.sidebar.radio("", ["Home","Admin","Contact US"])

# Title ----
st.title("Owner's Manual")
st.text("Periodic Maintenance table")

# DB connect --- 

# DB connect ---  SQLite database file
db_file_path = 'pms2.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_file_path)

# Create a cursor object
cursor = conn.cursor()


def reset_index_from_1(df):
    df_reset = df.reset_index(drop=True)
    df_reset.index = df_reset.index + 1
    return df_reset

# Define empty containers for each button's result table

replace_result_container = st.empty()
clean_result_container = st.empty()
other_result_container = st.empty()

# line 1 Select boxex
make, model, fuel = st.columns(3)

# Make select box --- line 1
cursor.execute("SELECT MAKE from TableMRU_1;")
rows = cursor.fetchall()
# make_list = sorted(list(set(row.MAKE for row in rows)))
make_list = list(set(row[0] for row in rows))
selected_make = make.selectbox("Make",[""] + make_list)
print("rows printed",rows)

# Model select box --- Line 1
if selected_make:
    cursor.execute(
        f"SELECT model FROM TableMRU_1 WHERE make LIKE '{selected_make}';"
    )
    rows = cursor.fetchall()
    model_list = sorted(list(set(row[0] for row in rows)))
    print("rows printed make ",rows)
else:
    model_list = []
selected_model = model.selectbox("Model", [""] + model_list)

# Fuel - Line 1
if selected_make and selected_model:
    cursor.execute(
        f"SELECT FUEL FROM TableMRU_1 WHERE make LIKE '{selected_make}' AND model LIKE '{selected_model}';")
    rows = cursor.fetchall()
    fuel_list = sorted(list(set(row[0] for row in rows)))
    print(rows,"rows of fuel")
    print(fuel_list,"fuel list")
else:
    fuel_list = []
selected_fuel = fuel.selectbox("Fuel", [""] + fuel_list)

# Select Box Mileage - Line 2
m1,m2  = st.columns(2)
mileage_months = ["1K / 1 month", "5K / 6 months", "10K / 12 months", "20K / 24 months", "30K / 36 months", "40K / 48 months",   
                  "50K / 60 months", "60K / 72 months", "70K / 84 months", "80K / 96 months", "90K / 108 months", "100K / 120 months",    
                  "10K / 132 months", "120K / 144 months", "130K / 156 months", "140K / 168 months", "150K / 180 months", "160K / 192 months",    
                  "170K / 204 months"]

selected_mileage = m1.selectbox("Mileage X 1000km / Months - Which ever comes First", [""] + mileage_months)
column_name = selected_mileage.split("/")[0].strip().replace(" ", "")
column_index = None

#Main group:---------------


main_list = []
if selected_make and selected_model and selected_fuel:
    cursor.execute(
        f"SELECT Main FROM TableMRU_1 WHERE make LIKE '{selected_make}' AND model LIKE '{selected_model}' AND FUEL LIKE '{selected_fuel}';"
    )
    rows = cursor.fetchall()
    #main_list = sorted(list(pd.unique(row.Main for row in rows)))
    main_list = sorted(list(set(row[0] for row in rows)))
    print("main list ->", main_list) 



    
else:
    # main_list = []
    rows = cursor.fetchall()
    main_list = list(set(main_list))

selected_main = m2.selectbox(" * Category --> Optional ", ["All"] + main_list)
   

    
      


#------------- End Main group

st.write("Selected Make     :",  selected_make)
st.write("Selected Model    :",  selected_model)
st.write("Selected Fuel     :",  selected_fuel)
st.write("Selected Mileage  :",  selected_mileage)
st.write("Selected category :",  selected_main)

# Define empty containers for each button's result table

col1, col2, col3, col4 = st.columns(4)

#inspect_button = col1.button("Inspect")

# "Replace" button
#replace_button = col2.button("Replace")

# "Clean" button
#clean_button = col3.button("Clean")

# "Others" button
#all_button = col4.button("All")

   # Display the result and clear other containers



inspect  = col1.button("Inspect")

Replace = col2.button("Replace")

Clean = col3.button("Clean")

others = col4.button("Others")
#--------------------------------------------------------------------------------------------Others


if others:
    
    selected_make = selected_make if selected_make != "" else None
    selected_model = selected_model if selected_model != "" else None
    selected_fuel = selected_fuel if selected_fuel != "" else None

    # Build the SQL query based on the selected values
    query = "SELECT * FROM TableMRU_1 WHERE 1=1"
    if selected_make is not None:
        query += f" AND MAKE LIKE '{selected_make}'"
    if selected_model is not None:
        query += f" AND MODEL LIKE '{selected_model}'"
    if selected_fuel is not None:
        query += f" AND FUEL LIKE '{selected_fuel}'"

   
    # Execute the query and fetch the results
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    if rows:
        num_columns = len(cursor.description)
        column_names = [column[0] for column in cursor.description]

        # Create a DataFrame with the fetched rows and column names
        df = pd.DataFrame(columns=column_names[:num_columns])
        for row in rows:
            df = df.append(dict(zip(column_names[:num_columns], row)), ignore_index=True)

        if column_name in df.columns:
            column_index = df.columns.get_loc(column_name)  # Get the index of the column_name
        else:
            st.write("No data available for the selected mileage")


    # Filter Main, Sub, and selected mileage
    filtered_df_all = None
    data_fetched = False  # Initialize data_fetched as False
    # Filter Main, Sub, and selected mileage
    if column_index is not None:

        filtered_rows = [(row[2], row[3], row[column_index], row[23]) for row in rows]
        filtered_df_all = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
        #filtered_df_all = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
        filtered_df_all = filtered_df_all[~filtered_df_all[column_name].isin(["Replace", "Inspect", "Clean",column_name])]

        # Filter out rows with "No Change" in the Note column
        filtered_df_all = filtered_df_all[~filtered_df_all['Note'].str.contains('No Change', case=False)]

    #filtered_df = filtered_df[filtered_df[column_name] == "Inspect"]
    if selected_main == "All":
        filtered_temp = filtered_df_all
    else:
        filtered_temp = filtered_df_all[filtered_df_all['Main'] == selected_main]

    # Colors to df
    def color_cell(val, col):
        if col == 'Note' and isinstance(val, str) and len(val) > 10 :
            return 'background-color: skyblue'
        elif col == filtered_temp.columns[2]:
            if val == 'Replace':
                return 'background-color: red'
            elif val == 'Inspect':
                return 'background-color: yellow'
            elif val == 'Clean':
                return 'background-color: Green'
        return ''
    main_value = filtered_temp["Main"].unique()
    lis_of_values = [reset_index_from_1(filtered_temp[filtered_temp["Main"]==mvalue]) for mvalue in main_value]
    for mvalue,dfvalue in zip(main_value,lis_of_values):
        with st.expander(mvalue):
            st.table(dfvalue)
    styled_df = filtered_temp.style.applymap(lambda x: color_cell(x, filtered_temp.columns[3]), subset=pd.IndexSlice[:, ['Note']])
    styled_df = styled_df.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, [filtered_temp.columns[2]]])
    # st.table(styled_df)
    
    # other_result_container.table(styled_df)
    # Set custom styles
    


#------------------------------------------------------------------------------------------inspect-----
elif inspect:
    
    selected_make = selected_make if selected_make != "" else None
    selected_model = selected_model if selected_model != "" else None
    selected_fuel = selected_fuel if selected_fuel != "" else None

    # Build the SQL query based on the selected values
    query = "SELECT * FROM TableMRU_1 WHERE 1=1"
    if selected_make is not None:
        query += f" AND MAKE LIKE '{selected_make}'"
    if selected_model is not None:
        query += f" AND MODEL LIKE '{selected_model}'"
    if selected_fuel is not None:
        query += f" AND FUEL LIKE '{selected_fuel}'"

   
    # Execute the query and fetch the results
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    if rows:
        num_columns = len(cursor.description)
        column_names = [column[0] for column in cursor.description]

        # Create a DataFrame with the fetched rows and column names
        df = pd.DataFrame(columns=column_names[:num_columns])
        for row in rows:
            df = df.append(dict(zip(column_names[:num_columns], row)), ignore_index=True)

        if column_name in df.columns:
            column_index = df.columns.get_loc(column_name)  # Get the index of the column_name
        else:
            st.write("No data available for the selected mileage")

# Filter Main, Sub, and selected mileage
    filtered_df = None
    data_fetched = False  # Initialize data_fetched as False
    # Filter Main, Sub, and selected mileage
    if column_index is not None:
        filtered_rows = [(row[2], row[3], row[column_index], row[23]) for row in rows]
        filtered_df_in = pd.DataFrame(filtered_rows, columns=['Main', 'Sub',column_name, 'Note'])
        filtered_df_in = filtered_df_in[filtered_df_in[column_name] == "Inspect"]
        if selected_main == "All":
            filtered_temp_in = filtered_df_in
        else:
            filtered_temp_in = filtered_df_in[filtered_df_in['Main'] == selected_main]
        print(filtered_df_in)
        # Colors to df
        def color_cell(val, col):
            if col == 'Note' and isinstance(val, str) and len(val) > 4:
                return 'background-color: skyblue'
            elif col == filtered_temp_in.columns[2]:
                if val == 'Replace':
                    return 'background-color: red'
                elif val == 'Inspect':
                    return 'background-color: yellow'
              
            return ''
        main_value = filtered_temp_in["Main"].unique()
        filtered_temp_in.fillna(" ")
        lis_of_values = [reset_index_from_1(filtered_temp_in[filtered_temp_in["Main"]==mvalue][["Main","Sub",column_name]]) for mvalue in main_value]
        for mvalue,dfvalue in zip(main_value,lis_of_values):
            with st.expander(mvalue,expanded=False):
                st.table(dfvalue)
        filtered_temp_in = filtered_temp_in.drop_duplicates()
        styled_df_in = filtered_temp_in.style.applymap(lambda x: color_cell(x, filtered_temp_in.columns[3]), subset=pd.IndexSlice[:, ['Note']])
        styled_df_in = styled_df_in.applymap(lambda x: color_cell(x, filtered_temp_in.columns[2]), subset=pd.IndexSlice[:, [filtered_temp_in.columns[2]]])
        
        # st.table(styled_df_in) 
        # inspect_result_container = st.empty() 
        # inspect_result_container.table(styled_df_in)   

    #------------------------------------------------------------------------------------------------ replace 
elif Replace:
    
    selected_make = selected_make if selected_make != "" else None
    selected_model = selected_model if selected_model != "" else None
    selected_fuel = selected_fuel if selected_fuel != "" else None

    # Build the SQL query based on the selected values
    query = "SELECT * FROM TableMRU_1 WHERE 1=1"
    if selected_make is not None:
        query += f" AND MAKE LIKE '{selected_make}'"
    if selected_model is not None:
        query += f" AND MODEL LIKE '{selected_model}'"
    if selected_fuel is not None:
        query += f" AND FUEL LIKE '{selected_fuel}'"

   
    # Execute the query and fetch the results
    cursor.execute(query)
    rows = cursor.fetchall()

    # Display the results
    if rows:
        num_columns = len(cursor.description)
        column_names = [column[0] for column in cursor.description]

        # Create a DataFrame with the fetched rows and column names
        df = pd.DataFrame(columns=column_names[:num_columns])
        for row in rows:
            df = df.append(dict(zip(column_names[:num_columns], row)), ignore_index=True)

        if column_name in df.columns:
            column_index = df.columns.get_loc(column_name)  # Get the index of the column_name
        else:
            st.write("No data available for the selected mileage")

    # Filter Main, Sub, and selected mileage
    filtered_df = None
    data_fetched = False  # Initialize data_fetched as False
    # Filter Main, Sub, and selected mileage
    if column_index is not None:
        filtered_rows = [(row[2], row[3], row[column_index], row[23]) for row in rows]
        filtered_df = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
        filtered_df = filtered_df[filtered_df[column_name] == "Replace"]
        if selected_main == "All":
            filtered_temp = filtered_df
        else:
            filtered_temp = filtered_df[filtered_df['Main'] == selected_main]

        # Colors to df
        def color_cell(val, col):
            if col == 'Note' and isinstance(val, str) and len(val) > 4:
                return 'background-color: skyblue'
            elif col == filtered_temp.columns[2]:
                if val == 'Replace':
                    return 'background-color: red'
                elif val == 'Inspect':
                    return 'background-color: yellow'
            return ''
        main_value = filtered_temp["Main"].unique()
        lis_of_values = [reset_index_from_1(filtered_temp[filtered_temp["Main"]==mvalue][["Main","Sub",column_name]]) for mvalue in main_value]
        for mvalue,dfvalue in zip(main_value,lis_of_values):
            with st.expander(mvalue,expanded=False):
                st.table(dfvalue)
        styled_df_replace = filtered_temp.style.applymap(lambda x: color_cell(x, filtered_temp.columns[3]), subset=pd.IndexSlice[:, ['Note']])
        styled_df_replace= styled_df_replace.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, [filtered_temp.columns[2]]])
        # st.table(styled_df_replace)

#-------------------------------------Clean
elif Clean:  
    selected_make = selected_make if selected_make != "" else None
    selected_model = selected_model if selected_model != "" else None
    selected_fuel = selected_fuel if selected_fuel != "" else None

    # Build the SQL query based on the selected values
    query = "SELECT * FROM TableMRU_1 WHERE 1=1"
    if selected_make is not None:
        query += f" AND MAKE LIKE '{selected_make}'"
    if selected_model is not None:
        query += f" AND MODEL LIKE '{selected_model}'"
    if selected_fuel is not None:
        query += f" AND FUEL LIKE '{selected_fuel}'"

   
        # Execute the query and fetch the results
        cursor.execute(query)
        rows = cursor.fetchall()

    # Display the results
    if rows:
        num_columns = len(cursor.description)
        column_names = [column[0] for column in cursor.description]

        # Create a DataFrame with the fetched rows and column names
        df = pd.DataFrame(columns=column_names[:num_columns])
        for row in rows:
            df = df.append(dict(zip(column_names[:num_columns], row)), ignore_index=True)

        if column_name in df.columns:
            column_index = df.columns.get_loc(column_name)  # Get the index of the column_name
        else:
            st.write("No data available for the selected mileage")
    # Filter Main, Sub, and selected mileage
    filtered_df = None
    data_fetched = False  # Initialize data_fetched as False
    # Filter Main, Sub, and selected mileage
    if column_index is not None:
        filtered_rows = [(row[2], row[3], row[column_index], row[23]) for row in rows]
        filtered_df = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
        filtered_df = filtered_df[filtered_df[column_name] == "Clean"]
        if selected_main == "All":
            filtered_temp = filtered_df
        else:
            filtered_temp = filtered_df[filtered_df['Main'] == selected_main]

        # Colors to df
        def color_cell(val, col):
            if col == 'Note' and isinstance(val, str) and len(val) > 4:
                return 'background-color: skyblue'
            elif col == filtered_temp.columns[2]:
                if val == 'Clean':
                    return 'background-color: Green '
                elif val == 'Inspect':
                    return 'background-color: yellow'
            return ''
        styled_df_clean = filtered_temp.style.applymap(lambda x: color_cell(x, filtered_temp.columns[3]), subset=pd.IndexSlice[:, ['Note']])
        styled_df_clean = styled_df_clean.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, [filtered_temp.columns[2]]])
        
        main_value = filtered_temp["Main"].unique()
        lis_of_values = [reset_index_from_1(filtered_temp[filtered_temp["Main"]==mvalue][["Main","Sub",column_name]]) for mvalue in main_value]
        for mvalue,dfvalue in zip(main_value,lis_of_values):
            with st.expander(mvalue):
                st.table(dfvalue)


elif selected_mileage:  
    all_result_container = st.empty()
# if not  col3.button("Clean",key="2"):
    selected_make = selected_make if selected_make != "" else None
    selected_model = selected_model if selected_model != "" else None
    selected_fuel = selected_fuel if selected_fuel != "" else None

        # Build the SQL query based on the selected values
    query = "SELECT * FROM TableMRU_1 WHERE 1=1"
    if selected_make is not None:
        query += f" AND MAKE LIKE '{selected_make}'"
        if selected_model is not None:
            query += f" AND MODEL LIKE '{selected_model}'"
        if selected_fuel is not None:
            query += f" AND FUEL LIKE '{selected_fuel}'"

        # Execute the query and fetch the results
        cursor.execute(query)
        rows = cursor.fetchall()

        # Display the results
        if rows:
            num_columns = len(cursor.description)
            column_names = [column[0] for column in cursor.description]

            #  creatin a DataFrame with the fetched rows and column names
            df = pd.DataFrame(columns=column_names[:num_columns])
            for row in rows:
                df = df.append(dict(zip(column_names[:num_columns], row)), ignore_index=True)
            print("dfvalue",df.columns)
            print("col name",column_names)
            if column_name in df.columns:
                column_index = df.columns.get_loc(column_name)  # Get the index of the column_name
                print("rows value",column_index)
            else:

                st.write("No data available for the selected mileage")

        # Filter Main, Sub, and selected mileage
        filtered_df_all = None
        data_fetched = False  # Initialize data_fetched as False
        # Filter Main, Sub, and selected mileage
        if column_index is not None:
            print("Rows Value", rows)
            print("Filered row_df_all",filtered_df_all)

            
            filtered_rows = [(row[2], row[3], row[column_index], row[23]) for row in rows]
            filtered_df_all = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
            #filtered_df_all = pd.DataFrame(filtered_rows, columns=['Main', 'Sub', column_name, 'Note'])
            filtered_df_all = filtered_df_all[filtered_df_all[column_name].isin(["Replace", "Inspect", "Clean"])]
        #filtered_df = filtered_df[filtered_df[column_name] == "Inspect"]
            print("Filered row",filtered_rows)
            print("Filered row_df_all",filtered_df_all)
        if selected_main == "All":
            filtered_temp = filtered_df_all
            print("filter alll values",filtered_temp)
        else:
            filtered_temp = filtered_df_all[filtered_df_all['Main'] == selected_main]
            filtered_temp = filtered_temp.drop(columns=['Note'])
        # Colors to df
        def color_cell(val, col):
            if col == filtered_temp.columns[2]:
                if val == 'Replace':
                    return 'background-color: red'
                elif val == 'Inspect':
                    return 'background-color: yellow'
                elif val == 'Clean':
                    return 'background-color: Green'
                elif col == 'Note' and isinstance(val, str) and len(val) > 9:
                    return 'background-color: skyblue'
   
        
        styled_df = filtered_temp.style.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, ['Note']])
        styled_df = styled_df.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, [filtered_temp.columns[2]]])
        # styled_df = styled_df.data.drop(columns=['Note'])

        styled_df = filtered_temp.style.applymap(lambda x: color_cell(x, filtered_temp.columns[2]), subset=pd.IndexSlice[:, [filtered_temp.columns[2]]])
        st.table(styled_df)
   
else:
    st.warning("Please select the mileage from the dropdown.")


