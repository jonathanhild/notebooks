import math

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

DATA_URL = 'salary_survey_2021_responses.csv'


@st.cache
def load_data():
    """
    Load and pre-processing of Salary Survey 2021 raw data.

    Returns:
        data: Processed DataFrame
    """
    data = pd.read_csv(DATA_URL, thousands=r',')

    # rename some of the columns
    column_name_mapping = {
        'How old are you?': 'age',
        'Job title': 'job',
        'Additional context on job title': 'job_context',
        'Annual salary': 'salary',
        'Other monetary comp': 'other_comp',
        'Currency - other': 'other_currency',
        'Additional context on income': 'income_context',
        'Overall years of professional experience': 'total_exp',
        'Years of experience in field': 'field_exp',
        'Highest level of education completed': 'highest_ed'}

    data.rename(columns=column_name_mapping, inplace=True)
    data.rename(columns=str.lower, inplace=True)

    # convert all currencies to USD using apply
    currency_map = {
        'USD': 1.00,
        'GBP': 1.41,
        'CAD': 0.83,
        'EUR': 1.21,
        'AUD/NZD': 0.72,
        'CHF': 1.10,
        'ZAR': 0.071,
        'SEK': 0.12,
        'HKD': 0.13,
        'JPY': 0.0091,
        'Other': np.nan
    }

    data['salary_usd'] = data.apply(lambda x: currency_map[x['currency']] * x['salary'], axis=1)

    # format total_exp values to be sortable
    total_exp_map = {
        '1 year or less': '00 - 01 years',
        '2 - 4 years': '02 - 04 years',
        '5-7 years': '05 - 07 years',
        '8 - 10 years': '08 - 10 years',
        '11 - 20 years': '11 - 20 years',
        '21 - 30 years': '21 - 30 years',
        '31 - 40 years': '31 - 40 years',
        '41 years or more': '41 - more years'
    }

    data['total_exp'] = data['total_exp'].map(total_exp_map)

    # Create a boolean column for each race
    races = [
        'Asian or Asian American',
        'Black or African American',
        'Hispanic, Latino, or Spanish origin',
        'Middle Eastern or Northern African',
        'Native American or Alaska Native',
        'White',
        'Another option not listed here or prefer not to answer']

    for race in races:
        data[race] = data['race'].str.contains(race)

    return data


data = load_data()

st.markdown('# Salary Survey 2021 Responses')
st.markdown(
    'Source: [Ask a Manager Salary Survey 2021](https://www.askamanager.org/2021/04/how-much-money-do-you-make-4.html)')
st.markdown('## Set filters for salary data')

# Add
column1, column2, column3, column4 = st.beta_columns(4)

# Get unique lists for selectbox values
# display them horizontally in three columns
# use selected values to query salary information
industries = list(data.groupby('industry')['timestamp'].count().nlargest(25).sort_index().index)
experience = list(data['total_exp'].sort_values().unique())
age = list(data['age'].sort_values().unique())
gender = list(data['gender'].unique())

with column1:
    industry = st.selectbox(
        'Industry',
        industries
    )

with column2:
    experience = st.selectbox(
        'Experience',
        experience
    )

with column3:
    age = st.multiselect(
        'Age',
        age,
        default='18-24'
    )

# Added new select box for gender
with column4:
    gender = st.selectbox(
        'Gender',
        gender
    )

# calculate average salary based on selectbox values
salary_data = data.query("industry == @industry and total_exp == @experience and age == @age")
average_salary = salary_data['salary_usd'].mean()

c = alt.Chart(salary_data).mark_bar().encode(
    alt.X('salary_usd',
          bin=True),
    y='count()',
    tooltip=['count()'])

st.altair_chart(c, use_container_width=True)

st.markdown('## Average Salary Comparison')

if pd.isnull(average_salary):
    st.write('Not enough data available')
else:
    average_salary = math.floor(average_salary)
    text = f'The average salary for {age} year old \
    {industry} professionals with \
    {experience} of experience is ${average_salary}.'
    st.write(text)

column1, column2 = st.beta_columns(2)

with column1:
    value1 = st.selectbox(
        'Row',
        ['Gender', 'Age', 'Experience', 'Education']
    )

with column2:
    value2 = st.selectbox(
        'Column',
        ['Age', 'Gender', 'Experience', 'Education']
    )

value_map = {
    'Gender': 'gender',
    'Age': 'age',
    'Experience': 'total_exp',
    'Education': 'highest_ed'
}

value1 = value_map[value1]
value2 = value_map[value2]

comparison_data = pd.crosstab(salary_data[value1], salary_data[value2], values=data['salary_usd'], aggfunc='mean')
if value1 != value2:
    st.dataframe(comparison_data.style.highlight_max(axis=0))
else:
    st.write('Please pick different values for comparison')
