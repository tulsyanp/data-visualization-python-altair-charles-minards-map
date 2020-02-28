#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd 
import numpy as np
import altair as alt

def datapre_city(df):
    modDf = df.dropna(how='all')
    modDf = df.dropna(how='any', subset=['CITY'])
    city = modDf[['LONC', 'LATC', 'CITY']]
    city.columns = ['lon','lat','city']
    return city;


def datapre_temp(df):
    modDf = df.dropna(how='any', subset=['TEMP'])
    temperatures = modDf[['LONT','TEMP','DAYS','MON', 'DAY']]
    temperatures['DAY'] = temperatures['DAY'].astype('str')
    temperatures['DAY'] = temperatures['DAY'].str.strip('.0')
    temperatures['MON'] = temperatures['MON'].astype('str')
    temperatures['day'] = temperatures[['DAY', 'MON']].agg('-'.join, axis=1)
    temperatures = temperatures.drop(columns=['MON', 'DAY'])
    temperatures = temperatures.replace('nan-nan', np.nan)
    temperatures.columns = ['lon','temp','days','date']
    temperatures["date"] = temperatures.fillna("").apply(axis=1, func=lambda row: "{}°C  {}".format(row[1], row[3].replace("-", ",")))
    return temperatures;
    
def datapre_army(df):
    army = df[['LONP','LATP','SURV','DIR','DIV']]
    army.columns = ['lon','lat','survivor','dir','division']
    army = army.sort_values(by=["division", "survivor"], ascending=False)
    return army;

def chartcreation(temp,army,city):
    temperatures = temp
    troops = army
    cities = city
    
    troops_chart = alt.Chart(troops).mark_trail().encode(
        longitude='lon:Q',
        latitude='lat:Q',
        size=alt.Size(
            'survivor',
            scale=alt.Scale(range=[2, 30]),
            legend=None
        ),
        detail='division',
        color=alt.Color(
            'division',
            scale=alt.Scale(
                domain=['1', '2', '3'],
                range=['#F44336', '#64B5F6', '#AFB42B']
            ),
            legend=None
        ),
        tooltip=[alt.Tooltip('lat', title='Latitude'), alt.Tooltip('lon', title='Longitude'), alt.Tooltip('survivor', title='Survivors'), alt.Tooltip('dir', title='Direction')]
    )

    troops_text = troops.iloc[::2, :].copy()
    troops_text["lon"] += 0.13 * (troops_text["division"])
    troops_text["lat"] += troops_text["dir"].replace({"A": 0.35, "R": -0.21})

    troops_text_chart = alt.Chart(troops_text).mark_text(
        font='Verdana',
        fontSize=8,
        fontStyle='italic',
        dx=1,
        dy=8,
        angle=280
    ).encode(
        longitude='lon:Q',
        latitude='lat:Q',
        text='survivor'
    )

    cities_chart_circle = alt.Chart(cities).mark_circle(size=60, color="#000000").encode(
        longitude='lon:Q',
        latitude='lat:Q',
        tooltip=[alt.Tooltip('lat', title='Latitude'), alt.Tooltip('lon', title='Longitude'),
                 alt.Tooltip('city', title='City')]
    )

    cities_chart_text = alt.Chart(cities).mark_text(
        font='Verdana',
        fontSize=9,
        fontStyle='bold',
        dx=7,
        dy=-12
    ).encode(
        longitude='lon:Q',
        latitude='lat:Q',
        text='city',
    )

    x_encode_chart = alt.X(
        'lon:Q',
        scale=alt.Scale(domain=[troops["lon"].min(), troops["lon"].max()]),
        axis=alt.Axis(title="Longitude", grid=True))

    y_encode_chart = alt.Y(
        'lat:Q',
        scale=alt.Scale(domain=[troops["lat"].min() - 1.25, troops["lat"].max() + 1.25]),
        axis=alt.Axis(title="Latitude", grid=True, orient="left"))
    
    map_chart = troops_chart + cities_chart_circle + cities_chart_text + troops_text_chart + alt.Chart(troops).mark_text().encode(
        x=x_encode_chart,
        y=y_encode_chart,
    )

    x_encode = alt.X(
        'lon:Q',
        scale=alt.Scale(domain=[troops["lon"].min(), troops["lon"].max()]),
        axis=alt.Axis(title="Longitude", grid=True))

    y_encode = alt.Y(
        'temp',
        axis=alt.Axis(title="Temperature on Retreat", grid=True, orient='right'),
        scale=alt.Scale(domain=[temperatures["temp"].min() - 10, temperatures["temp"].max() + 10]))

    temperatures_chart = alt.Chart(temperatures).mark_line(
        color="#4CAF50"
    ).encode(
        x=x_encode,
        y=y_encode,
    ) + alt.Chart(temperatures).mark_circle(size=50, color="#4CAF50").encode(
        x=x_encode,
        y=y_encode,
        tooltip=[alt.Tooltip('lon', title='Longitude'),
                 alt.Tooltip('temp', title='Temperature'), alt.Tooltip('date', title='Date')]
    ) + alt.Chart(temperatures).mark_text(
        dx=5,
        dy=20,
        font='Verdana',
        fontSize=10,
        fontStyle='bold',
    ).encode(
        x=x_encode,
        y=y_encode,
        text='date',
    )

    temperatures_chart = temperatures_chart.properties(height=200)

    final_chart = alt.vconcat(map_chart, temperatures_chart).configure_view(
        width=1000,
        height=600,
        strokeWidth=0,
    ).configure_axis(
        grid=False,
        labelFont="Verdana",
        titleFont="Verdana",
    )

    return final_chart


def main():
    df = pd.read_csv('minard-data.csv')
    city = datapre_city(df)
    temp = datapre_temp(df)
    army = datapre_army(df)
    chart = chartcreation(temp,army,city)
    chart.save('index.html', embed_options={'actions': False})
  
if __name__== "__main__":
  main()



    



