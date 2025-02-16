import json
import os
import pandas as pd
import jdatetime
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Mapping Persian month names to their respective numbers and names
persian_months = {
    'فروردین': 1, 'اردیبهشت': 2, 'خرداد': 3,
    'تیر': 4, 'مرداد': 5, 'شهریور': 6,
    'مهر': 7, 'آبان': 8, 'آذر': 9,
    'دی': 10, 'بهمن': 11, 'اسفند': 12
}

# Adding reverse mapping from numbers to Persian month names
reverse_persian_months = {v: k for k, v in persian_months.items()}

def convert_persian_numbers_to_numeric(persian_str):
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers = '0123456789'
    translation_table = str.maketrans(persian_numbers, english_numbers)
    return persian_str.translate(translation_table)

def load_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_persian_date(date_str):
    try:
        parts = date_str.split()
        persian_month = parts[0]
        year_str = parts[1].split('(')[0].strip()
        year = int(year_str)
        month = persian_months[persian_month]
        return jdatetime.date(year, month, 1).togregorian()
    except Exception as e:
        print(f"Error parsing date: {date_str}, {e}")
        return None

def process_reviews(data):
    reviews_list = []
    for hotel in data:
        hotel_name = hotel['hotel_name']
        for review in hotel['reviews']:
            review_date = parse_persian_date(review['date'])
            if review_date:
                rating_str = review.get('rating', '0')
                try:
                    rating = float(convert_persian_numbers_to_numeric(rating_str))
                except ValueError:
                    rating = None  # or set to a default value, e.g., 0.0
                reviews_list.append({
                    'hotel_name': hotel_name,
                    'review_date': review_date,
                    'rating': rating
                })
    return pd.DataFrame(reviews_list)

def extract_important_word(name):
    words = name.split()
    important_word = max(words, key=len)
    return important_word.capitalize()

def generate_persian_month_year_label(date):
    persian_date = jdatetime.date.fromgregorian(date=date)
    return f"{reverse_persian_months[persian_date.month]} {persian_date.year}"

def sort_dates(month_year_series):
    return month_year_series.map(lambda x: jdatetime.date(int(x.split()[1]), persian_months[x.split()[0]], 1).togregorian())

def generate_interactive_charts(df, city_name):
    df['review_date'] = pd.to_datetime(df['review_date'], errors='coerce')
    important_words = {name: extract_important_word(name) for name in df['hotel_name'].unique()}
    df['hotel_word'] = df['hotel_name'].map(important_words)
    df['month_year'] = df['review_date'].apply(generate_persian_month_year_label)
    df['sorted_dates'] = sort_dates(df['month_year'])

    fig = make_subplots(rows=1, cols=1)

    # Total reviews per hotel
    total_reviews = df['hotel_word'].value_counts()
    total_reviews_bar = go.Bar(
        x=total_reviews.index,
        y=total_reviews.values,
        name='Total Reviews',
        text=total_reviews.values,
        textposition='auto'
    )

    # Reviews per hotel per month
    reviews_per_month = df.groupby(['month_year', 'hotel_word']).size().unstack(fill_value=0)
    reviews_per_month = reviews_per_month.sort_index(axis=0, key=lambda x: sort_dates(pd.Series(x)))
    reviews_per_month_bar = [
        go.Bar(
            x=reviews_per_month.index,
            y=reviews_per_month[hotel],
            name=hotel
        ) for hotel in reviews_per_month.columns
    ]

    # Adding traces to the figure
    fig.add_trace(total_reviews_bar)
    for trace in reviews_per_month_bar:
        fig.add_trace(trace)

    # Update layout for dropdown
    fig.update_layout(
        barmode='stack',
        updatemenus=[
            dict(
                buttons=list([
                    dict(label="Total Reviews",
                         method="update",
                         args=[{"visible": [True] + [False] * len(reviews_per_month_bar)},
                               {"title": "Total Reviews Per Hotel in " + city_name},
                               {"xaxis": {"title": "Hotel Name (Important Word)"},
                                "yaxis": {"title": "Number of Reviews"}}]),
                    dict(label="Reviews per Month",
                         method="update",
                         args=[{"visible": [False] + [True] * len(reviews_per_month_bar)},
                               {"title": "Reviews Per Hotel Per Month in " + city_name},
                               {"xaxis": {"title": "Month-Year (Persian)"},
                                "yaxis": {"title": "Number of Reviews"}}])
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
            ),
        ]
    )

    fig.update_layout(title_text=f"Insights for {city_name}")
    fig.show()

# Define the path to the reviews directory
reviews_dir = os.path.join(os.path.dirname(__file__), '../../rag/core', '..', 'data', 'reviews')
shiraz_path = os.path.join(reviews_dir, 'shiraz_hotel_reviews.json')
mashhad_path = os.path.join(reviews_dir, 'mashhad_hotel_reviews.json')

# Load the data
shiraz_data = load_data(shiraz_path)
mashhad_data = load_data(mashhad_path)

# Process the data
shiraz_reviews_df = process_reviews(shiraz_data)
mashhad_reviews_df = process_reviews(mashhad_data)

# Generate interactive charts for Shiraz
generate_interactive_charts(shiraz_reviews_df, 'Shiraz')

# Generate interactive charts for Mashhad
generate_interactive_charts(mashhad_reviews_df, 'Mashhad')
