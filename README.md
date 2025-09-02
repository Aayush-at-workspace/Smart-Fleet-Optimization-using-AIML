# Smart Fleet Optimization System 
 
A comprehensive AI-powered fleet optimization platform that uses machine learning to predict demand patterns and optimize taxi fleet operations in urban environments. 
  
## Features 
- AI-Powered Demand Prediction: Machine learning models predict ride demand across different zones and time periods 
- Real-time Fleet Optimization: Dynamic routing and zone allocation based on current demand patterns 
- Interactive Analytics Dashboard: Comprehensive visualization of fleet performance metrics 
- Zone-based Intelligence: Smart recommendations for optimal pickup locations with probability scoring 
  
## Technology Stack 
  
### Backend 
- Python 3.9+: Core programming language 
- Flask: Web framework for API endpoints 
- SQLite: Lightweight database for data storage 
- Pandas: Data manipulation and analysis 
- Scikit-learn: Machine learning algorithms (MLPRegressor) 
  
### Frontend 
- React 18: Modern JavaScript framework 
- Framer Motion: Smooth animations and transitions 
- Chart.js: Interactive data visualizations 
  
## Installation and Setup 
  
### Prerequisites 
- Python 3.9 or higher 
- Node.js 16+ and npm 
- Git 
  
### Backend Setup 
1. Clone the repository: 
   git clone <repository-url> 
   cd Smart-Fleet-Optimization-using-AIML 
  
2. Create and activate virtual environment: 
   python -m venv venv 
   source venv/bin/activate  # On Windows: venv\Scripts\activate 
  
3. Install Python dependencies: 
   pip install -r requirements.txt 
  
### Frontend Setup 
1. Navigate to frontend directory: 
   cd frontend 
  
2. Install Node.js dependencies: 
   npm install 
  
3. Start the React development server: 
   npm start 
  
## Usage 
  
### Backend API Endpoints 
- GET /zones: Retrieve all taxi zones with IDs and names 
- POST /complete_ride: Submit ride completion data and get optimization results 
- GET /health: Health check endpoint 
  
### Frontend Navigation 
- Dashboard: Overview of system metrics and recent activity 
- Fleet Optimization: Ride completion form and AI recommendations 
- Analytics: Detailed performance metrics and insights 
  
## Project Structure 
  
The project combines a Flask backend with machine learning algorithms and a React frontend to create an intelligent system for fleet management. The system analyzes historical trip data, predicts demand patterns, and provides real-time optimization recommendations for taxi drivers and fleet operators. 

## 🚀 Quick Start with Docker

1. Build the Docker image:
   ```bash
   docker build -t smart-fleet-app .
   ```

2. Run the container:
   ```bash
   docker run -d -p 5000:5000 --name smart-fleet-container smart-fleet-app
   ```

3. Visit [http://localhost:5000](http://localhost:5000) in your browser.

For more details, see [DOCKER_SETUP.md](./DOCKER_SETUP.md).