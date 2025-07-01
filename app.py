import streamlit as st
import pandas as pd

# Load the CSV file
data = pd.read_csv("Used_Bikes.csv")

# Set Streamlit page configuration
st.set_page_config(page_title="Used Bike Price Predictor", layout="centered")

st.title("🏍️ Used Bike Price Prediction App")
st.markdown("Predict the resale price of a used bike based on model, city, power, usage and more!")

st.sidebar.header("🛠️ Enter Bike Details")

# Sidebar Inputs
brand = st.sidebar.selectbox("Select Bike Brand", sorted(data['brand'].unique()))
models_for_brand = data[data['brand'] == brand]['bike_name'].unique()
bike_model = st.sidebar.selectbox("Select Bike Model", sorted(models_for_brand))
city = st.sidebar.selectbox("Select City", sorted(data['city'].unique()))
owner = st.sidebar.selectbox("Select Owner Type", sorted(data['owner'].unique()))
kms_driven = st.sidebar.number_input("Kilometers Driven", min_value=0, value=10000, step=500)
age = st.sidebar.slider("Bike Age (Years)", min_value=0, max_value=20, value=3)
power = st.sidebar.slider("Engine Power (cc)", min_value=50, max_value=1500, value=150)
purchase_price = st.sidebar.number_input("Original Purchase Price (₹)", min_value=1000.0, value=40000.0)
brokerage_percentage = st.sidebar.slider("Brokerage Percentage (%)", min_value=0, max_value=20, value=5)

# Pricing logic
def calculate_predicted_price(purchase_price, city, owner, kms_driven, age, power):
    owner_multipliers = {"first": 1.0, "second": 0.95, "third": 0.90, "other": 0.85}
    owner_multiplier = owner_multipliers.get(owner.lower(), 0.85)

    high_value_cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"]
    city_multiplier = 1.05 if city in high_value_cities else 1.0

    depreciation = purchase_price * 0.08 * age
    usage_penalty = (kms_driven / 10000) * 3000
    power_bonus = power * 50

    predicted_price = (purchase_price * owner_multiplier * city_multiplier) - depreciation - usage_penalty + power_bonus
    return max(predicted_price, 5000)

# EMI Calculator
def calculate_emi(amount, months, interest=10.0):
    r = interest / (12 * 100)
    emi = (amount * r * (1 + r)**months) / ((1 + r)**months - 1)
    return emi

# Prediction Button
if st.sidebar.button("🔍 Predict Price"):
    if purchase_price > 0:
        predicted_price = calculate_predicted_price(purchase_price, city, owner, kms_driven, age, power)
        profit = predicted_price - purchase_price
        broker_profit = predicted_price * (brokerage_percentage / 100)

        # Deal Evaluation
        if profit > 15000:
            deal_status = "💰 Excellent Deal"
        elif profit > 5000:
            deal_status = "👍 Fair Deal"
        else:
            deal_status = "⚠️ Overpriced"

        # Display Summary
        st.subheader("📋 Bike Summary")
        st.markdown(f"""
        - **Brand**: {brand}  
        - **Model**: {bike_model}  
        - **City**: {city}  
        - **Owner**: {owner.title()}  
        - **KMs Driven**: {kms_driven} km  
        - **Age**: {age} years  
        - **Power**: {power} cc  
        """)

        # Result Display
        st.success(f"💸 **Predicted Resale Price**: ₹{predicted_price:,.2f}")
        st.info(f"📈 Buyer's Profit: ₹{profit:,.2f}")
        st.info(f"🤝 Broker's Profit: ₹{broker_profit:,.2f}")
        st.warning(f"📊 Deal Analysis: {deal_status}")

        # Bar Chart
        chart_data = pd.DataFrame({
            "Type": ["Original Price", "Predicted Price"],
            "Amount": [purchase_price, predicted_price]
        }).set_index("Type")
        st.subheader("📊 Price Comparison Chart")
        st.bar_chart(chart_data)

        # EMI Options
        if st.checkbox("💳 Show EMI Options"):
            st.subheader("💰 EMI Plans")
            for months in [6, 12, 18, 24]:
                emi_val = calculate_emi(predicted_price, months)
                st.write(f"{months} months: ₹{emi_val:.2f}/month")

        # Optional Broker Card
        with st.expander("📇 Add Broker Info"):
            broker_name = st.text_input("Broker Name")
            broker_phone = st.text_input("Broker Contact Number")
            if broker_name and broker_phone:
                st.success(f"📞 {broker_name} | 📱 {broker_phone} | 💼 Earns ₹{broker_profit:.2f}")

    else:
        st.warning("⚠️ Please enter a valid purchase price.")

# Sample Data
if st.checkbox("📄 Show Sample Bike Data"):
    st.dataframe(data.head())
