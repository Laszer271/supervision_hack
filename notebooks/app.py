import streamlit as st
import pandas as pd
import plotly.express as px
data = {
    'Name of bank': ['Bank A', 'Bank B', 'Bank C', 'Bank D', 'Bank E'],
    'Date': ['01-11-2023', '05-12-2023', '10-09-2023', '15-07-2023', '20-03-2023'],
    'Product Type': ['Savings', 'Checking', 'Term Deposit', 'Savings', 'Savings'],
    'Length/Maturity': ['1 year', 'Ongoing', '3 years', '30 years', '5 years'],
    'Interest Rate': [2.5, 1.8, 3.2, 4.0, 5.5],
    'Customer Type': ['Individual', 'Corporate', 'Individual', 'Individual', 'Corporate'],
    'Offer Type': ['Promotional', 'Standard', 'Standard', 'Promotional', 'Standard'],
    'Maximum Deposit Amount': [10000, 50000, 20000, 100000, 30000],
    'Other Significant Conditions': ['N/A', 'Minimum balance required', 'N/A', 'Insurance required', 'N/A']
}
df = pd.DataFrame(data)


def main():
    
    st.markdown("<h1 style='text-align: center; color: White;background-color:#e84343'>InterestGuardian</h1>", unsafe_allow_html=True)
    # st.markdown("<h3 style='text-align: center; color: Black;'>Drop in The required Inputs and we will do  the rest.</h3>", unsafe_allow_html=True)
    # st.markdown("<h4 style='text-align: center; color: Black;'>Submission for The Python Week</h4>",
    #             unsafe_allow_html=True)
    st.header("What is this Project about?")
    st.text("It a Web app that would help the Supervisors in determining\n whether bank is an outcast or not.")
    st.header("What tools where used to make this?")
    st.text("We used web scraping, AI and other cool stuff.")
    st.sidebar.header("FILTERS")

    # taking the cgpa by giving in the range from 0 to 10
    selected_banks = st.sidebar.multiselect("Filter by banks",df['Name of bank'].to_list(), df['Name of bank'].to_list())
    selected_interest_threshold = st.sidebar.slider("Input your interest threshold", 0, 20)
    # taking the TOEFL by giving in the range from 0 to 120
    selected_deposit_threshold = st.sidebar.slider("Input your maximum deposit value", 10000, 100000)
    # taking the input of whether or not a person has written a research paper

    c = dict(zip(df["Name of bank"].unique(), px.colors.qualitative.G10))


    filtered_df = df[df['Name of bank'].isin(selected_banks) & (df['Interest Rate'] >= selected_interest_threshold) & (df['Maximum Deposit Amount'] >= selected_deposit_threshold) & (df['Customer Type'] == 'Individual')]
    fig = px.bar(filtered_df, x="Interest Rate", y="Maximum Deposit Amount", color="Name of bank",color_discrete_map=c, title = 'Indiviudal clients')

    filtered_df = df[df['Name of bank'].isin(selected_banks) & (df['Interest Rate'] >= selected_interest_threshold) & (df['Maximum Deposit Amount'] >= selected_deposit_threshold) & (df['Customer Type'] == 'Corporate')]
    fig_2 = px.bar(filtered_df, x="Interest Rate", y="Maximum Deposit Amount", color="Name of bank",color_discrete_map=c, title = 'Corporate clients')
 

    # Plot!
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig_2, use_container_width=True)


        # if st.button('Predict'):  # making and printing our prediction
        #     pass
        #     # result = model.predict(inputs)
        #     # updated_res = result.flatten().astype(float)
        #     # st.success(
        #     #     'The Probability of getting admission is {}'.format(updated_res))


if __name__ == '__main__':
        main()
