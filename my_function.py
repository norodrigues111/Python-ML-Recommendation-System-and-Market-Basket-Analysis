#  Libraries
import pandas as pd
import plotly.express as px  

# User-friendly color palette for users over 65
color_palette = ['#440154', '#48186a', '#472d7b', '#3f4a8a', '#33638d', '#2a7b8d', '#21918c', '#28ae80', '#5ec962', '#addc30', '#fde725']

# Function created to reorder days of the week
def reorder_days(df):
    days_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    if 'day_of_week' in df:
        df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=days_order, ordered=True)
        return df.sort_values('day_of_week')
    else:
        return df

# Set a callback function to update the bar graph and tables based on the selected date range and aggregation period
def update_items_sold_bar_plot(df, start_date, end_date, aggregation_period, selected_item, data_neighbours):
    
    # Filter data based on the selected date range
    filtered_data = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    # Group data based on the selected aggregation period and calculate the count of items sold
    if aggregation_period == 'day':
        grouped_data = filtered_data.groupby(pd.Grouper(key='Date', freq='D'))['itemDescription'].count().reset_index(name='Count')
    elif aggregation_period == 'day_of_week':
        grouped_data = filtered_data.groupby(filtered_data['Date'].dt.day_name())['itemDescription'].count().reset_index(name='Count')
        grouped_data.rename(columns={'Date': 'day_of_week'}, inplace=True)
        grouped_data = reorder_days(grouped_data)
    else:
        grouped_data = filtered_data.groupby(pd.Grouper(key='Date', freq='M'))['itemDescription'].count().reset_index(name='Count')

    # Bar chart for the number of items sold based on the selected aggregation period
    line_fig = px.line(
        grouped_data,
        x='day_of_week' if aggregation_period == 'day_of_week' else 'Date',
        y='Count',
        title=f'Number of Items Sold ({start_date} to {end_date})',
        labels={'Count': 'Quantity'},
        orientation='v',
        color_discrete_sequence=['#440154'],   
        hover_data={'Count': ':y'})
    
    # Update layout to increase font size of hover tooltip
    line_fig.update_layout(hoverlabel=dict(font=dict(size=24)))  
    
    # Increase font size of labels
    line_fig.update_xaxes(title_text='Date', tickfont=dict(size=24), title_font=dict(size=30))
    line_fig.update_yaxes(title_text='Quantity',tickfont=dict(size=30), title_font=dict(size=30))

    # Update layout to make title black and bold
    line_fig.update_layout(title=dict(text=f'Number of Items Sold ({start_date} to {end_date})',
            font=dict(color='black', size=30)))
    
    # Set category orders for months 
    if aggregation_period == 'month':
        line_fig.update_xaxes(categoryorder='category ascending')

    # Bar chart for the Top 10 products sold
    top_10_data = filtered_data['itemDescription'].value_counts().nlargest(10).reset_index()
    top_10_data.columns = ['itemDescription', 'Quantity']

    top_10_bar_fig = px.bar(
        top_10_data,
        x='itemDescription',
        y='Quantity',
        title=f'Top 10 Products Sold ({start_date} to {end_date})',
        labels={'Quantity': 'Quantity'},
        color='itemDescription',
        color_discrete_sequence=color_palette) # Color palette defined on top
    
    # Update layout to hide legend
    top_10_bar_fig.update_layout(showlegend=False)
    
    # Increase font size for x-axis and y-axis labels
    top_10_bar_fig.update_xaxes(title_text='Product', tickfont=dict(size=24), title_font=dict(size=30))
    top_10_bar_fig.update_yaxes(title_text='Quantity', tickfont=dict(size=30), title_font=dict(size=30))
    
    # Update layout to increase font size of hover tooltip
    top_10_bar_fig.update_layout(hoverlabel=dict(font=dict(size=24)))  

    # Update layout to make title black and bold
    top_10_bar_fig.update_layout(title=dict(text=f'Top 10 Products Sold ({start_date} to {end_date})',
            font=dict(color='black', size=30)))

    # Calculate the bottom 10 products sold
    bottom_10_data = filtered_data['itemDescription'].value_counts().nsmallest(10).reset_index()
    bottom_10_data.columns = ['itemDescription', 'Quantity']

    # Get recommendated  items for the selected item
    attributes_list = data_neighbours.loc[selected_item, 2:11].tolist()

    # Create a list of dictionaries for the recommendation table
    recommendation_table_data = [{'Rank': i + 1, 'RecommendedItem': item} for i, item in enumerate(attributes_list)]

    return line_fig, top_10_bar_fig, bottom_10_data.to_dict('records'), recommendation_table_data