import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# Initialize OpenAI client
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI User Story Generator")

# Upload file
uploaded_file = st.file_uploader("Upload your Feature List", type=["xlsx"])

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    st.write("Preview of uploaded data:")
    st.dataframe(df)

    # Button to trigger AI
    if st.button("Generate User Stories"):

        results = []

        with st.spinner("Generating user stories..."):

            for index, row in df.iterrows():

                feature = str(row["Feature Name"]).strip()
                feature_description = str(row["Feature Description"]).strip()

                # Prompt
                prompt = f"""
                You are a Business Analyst.

                Convert the following feature into a user story and acceptance criteria.

                Feature: {feature}
                Description: {feature_description}

                Return STRICTLY in this format:

                User Story:
                As a <user>, I want <goal> so that <benefit>.

                Acceptance Criteria:
                1. <criteria 1>
                2. <criteria 2>
                3. <criteria 3>

                Do NOT add extra text.
                """

                # AI call
                response = client.responses.create(
                    model="gpt-5-mini",
                    input=prompt
                )

                output = response.output_text

                # --- Parsing logic ---
                user_story = ""
                acceptance_criteria = ""

                output_lower = output.lower()

                if "acceptance criteria" in output_lower:

                    split_index = output_lower.find("acceptance criteria")

                    user_story = output[:split_index].replace("User Story", "").replace(":", "").strip()

                    acceptance_criteria = output[split_index:].replace("Acceptance Criteria", "").replace(":", "").replace("(single)", "").strip()

                else:
                    user_story = output.strip()

                # Store results
                results.append({
                    "Feature": feature,
                    "User Story": user_story,
                    "Acceptance Criteria": acceptance_criteria
                })

        # Convert to DataFrame
        output_df = pd.DataFrame(results)

        st.success("User stories generated successfully!")

        st.write("Generated Output:")
        st.dataframe(output_df)

        # Download button
        st.download_button(
            label="Download Results",
            data=output_df.to_csv(index=False),
            file_name="user_stories.csv",
            mime="text/csv"
        )
