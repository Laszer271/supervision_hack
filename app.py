import streamlit as st
import pandas as pd
import plotly.express as px

def main():

    path = "results.csv"
    df = pd.pandas.read_csv(path)
    
    df['HighestInterest'] = df['HighestInterest'].abs()
    df['Length'] = df['Length'].abs()
    df['Length'] = df['Length'].apply(lambda x: x if x <= 36 else 36)
    df['MaxPLN'] = df['MaxPLN'].apply(lambda x: x if x >= 10000 else 1000)
    
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
    selected_banks = st.sidebar.multiselect("Filter by banks",df['Bank'].unique().tolist(), df['Bank'].unique().tolist())
    selected_interest_threshold = st.sidebar.slider("Input your interest threshold", 0, 15)
    # taking the TOEFL by giving in the range from 0 to 120
    selected_deposit_threshold = st.sidebar.slider("Input your minimum deposit value", 1, 100000)
    # taking the input of whether or not a person has written a research paper

    c = dict(zip(df["Bank"].unique(), px.colors.qualitative.G10))


    filtered_df = df[df['Bank'].isin(selected_banks) & (df['HighestInterest'] >= selected_interest_threshold) & (df['MaxPLN'] >= selected_deposit_threshold) & (df['Client type'] == 'Individual')]
    
    fig = px.bar(filtered_df, x="HighestInterest", y="MaxPLN", color="Bank",color_discrete_map=c, title = 'Indiviudal clients')

    filtered_df = df[df['Bank'].isin(selected_banks) & (df['HighestInterest'] >= selected_interest_threshold) & (df['MaxPLN'] >= selected_deposit_threshold) & (df['Client type'] == 'Corporation')]

    fig_2 = px.bar(filtered_df, x="HighestInterest", y="MaxPLN", color="Bank",color_discrete_map=c, title = 'Corporation ')

    fig_3 = px.bar(filtered_df, x='Bank', y="HighestInterest", color="Bank",color_discrete_map=c, title = 'Interest Rate')
 

    # Plot!
    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig_2, use_container_width=True)
    st.plotly_chart(fig_3, use_container_width=True)


        # if st.button('Predict'):  # making and printing our prediction
        #     pass
        #     # result = model.predict(inputs)
        #     # updated_res = result.flatten().astype(float)
        #     # st.success(
        #     #     'The Probability of getting admission is {}'.format(updated_res))


if __name__ == '__main__':
        main()
