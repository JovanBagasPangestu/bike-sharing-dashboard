# Bike Sharing Analytics Dashboard

Dashboard Streamlit untuk menganalisis pola penyewaan sepeda 2011–2012
(Bike Sharing Dataset): jam operasional, musim dan cuaca, serta pertumbuhan bulanan.

## Setup Environment - Anaconda
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt

## Setup Environment - Shell/Terminal
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

## Run Streamlit App
streamlit run dashboard/dashboard.py