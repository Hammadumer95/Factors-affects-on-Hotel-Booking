# -*- coding: utf-8 -*-
"""HotelBookingAnalysis.ipynb

Automatically generated by Colaboratory.
Original file is located at
    https://colab.research.google.com/drive/13votQ2XRypSH0tul0dXym9HbAVlkDpnk
"""

#.........................................................
#Here i am uploaded the dataset file in colab if you want to upload it from your pc check next few lines.
import pandas as pd
data = pd.read_csv('hotel_bookings.csv')
data.head()
#.........................................................
from google.colab import files
data = files.upload()
#.........................................................

import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

#Little bit discription of the Data
print('Shape of Data Set' , data.shape)
data.describe(include='all')

#Change the columns names
data.columns = ['Hotel', 'Canceled', 'LeadTime', 'ArrivingYear', 'ArrivingMonth', 'ArrivingWeek','ArrivingDate', 'WeekendStay',
              'WeekStay', 'Adults', 'Children', 'Babies', 'Meal','Country', 'Segment', 'DistChannel','RepeatGuest', 'PrevCancel',
              'PrevBook', 'BookRoomType','AssignRoomType', 'ChangeBooking', 'DepositType', 'Agent','Company', 'WaitingDays', 
              'CustomerType', 'Adress','ParkSpace', 'SpecialRequest','Reservation', 'ReservationDate']

data.head()

#Identify Categorical and Continuous Variables
def get_cat_con_var(data):
    unique_list = pd.DataFrame([[i,len(data[i].unique())] for i in data.columns])
    unique_list.columns = ['name','uniques']

    universe = set(data.columns)
    cat_var = set(unique_list.name[(unique_list.uniques<=12)      | 
                                   (unique_list.name=='Country')  | 
                                   (unique_list.name=='Agent')                                     
                                  ])
    con_var = universe - cat_var
    
    return cat_var, con_var 


cat_var, con_var = get_cat_con_var(data)

print("Continuous Variables (",len(con_var),")\n",con_var,'\n\n'
      "Categorical Variables(",len(cat_var),")\n",cat_var)

#13 continuous and 19 categorical variables are identified, based on number of unique values i.e. factor levels.
#The number of countries is greater than 12 (factor level threshold), but should be assigned to categorical variables based on knowledge.

#Missing Values (Data Preprocessing)
missing_col_list = data.columns[data.isna().sum()>0]
print('Missing data columns =',missing_col_list)
t = pd.DataFrame([[i,data[i].unique(),data[i].isna().sum()] for i in missing_col_list])
t.columns = ['name','unique','missing']
t   
#The number of missing values found is 4 & 488 for features 'Children' & 'Country' respectively, 
#both of which are categorical.
#Features Agent and Company acts as primary keys, however, contains missing values.

data.loc[data.Children.isna(),'Children'] = 0

data.loc[data.Country.isna(),'Country'] = 'NAA'

# agent and country are ID, cannot be imputed. Impute available/unavailable.
data.loc[data.Agent>0,'Agent']      = 1
data.loc[data.Agent.isna(),'Agent'] = 0

data.loc[data.Company>0,'Company']      = 1
data.loc[data.Company.isna(),'Company'] = 0

print('Remaining Missing Values = ',data.isna().sum().sum())

def print_uniques_values(cols):
  for i in cols:
     print(i,data[i].unique())

print_uniques_values(cat_var)

#Categorical Features seems to have outlier values
#Babies : 9, 10
#Parkspace: 8
#Children : 10

#Impute Outliers (for Categorical Variables)
 data.loc[data.Babies    > 8,'Babies']    = 0
 data.loc[data.ParkSpace > 5,'ParkSpace'] = 0
 data.loc[data.Children > 8,'Children'] = 0
 
data[cat_var].describe()
#No outliers seem to exist, by examining all Categorical Variables.Check Below

#Find Outliers (for Continuous Variables)
data[con_var].describe()

#Impute Outliers (for Continuous Variable)

data.loc[data.LeadTime      > 500,'LeadTime'     ]=500
data.loc[data.WaitingDays   >   0,'WaitingDays'  ]=  1
data.loc[data.WeekendStay   >=  5,'WeekendStay'  ]=  5
data.loc[data.Adults        >   4,'Adults'       ]=  4
data.loc[data.PrevBook      >   0,'PrevBook'     ]=  1
data.loc[data.PrevCancel    >   0,'PrevCancel'   ]=  1
data.loc[data.WeekStay      >  10,'WeekStay'     ]= 10
data.loc[data.ChangeBooking >   5,'ChangeBooking']=  5

cat_var = set(list(cat_var) + ['PrevBook','PrevCancel'])
con_var = set(data.columns) - cat_var

data[con_var].describe()

cor_mat = data.corr()
fig, ax = plt.subplots(figsize=(16,6))
sns.heatmap(cor_mat,ax=ax,cmap="YlGnBu",linewidths=0.1)

pie_list = list()
bar_list = list()
line_list = list()

for i in cat_var:
    if len(data[i].unique())<=5:
        pie_list.append(i)
    elif len(data[i].unique())<=12:
        bar_list.append(i)
    else:
        line_list.append(i)
        
print('Features with 5 levels   \n',pie_list,'\n\n',
      'Features with 5-10 levels\n',bar_list,'\n\n',
      'Features with >10 levels \n',line_list)

def get_pie_label_values(data,col):
    temp = pd.DataFrame([[i,data[data[col]==i].shape[0]] for i in data[col].unique()])    
    return temp[0],temp[1]

def put_into_bucket(data,col,bucket):    
    diff = int(max(data[col])/bucket)
    for i in range(bucket):    
        data.loc[(data[col] > diff*(i)) & (data[col] <= diff*(i+1)),col] = i+1
    data.loc[data[col]==0,col] = 1
    return data

df = put_into_bucket(data,'LeadTime',bucket=5)

#Reservation Date Extraction (into Date, Month, Year)
 # Extraction
new = data['ReservationDate'].str.split('-', n = 2, expand = True) 
data['YearReserve' ]= new[0] 
data['MonthReserve']= new[1] 
data['DateReserve' ]= new[2] 
data.drop(columns=['ReservationDate'],inplace=True)

n_row = 3
n_col = 5
fig = make_subplots(rows=n_row, cols=n_col, specs=[[{'type':'domain'}, {'type':'domain'},{'type':'domain'}, {'type':'domain'},{'type':'domain'}],
                                           [{'type':'domain'}, {'type':'domain'},{'type':'domain'}, {'type':'domain'},{'type':'domain'}],
                                           [{'type':'domain'}, {'type':'domain'},{'type':'domain'}, {'type':'domain'},{'type':'domain'}]],                                           
                   subplot_titles=pie_list,
                   horizontal_spacing = 0.03, vertical_spacing = 0.08)

row = 1
col = 1
x_adr = 0.082
y_adr = 0.85
x_diff = 0.21 # increasing order
y_diff = 0.845 - 0.485 # decreasing order
ls = list()
for i in pie_list:
    labels, values = get_pie_label_values(data,i)    
    fig.add_trace(go.Pie(labels=labels, values=values, name=i),row,col)      # Design Pie Charts          
    ls.append(dict(text=str('<b>'+i+'</b>'), x=x_adr, y=y_adr, font_size=10, showarrow=False)) # Get position of text in Pie-Holes    
    col+=1                                                                   # Get Grid Details
    x_adr+=x_diff
    if col > n_col:
        col =1
        row+=1
        x_adr = 0.082
        y_adr-= y_diff
    
fig.update_traces(hole=0.65, hoverinfo="label+percent+name")    
fig.update_layout(title_text="Visualizing Categorical Variables using <b>Pie charts</b> : (<i>With or less than 5 levels</i>)",
                  annotations=ls,
                  width=1200,height=650,
                  showlegend=False)
fig.show()

n_row = 1
n_col = 5
fig = make_subplots(rows=n_row, cols=n_col, specs=[[{'type':'bar'}, {'type':'bar'},{'type':'bar'},{'type':'bar'},{'type':'bar'}]],                                                   
                   subplot_titles=bar_list,
                   horizontal_spacing = 0.03, vertical_spacing = 0.13)

row = 1
col = 1
for i in bar_list:
    labels, values = get_pie_label_values(data,i)
    #print(labels, values)
    fig.add_trace(go.Bar(y=values),row=row, col=col)
    
    col+=1
    if col > n_col:
        col =1
        row+=1    
    fig.update_layout(annotations=[dict(font_size=10, showarrow=False)])

    
fig.update_layout(title_text="Visualizing Categorical Variables using <b>Bar charts</b>: (<i>Within 5 - 10 levels</i>)",
                  width=1200,height=500,showlegend=False)
fig.show()

ls=list()
for i in line_list:
    for j in df[i].unique():
        ls.append([j,df[df[i]==j].shape[0],i])
ls = pd.DataFrame(ls)
ls.columns = ['column','counts','feature']

ls.sort_values(by='counts',ascending=False,inplace=True)
fig = px.bar(ls[1:50],x='column',y='counts',color='counts',facet_col='feature')
fig.update_layout(title_text="Visualizing Categorical Variables using <b>Bar charts</b> : (<i>More than 10 levels</i>, Top 50 Countries)",
                  width=1150,height=400,showlegend=False)
fig.show()

list_01 = ['Adults', 'WaitingDays', 'LeadTime', 'ChangeBooking', 
            'WeekStay', 'WeekendStay','YearReserve','MonthReserve']

n_row = 2
n_col = 4
fig = make_subplots(rows=n_row, cols=n_col, specs=[[{'type':'bar'},{'type':'bar'},{'type':'bar'},{'type':'bar'}],
                                                   [{'type':'bar'},{'type':'bar'},{'type':'bar'},{'type':'bar'}]],               
                   subplot_titles=list_01,
                   horizontal_spacing = 0.03, vertical_spacing = 0.23)

row = 1
col = 1
for i in list_01:
    labels, values = get_pie_label_values(data,i)
    #print(labels, values)
    fig.add_trace(go.Bar(x=labels,y=values),row=row, col=col)
    
    col+=1
    if col > n_col:
        col =1
        row+=1    
    fig.update_layout(annotations=[dict(font_size=10, showarrow=False)])
    
fig.update_layout(title_text="Visualizing Continuous Variables using <b>Bar charts</b>",width=1200,height=500,showlegend=False)
fig.show()

list_02 = ['DateReserve','ArrivingDate','ArrivingWeek']

n_row = 3
n_col = 1
fig = make_subplots(rows=n_row, cols=n_col, specs=[[{'type':'bar'}],
                                                   [{'type':'bar'}],
                                                   [{'type':'bar'}]],                                                                                    
                   subplot_titles=list_02,
                   horizontal_spacing = 0.03, vertical_spacing = 0.08)

row = 1
col = 1
for i in list_02:
    labels, values = get_pie_label_values(data,i)
    print(i,'=',min(values))
    values = values - min(values)        
    fig.add_trace(go.Bar(x=labels,y=values),row=row, col=col)
    col+=1
    if col > n_col:
        col =1
        row+=1    
    fig.update_layout(annotations=[dict(font_size=10, showarrow=False)])
    
fig.update_layout(title_text="Visualizing Continuous Variables using <b>Bar charts</b>",width=1200,height=700,showlegend=False)
fig.show()
