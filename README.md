# Influencer Engagement and Sponsorship Coordination Platform

## Overview

This platform connects Sponsors and Influencers, allowing Sponsors to advertise their products/services and Influencers to gain monetary benefits. The project is built using Flask, Jinja2 templates, Bootstrap, and SQLite.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Roles](#roles)
  - [Admin](#admin)
  - [Sponsors](#sponsors)
  - [Influencers](#influencers)
- [Core Functionalities](#core-functionalities)
- [Recommended Functionalities](#recommended-functionalities)
- [Optional Functionalities](#optional-functionalities)
- [Project Report](#project-report)

## Features

- Admin dashboard for monitoring and statistics
- Campaign management for sponsors
- Ad request management
- Search functionality for influencers and public campaigns
- Ad request actions for influencers (accept, reject, negotiate)
- API resources for user interaction
- Responsive frontend design

## Technologies Used

- **Backend**: Flask, SQLite
- **Frontend**: Jinja2, Bootstrap, HTML, CSS, JS

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/chanikkyasaai/iescp.git
   ```
2. **Navigate to the project directory**:
   ```bash
   cd iescp
   ```
3. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the application**:
   ```bash
   flask run
   ```
6. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Roles

### Admin

- Monitor all users and campaigns
- View statistics (active users, campaigns, ad requests, flagged users)
- Flag inappropriate campaigns/users

### Sponsors

- Create and manage campaigns
- Search for influencers and send ad requests
- Track individual campaigns
- Profile includes: Name, Industry, Budget

### Influencers

- Receive and manage ad requests (accept, reject, negotiate)
- Search for public campaigns
- Update publicly visible profile
- Profile includes: Name, Category, Niche, Reach

## Core Functionalities

1. **Admin login and user login**:
   - Separate login/register forms for Admin, Sponsors, and Influencers
   - Differentiation of user types in the model

2. **Admin Dashboard**:
   - Display relevant statistics (active users, campaigns, ad requests, flagged users)

3. **Campaign Management** (Sponsors):
   - Create, update, and delete campaigns

4. **Ad Request Management** (Sponsors):
   - Create, edit, and delete ad requests

5. **Search for influencers and public campaigns**:
   - Sponsors search based on niche, reach, followers
   - Influencers search based on niche, relevance

6. **Ad Request Actions** (Influencers):
   - View, accept/reject, and negotiate ad requests

## Recommended Functionalities

- API resources for user interaction
- External libraries for creating charts (e.g., ChartJS)
- Frontend validation using HTML5/JavaScript
- Backend validation within controllers

## Optional Functionalities

- Responsive frontend design using CSS/Bootstrap
- Proper login system using Flask extensions (flask_login, flask_security)
- Dummy payment portal for ad requests
