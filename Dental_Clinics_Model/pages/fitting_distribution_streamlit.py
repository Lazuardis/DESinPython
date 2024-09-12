import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitting_distribution import process_interarrival_times, fit_distribution_interarrival  
import requests

def app():
    st.title("Input Processing and Fitting")
    

    # File uploader to upload the CSV file
    uploaded_file = st.file_uploader("Upload CSV with Arrival Times", type="csv")

    if uploaded_file is not None:
        # Read the CSV file
        arrival_times = pd.read_csv(uploaded_file)
        
        # Process the inter-arrival times
        inter_arrival_times = process_interarrival_times(arrival_times)
        
        # Display the processed inter-arrival times DataFrame
        st.markdown("### Inter-Arrival Times")
        st.dataframe(inter_arrival_times)

        # Display histogram of inter-arrival times
        st.markdown("### Histogram of Inter-Arrival Times")
        plt.figure(figsize=(10, 6))
        sns.histplot(inter_arrival_times['Inter-Arrival Time (Minutes)'], kde=True)
        plt.xlabel("Inter-Arrival Time (Minutes)")
        plt.ylabel("Frequency")
        plt.title("Histogram of Inter-Arrival Times")
        st.pyplot(plt)
        
        input_settings = st.selectbox("Input Settings", ("Use this Schedule", "Fit into Distribution"))
        
        if input_settings == "Fit into Distribution":

            # Fit distribution to the inter-arrival times
            Interarrival_distribution = fit_distribution_interarrival(inter_arrival_times)
            
            # Display the best-fit distribution
            st.markdown("### Best-Fit Inter-Arrival Distribution")
            st.write(Interarrival_distribution)
            
            if st.button('Save and Use Distribution Data'):
            # POST the interarrival_distribution to the Flask server
                response = requests.post(
                    'http://127.0.0.1:5000/set_distribution', 
                    # 'https://db1a-35-202-194-168.ngrok-free.app/set_distribution',
                    json={'interarrival_distribution': Interarrival_distribution}
                )
                
                if response.status_code == 200:
                    st.success("Distribution successfully sent to the server!")
                else:
                    st.error("Failed to send distribution to the server.")
                    
        elif input_settings == "Use this Schedule":
            
            inter_arrival_times_list = inter_arrival_times.iloc[:, 0].tolist()
            
            if st.button('Set Schedule'):
                # POST the interarrival_distribution to the Flask server
                response = requests.post(
                    'http://127.0.0.1:5000/set_arrival_schedule',
                    json={'arrival_schedule': inter_arrival_times_list}
                )
                if response.status_code == 200:
                    st.success("Schedule sent to the server!")
                else:
                    st.error("Failed to send Schedule to the server.")
                    
                    
                    
    else:
        
        st.divider()
        
        st.markdown("### Define the Inter-arrival times Manually")
        
        rate = st.number_input("Inter-Arrival Time Mean (Minutes)", value=5, step=1)
        st.caption('Distribution used: Exponential. If mean equal to 5, it means one customer arrive every 5 minutes')
        
        interarrival_distribution = f"random.expovariate({1/rate})"
        
        if st.button('Save and Use Distribution Data'):
        # POST the interarrival_distribution to the Flask server
            response = requests.post(
                'http://127.0.0.1:5000/set_distribution', 
                # 'https://db1a-35-202-194-168.ngrok-free.app/set_distribution',
                json={'interarrival_distribution': interarrival_distribution}
            )
        
            if response.status_code == 200:
                st.success("Distribution successfully sent to the server!")
            else:
                st.error("Failed to send distribution to the server.")       
                        


    #streamlit run fitting_distribution_streamlit.py --server.enableXsrfProtection false