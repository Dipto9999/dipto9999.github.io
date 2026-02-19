# Muntakim Rahman : Developer Portfolio

 ## Contents

* [Overview](#Overview)
* [Dashboards](#Dashboards)
    * [Steam](#Steam)
    * [Steam](#GoodReads)

## Overview

This is my portfolio website, where I have included my academic and project highlights so far in my career. I have also included some stats of my hobbies and pasttimes with use of online **API**s.


This is my portfolio website, where I've highlighted academic achievements and my engineering projects. I also showcase some hobby stats with data visualizations, presented in a responsive **React** web app.

## Dashboards

### Steam

I pulled my account data from the **Steam API** using the [`steam.py`](src/assets/data/steam/steam.py) **Python** script.
After fetching, the data was processed and cleaned with **pandas**, then visualized with **vega-altair**.

The initial [`Dipto9999_Dashboard.json`](src/assets/data/steam/Charts/Dipto9999_Dashboard.json) and related chart assets
were migrated to the **React** application and further adjusted for browser responsiveness.

<div align = "center">
    <img src = "src/assets/data/steam/Charts/Dipto9999_Dashboard.svg" width = 750 title = "Dipto9999 Steam Dashboard">
</div>

#### Automation

This data is automatically updated with **GitHub Actions** every **Monday** at **6 AM UTC**.

<div align = "center">
    <img src = "ref/GitHub_Actions.png" width = 750 title = "GitHub Action"/>
</div>


### GoodReads

GoodReads doesn't provide access to its **API** for new users. I exported my user data from the website, cleaned, and visualized the data in the [`GoodReads_Stats.ipynb`](src/assets/data/goodreads/GoodReads_Stats.ipynb) **Jupyter Notebook**.

The initial [`Muntakim_Dashboard.json`](src/assets/data/goodreads/Charts/Muntakim_Dashboard.json) and related chart assets
were migrated to the **React** application and further adjusted for browser responsiveness.

<div align = "center">
    <img src = "src/assets/data/goodreads/Charts/Muntakim_Dashboard.svg" width = 750 title = "Muntakim GoodReads Dashboard">
</div>
