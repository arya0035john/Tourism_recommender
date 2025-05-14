from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

df = pd.read_csv("Untitlednew.csv")
df = df.rename(columns={
    'Place Name': 'place_name',
    'State/Region': 'state_region',
    'Type of Place': 'place_type',
    'Suitable Season(s)': 'season',
    'Budget (INR)': 'budget',
    'Mid-range (INR)': 'midrange',
    'Luxury (INR)': 'luxury',
    'Recommended for': 'recommended'
})

def normalize_place_type(ptype):
    if 'desert' in ptype.lower():
        return 'Desert'
    elif 'heritage' in ptype.lower():
        return 'Heritage'
    else:
        return ptype.strip()

df['place_type'] = df['place_type'].apply(normalize_place_type)

unique_types = sorted(df['place_type'].unique())

unique_seasons = sorted({season.strip() for seasons in df['season'] for season in seasons.split(',')})

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    selected_type = None
    selected_people = None
    selected_days = None
    selected_season = None
    selected_budget = None

    if request.method == 'POST':
        selected_type = request.form.get('place_type')
        selected_people = request.form.get('people')
        selected_days = request.form.get('days')
        selected_season = request.form.get('season')
        selected_budget = request.form.get('budget')

        try:
            selected_days = int(selected_days) if selected_days else 1
        except ValueError:
            selected_days = 1
        try:
            selected_people = int(selected_people) if selected_people else 1
        except ValueError:
            selected_people = 1
        try:
            budget_total = float(selected_budget) if selected_budget else 0
        except ValueError:
            budget_total = 0

        per_day_budget = budget_total / max(selected_days, 1)

        filtered = df[df['place_type'] == selected_type]

        if selected_season and selected_season != "All year":
            mask = filtered['season'].str.contains(selected_season, na=False) \
                   | filtered['season'].str.contains("All year", na=False)
            filtered = filtered[mask]

        filtered = filtered[filtered['budget'] <= per_day_budget].copy()

        filtered['diff'] = per_day_budget - filtered['budget']
        filtered = filtered.sort_values(by='diff')

        results = filtered.to_dict(orient='records')

    return render_template('index.html',
                           types=unique_types,
                           seasons=unique_seasons,
                           results=results,
                           selected_type=selected_type,
                           selected_people=selected_people,
                           selected_days=selected_days,
                           selected_season=selected_season,
                           selected_budget=selected_budget)

if __name__ == '__main__':
    app.run(debug=True)
