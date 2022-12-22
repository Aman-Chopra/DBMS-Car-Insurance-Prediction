import streamlit as st
import psycopg2 as psycopg2
import pickle
import pandas as pd
from datetime import date

displayData = st.container()
predictPrem = st.container()

# establishing the connection
conn = psycopg2.connect(
    database="postgres", user='postgres', password='amanapple@A2', host='127.0.0.1', port='5432'
)
# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Executing an MYSQL function using the execute() method
cursor.execute("select version()")

# Commit your changes in the database
conn.commit()

# Closing the connection
#conn.close()

model = pickle.load(open('data/model.pkl', 'rb'))

def predictPremium(X_test, base):
    probabilities = model.predict_proba(X_test)
    diabetesProne = probabilities[0][1]
    return base * (1 + diabetesProne * 3)

def predict(data, base):
    x_neww = pd.DataFrame([data])
    price = predictPremium(x_neww, base)
    return price

with displayData:
    st.title("DBMS Project")
    st.header('Fetch data')
    st.text('In this section you can see the data!')
    table = st.selectbox ('Select the table', 
        options=['CUSTOMER', 'EMPLOYEES', 'PRODUCT'], 
        index=0)

    if st.button('Show'):
        query = 'select * from "{}" as a'.format(table)
        cursor.execute(query)

        df = pd.read_sql('select * from "{}" as a'.format(table), conn)
        
        # CSS to inject contained in a string
        hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        # Display a static table
        st.table(df)

with predictPrem:
    st.header('Predict Premium')
    st.text('In this section you can calculate your premium by entering normalised values!')

    education = 0.5
    Cust_Id = st.text_input('Customer Id', '1')
    product = st.selectbox ('Select the product', 
        options=['1', '2'], 
        index=0)
    cigsPerDay = st.slider('Cigarettes per day', min_value=0, max_value=20, value=1, step=1)
    BPMeds = st.number_input('BP Meds', min_value=0.00, max_value=1.00, value=0.23)
    prevalentStroke = st.number_input('Prevalent Stroke', min_value=-1.00, max_value=1.00, value=-0.12, step=0.01)
    totChol = st.number_input('Total Cholestrol', min_value=0.00, max_value=1.00, value=0.67, step=0.01)
    sysBP = st.number_input('Systolic BP', min_value=0.00, max_value=1.00, value=0.15, step=0.01)
    BMI = st.number_input('BMI', min_value=-1.00, max_value=1.00, value=-0.31, step=0.01)
    heartRate = st.number_input('Heart Rate', min_value=0.00, max_value=1.00, value=0.32, step=0.01)
    glucose = st.number_input('Glucose', min_value=0.00, max_value=1.00, value=0.32, step=0.01)

    if st.button('Get Premium'):           # when the submit button is pressed
        df = pd.read_sql('select * from "{}" where "{}" = {}'.format("CUSTOMER", "Cust_Id", Cust_Id), conn)
        gender = df.iloc[0]['Gender']
        dob = df.iloc[0]['DOB']
        if gender == 'M':
            male = 1
        else:
            male = 0
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        # Normalise the age
        age /= 100
        df = pd.read_sql('select * from "{}" where "{}" = {}'.format("PRODUCT", "Product_Id", product), conn)
        base = df.iloc[0]['Base']
        data = {
            'male': male,
            'age': age,
            'education': education,
            'cigsPerDay': cigsPerDay,
            'BPMeds': BPMeds,
            'prevalentStroke': prevalentStroke,
            'totChol': totChol,
            'sysBP': sysBP,
            'BMI': BMI,
            'heartRate': heartRate,
            'glucose': glucose
        }
        price = predict(data, base)
        st.success(f'Your insurance charges would be: ${price}')