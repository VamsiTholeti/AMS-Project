#Importing all necessary dependencies.........
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Set page configuration
st.set_page_config(
    page_title="AMS Dashboard",
    page_icon=":bar_chart:",
    layout="wide",  # 'wide' or 'centered'
    initial_sidebar_state="expanded"  # 'expanded' or 'collapsed'
)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Create connection with MySQL database
DATABASE_URL = 'mysql://root:root123@localhost:3306/ams'
engine = create_engine(DATABASE_URL)

# Load initial data
query1 = 'SELECT * FROM employee_info'
employee_info = pd.read_sql(query1, engine)

query2 = 'SELECT * FROM dept_info'
dept_info = pd.read_sql(query2, engine)

query3 = 'SELECT * FROM shift_info'
shift_info = pd.read_sql(query3, engine)

query4 = 'SELECT * FROM attendance_info'
attendance_info = pd.read_sql(query4, engine)

query5 = 'SELECT * FROM designation_info'
designation_info = pd.read_sql(query5, engine)

query6='SELECT * FROM attendance_timing'
attendance_timing = pd.read_sql(query5, engine)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Display animated heading
html_code = """
<style>
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.heading {
    font-size: 2.5em;
    color: white;
    background: linear-gradient(270deg, #ff6f61, #de1a72, #4a00e0);
    background-size: 200% 200%;
    animation: gradient 5s ease infinite;
    padding: 10px;
    border-radius: 20px;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 60px; /* Adjust the height as needed */
}
</style>
<div class="heading">
    Employee Attendance Monitoring Dashboard
</div>
"""
st.markdown(html_code, unsafe_allow_html=True)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<
#Metrics...............
# Calculate metrics
employees_count = len(employee_info)
departments_count = len(dept_info['dept_name'].unique())
total_shifts = len(shift_info['shift_name'].unique())
designation_count = len(designation_info['designation'].unique())
# Create a row with multiple columns
col1, col2, col3, col4 = st.columns(4)
with col1:
# Box for Total Employees
 st.info(f"Total Employees: {employees_count}")
with col2:
# Box for Total Departments
 st.success(f"Total Departments: {departments_count}")
with col3:
# Box for Total Shifts
 st.warning(f"Total Shifts: {total_shifts}")
with col4:
# Box for Total Designations
 st.error(f"Total Designations: {designation_count}")
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<
#Charts/Graphs...........
# Organize charts into columns
# First row: Department-wise Employee Count and Department-wise Attendance
col1, col2 = st.columns(2)

# Department-wise Employee Count
query_dept = """
SELECT d.dept_name, COUNT(e.emp_id) AS num_employees
FROM dept_info d
JOIN employee_info e ON d.emp_id = e.emp_id
GROUP BY d.dept_name;
"""
df_dept = pd.read_sql_query(query_dept, engine)

fig_dept = px.pie(df_dept, 
                  names='dept_name', 
                  values='num_employees', 
                  title='Department-wise Employee Count',
                  color_discrete_sequence=px.colors.qualitative.Set2)
fig_dept.update_traces(textposition='inside', textinfo='percent+label')
col1.plotly_chart(fig_dept, use_container_width=True)

# Department-wise Attendance
query_attendance_dept = """
SELECT a.status, d.dept_name
FROM attendance_info a
JOIN dept_info d ON a.emp_id = d.emp_id;
"""
attendance_dept_df = pd.read_sql_query(query_attendance_dept, engine)
attendance_by_dept = attendance_dept_df.groupby('dept_name')['status'].count().reset_index()

fig_attendance_dept = px.bar(attendance_by_dept, 
                             x='dept_name', 
                             y='status', 
                             color='dept_name',
                             title='Department-wise Attendance',
                             labels={'dept_name': 'Department', 'status': 'Attendance Count'})
col2.plotly_chart(fig_attendance_dept, use_container_width=True)

# Second row: Shift-wise Employee Distribution and Designation-wise Employee Count
col3, col4 = st.columns(2)

# Shift-wise Employee Distribution
query_shift = """
SELECT shift_name, COUNT(emp_id) AS num_employees
FROM shift_info
GROUP BY shift_name
ORDER BY shift_name;
"""
df_shift = pd.read_sql_query(query_shift, engine)

fig_shift = px.bar(df_shift, 
                   x='shift_name', 
                   y='num_employees', 
                   title='Shift-wise Employee Distribution',
                   labels={'shift_name': 'Shift Name', 'num_employees': 'Number of Employees'},
                   color='shift_name')
col3.plotly_chart(fig_shift, use_container_width=True)

# Designation-wise Employee Count
query_desig = """
SELECT des.designation, COUNT(e.emp_id) AS num_employees
FROM designation_info des
JOIN employee_info e ON des.emp_id = e.emp_id
GROUP BY des.designation;
"""
df_desig = pd.read_sql_query(query_desig, engine)

fig_desig = px.pie(df_desig, names='designation', values='num_employees', 
                   title='Designation-wise Employee Count',
                   color_discrete_sequence=px.colors.qualitative.Set2,
                   hole=0.3)
fig_desig.update_traces(textposition='inside', textinfo='percent+label')
col4.plotly_chart(fig_desig, use_container_width=True)

# Separate row for Department vs. Designation Distribution
dept_desig_counts = employee_info.groupby(['dept_name', 'designation']).size().reset_index(name='count')

fig_dept_desig = px.bar(dept_desig_counts, 
                        x='dept_name', 
                        y='count', 
                        color='designation',
                        title='Department vs. Designation Distribution')
st.plotly_chart(fig_dept_desig, use_container_width=True)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
