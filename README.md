# ⚡ Smart Grid Stability Analyzer

## 📌 Problem Statement

Renewable energy sources like solar and wind are intermittent in nature. Solar energy is available only during daytime, while wind energy is unpredictable. This leads to fluctuations in power generation, causing imbalance between supply and demand and resulting in grid instability.

---

## 💡 Solution

This project analyzes the impact of a solar-wind hybrid system on grid stability. By combining both energy sources, the system evaluates whether the total generated power can meet demand and determines the stability of the grid.

---

## 🚀 Features

* Real-time simulation of solar and wind energy
* Grid stability detection (Stable / Unstable)
* Stability score calculation
* Simple and interactive user interface
* Optional real-time weather data integration

---

## 🛠️ Tech Stack

* HTML
* CSS
* JavaScript / Streamlit (Python)
* OpenWeather API (for real-time data)

---

## ▶️ How to Run the Project

### For Web Version:

1. Open `index.html` in your browser

### For Streamlit Version:

1. Install dependencies
2. Run the command:

   ```bash
   streamlit run app.py
   ```

---

## 📊 Working Logic

* Total Power = Solar Power + Wind Power
* If Total Power ≥ Demand → ✅ Grid is Stable
* If Total Power < Demand → ❌ Grid is Unstable

---

## 📸 Demo Screenshot

(Add your screenshot file in the project folder and name it `screenshot.png`)

![App Screenshot](screenshot.png)

---

## 🌍 Future Scope

* Integration with real-time smart grid systems
* AI-based prediction of energy demand
* Multi-city energy monitoring
* Mobile application development

---

## 🏁 Conclusion

Hybrid renewable energy systems provide better stability compared to individual sources. This project demonstrates how combining solar and wind energy can improve reliability and ensure consistent power supply.

---

## 🙌 Acknowledgement

Developed as part of a hackathon project to explore innovative solutions in renewable energy and smart grid systems.
