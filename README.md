![](./assets/readme_banner.png)

<p align="center">
  <!-- <a href="https://github.com/gfidanli/fantasy_football_analysis/releases/" target="_blank">
    <img alt="GitHub release" src="https://img.shields.io/github/v/release/gfidanli/fantasy_football_analysis?include_prereleases&style=flat-square">
  </a> -->

  <a href="https://github.com/gfidanli/fantasy_football_analysis/commits/master" target="_blank">
    <img src="https://img.shields.io/github/last-commit/gfidanli/fantasy_football_analysis?style=flat-square" alt="GitHub last commit">
  </a>

  <a href="https://github.com/gfidanli/fantasy_football_analysis/issues" target="_blank">
    <img src="https://img.shields.io/github/issues/gfidanli/fantasy_football_analysis?style=flat-square&color=red" alt="GitHub issues">
  </a>

  <a href="https://github.com/gfidanli/fantasy_football_analysis/pulls" target="_blank">
    <img src="https://img.shields.io/github/issues-pr/gfidanli/fantasy_football_analysis?style=flat-square&color=blue" alt="GitHub pull requests">
  </a>

  <a href="https://standardjs.com" target="_blank">
    <img alt="ESLint" src="https://img.shields.io/badge/code_style-standard-brightgreen.svg?style=flat-square">
  </a>

  <a href="https://github.com/gfidanli/fantasy_football_analysis/blob/master/LICENSE" target="_blank">
    <img alt="LICENSE" src="https://img.shields.io/github/license/gfidanli/fantasy_football_analysis?style=flat-square&color=yellow">
  </a>

  </a>
</p>
<hr>

A place where I share insights about NFL/Fantasy Football in a variety of formats:
- Daily notebooks
- Visualizations
- Tables
- Helpful scripts

With the aim of learning SQL, Python, data visualization techniques, statistical analysis/modeling, and reporting through my passion for NFL and Fantasy Football. 

# Daily Analysis
In order to hold myself accountable while becoming familiar with the main tools a Data Analyst uses at their job, I decided to participate in the [#100DaysOfCode Challenge](https://www.100daysofcode.com). I made a pledge to code every day for 100 days and post the results on Twitter.  

Within `/daily_analysis` you'll find each day's analysis in either Jupyter Notebook or Markdown format. For the majority of days, the process is very similar. At a high level, I use SQL to query my database for the data I need, use SQL/Python to clean and transform the data, and then use a visualization package (Matplotlib or Seaborn) or software (Tableau) to create supporting visualizations as necessary.  

Each day builds upon new skills learned and practiced on the previous and I frequently revisit old work to add to the analysis by incorporating new ideas and/or techniques I learn along the way.

# ETL (Extract Transform Load)
As a Data Analyst, I'll be exposed to ETL scripts and data pipelines so it's imperative I understand how they work and how to write them myself. I certainly can't do my daily analysis work if I don't have structured data to work with! So, with the help of an incredible Python package, `nfl_data_py`, I was able to build a robust database of NFL data that I can use to analyze not only NFL seasons themselves but also fantasy football.

The ETL process originally contained two scripts which are now saved under `etl/archive`. Since this repository is more learning-focused, I wanted to keep them to show how I went from the old process to the new one. The refactoring took place on Day 60 of the #100DaysOfCode Challenge and you can find that writeup here `daily_analysis/day_51_60/day60.md`. Now, a user needs to only update `config.py` and run `etl.py`. If the user wants to generate new tables, just add that code to `transformations.py`.
<br/><br/>
