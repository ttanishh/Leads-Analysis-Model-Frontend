# Lead Analysis Model (LAM)

A machine learning-powered lead scoring system with a Flask API and Streamlit dashboard for analyzing and scoring potential leads.

## 🚀 Features

- **ML-Powered Lead Scoring**: Predicts lead interest and assigns scores
- **Flask API**: RESTful API for batch lead scoring
- **Streamlit Dashboard**: Interactive web interface for data exploration and lead scoring
- **Data Export**: Export scored leads in CSV and Excel formats

## 📁 Project Structure

```
LAM/
├── lead_api.py              # Flask API for lead scoring
├── lead_dashboard.py        # Streamlit dashboard
├── lead_ml.py              # ML model training script
├── model/
│   └── lead_scoring_model.pkl  # Trained ML model
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-service deployment
└── README.md              # This file
```

## 🛠️ Installation & Setup

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd LAM
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API**
   ```bash
   python lead_api.py
   ```
   The API will be available at `http://localhost:5000`

5. **Run the Dashboard** (in a new terminal)
   ```bash
   streamlit run lead_dashboard.py
   ```
   The dashboard will be available at `http://localhost:8501`

### Option 2: Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the services**
   - API: `http://localhost:5000`
   - Dashboard: `http://localhost:8501`

### Option 3: Individual Docker Containers

1. **Build the image**
   ```bash
   docker build -t lam-app .
   ```

2. **Run API container**
   ```bash
   docker run -p 5000:5000 -v $(pwd)/model:/app/model lam-app python lead_api.py
   ```

3. **Run Dashboard container**
   ```bash
   docker run -p 8501:8501 -v $(pwd)/model:/app/model lam-app streamlit run lead_dashboard.py --server.port=8501 --server.address=0.0.0.0
   ```

## 🌐 API Usage

### Endpoints

- `GET /` - Health check
- `POST /predict` - Batch lead scoring

### Example API Request

```python
import requests
import pandas as pd

# Load your data
df = pd.read_excel('your_leads.xlsx')

# Make prediction request
response = requests.post(
    'http://localhost:5000/predict',
    json=df.to_dict(orient='records')
)

# Get results
results = response.json()
for result in results:
    print(f"Score: {result['lead_score_percent']}%, Category: {result['lead_category']}")
```

## 📊 Dashboard Usage

1. **Upload Data**: Upload your Excel file with lead data
2. **Explore Data**: Use the EDA section to understand your data
3. **Score Leads**: Use the ML model to score your leads
4. **Export Results**: Download scored data in CSV or Excel format

## 🚀 Production Deployment

### Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-lam-app
   ```

2. **Add buildpacks**
   ```bash
   heroku buildpacks:add heroku/python
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS/GCP/Azure Deployment

Use the provided Docker configuration:

```bash
# Build and push to container registry
docker build -t your-registry/lam-app .
docker push your-registry/lam-app

# Deploy to your cloud platform using docker-compose.yml
```

## 🔧 Configuration

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `STREAMLIT_SERVER_PORT`: Dashboard port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Dashboard address (default: 0.0.0.0)

### Model Configuration

The ML model expects the following features:
- `Took_Exam`: Yes/No
- `Visa_Knowledge`: Yes/No  
- `Language_Test_Willing`: Yes/No
- `Follows_Intl_Edu_Content`: Yes/No
- Additional numerical features as needed

## 📈 Model Performance

The lead scoring model provides:
- **Lead Score**: Percentage (0-100%) indicating likelihood of interest
- **Predicted Interest**: Binary classification (0/1)
- **Lead Category**: High (>70%), Medium (40-70%), Low (<40%)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Happy Lead Scoring! 🎯** 