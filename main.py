import pandas as pd

# Define a function to read the file and return a DataFrame
def load_csv_to_dataframe(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        return str(e)

def extract_date(df):
    """
    This function takes a DataFrame and extracts the first non-null date (YYYY-MM-DD) part
    from the '실제 시작 시간' column, returning it as a string.
    If there are no non-null dates, it returns None.
    """
    # Extract the date part and drop nulls, then get the first non-null value
    first_date = df['Unnamed: 3'].str.extract(r'(\d{4}\.\d{1,2}\.\d{1,2})')[0].dropna().iloc[0]
    first_date = first_date.replace('.', '_')
    return first_date


def set_header_after_quiz(df):
    """
    This function takes a DataFrame, searches for a row containing '주차 POP QUIZ'
    (where '주차' can be any number), and sets the row immediately following it as the new header.
    It then returns a new DataFrame starting from this new header and deletes all previous rows.
    """
    header_row_index = df[df.iloc[:, 0].str.contains(r'\d주차 POP QUIZ', na=False)].index[0] + 1
    new_header = df.iloc[header_row_index]
    df_with_new_header = df[header_row_index+1:].copy()
    df_with_new_header.columns = new_header.values
    df_with_new_header.reset_index(drop=True, inplace=True)
    
    return df_with_new_header

# Adjusting the function to handle submissions with answers in various formats, including multiple lines and separators
# Revised function to accurately count correct and incorrect answers based on the updated requirements
def evaluate_answers_final(df, correct_answers):
    answer_col = df.columns[df.columns.get_loc("제출 날짜 및 시간") + 1]

    def evaluate_submission(submission):
        # Splitting submission into individual answers, considering both "\n" and ";"
        submitted_answers = [ans.strip().lower() for part in submission.split("\n") for ans in part.split(";") if ans.strip()]
        
        # Initialize counts
        correct_count = 0
        incorrect_count = 0
        
        # Count correct and incorrect answers
        for ans in submitted_answers:
            if ans in correct_answers:
                correct_count += 1
            else:
                incorrect_count += 1
        
        # Determine the evaluation result
        if correct_count > 0 and incorrect_count > 0:
            result = "부분 정답"
        elif correct_count == 0:
            result = "오답"
        else:
            result = "정답"

        return result, correct_count, incorrect_count
    
    # Apply evaluation function to each row
    evaluation_results = df[answer_col].apply(lambda x: evaluate_submission(x if pd.notna(x) else ""))
    df["정답"], df["맞은 개수"], df["틀린 개수"] = zip(*evaluation_results)
    
    # Selecting relevant columns for the result
    result_df = df[["사용자 이름", "정답", "맞은 개수", "틀린 개수", answer_col]]
    result_df = result_df.rename(columns={str(answer_col): "제출 답안"})
    return result_df

import re
def split_df_based_on_username_enhanced(df):
    df['사용자 이름'] = df['사용자 이름'].str.replace(r'[^\w\s]', '', regex=True).str.replace(' ', '')

    # Enhanced function to check username criteria (either 10 digits followed by characters or characters followed by 10 digits)
    def is_valid_username(username):
        # Checks for either 10 digits followed by characters or characters followed by 10 digits
        return bool(re.match(r'(\d{10}\w+|\w+\d{10})', username))

    # Applying the function to identify valid and invalid usernames
    valid_usernames_mask = df['사용자 이름'].apply(is_valid_username)

    # Splitting the dataframe into valid and invalid based on the condition
    df_valid = df[valid_usernames_mask]
    df_invalid = df[~valid_usernames_mask]

    return df_valid, df_invalid

# Applying the enhanced function to the DataFrame
def rearrange_usernames(df):
    # Function to check and rearrange usernames from name-student number to student number-name
    def rearrange_username(username):
        # If the username starts with letters (name) followed by 10 digits (student number)
        if re.match(r'\D+\d{10}', username):
            name_part = re.search(r'\D+', username).group()
            number_part = re.search(r'\d{10}', username).group()
            return number_part + name_part  # Rearrange to student number-name format
        else:
            return username  # Return as is if already in the correct format or doesn't match the pattern

    df['사용자 이름'] = df['사용자 이름'].apply(rearrange_username)

    return df

def split_usernames_into_columns_final(df):
    # Adjusting the function to split '사용자 이름' into '학번' (10 digits) and '이름'
    def split_username_final(username):
        # Extracting the first 10 digits as student number and the rest as name
        student_number = username[:10]
        name = username[10:]
        return student_number, name

    # Applying the final split function
    df[['학번', '이름']] = df.apply(lambda row: split_username_final(row['사용자 이름']), axis=1, result_type='expand')

    # Placing '학번' and '이름' columns at the front
    cols = ['학번', '이름'] + [col for col in df.columns if col not in ['학번', '이름']]
    df = df[cols]

    return df

def save_dataframes_to_excel(processed_df, unprocessed_df, file_path):
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    
    # Write the "정상 처리 리스트" label
    processed_df_label = pd.DataFrame(['정상 처리 리스트'])
    processed_df_label.to_excel(writer, sheet_name='Sheet1', startrow=0, index=False, header=False)
    
    # Write the processed DataFrame to the Excel file
    processed_df.to_excel(writer, sheet_name='Sheet1', startrow=2, index=False)
    
    # Calculate the next start row: current DataFrame length + 4 for spacing and the label
    next_start_row = len(processed_df) + 4
    
    # Write the "미처리 리스트" label
    unprocessed_df_label = pd.DataFrame(['미처리 리스트'])
    unprocessed_df_label.to_excel(writer, sheet_name='Sheet1', startrow=next_start_row, index=False, header=False)
    
    # Write the unprocessed DataFrame to the Excel file, after skipping one row post label
    unprocessed_df.to_excel(writer, sheet_name='Sheet1', startrow=next_start_row + 2, index=False)
    
    # Close the Pandas Excel writer and output the Excel file
    writer.close()



def main(path, answers):
    df = load_csv_to_dataframe(path)
    # Apply the function to get the first date only as a string
    first_date_only = extract_date(df)
    df_new_header = set_header_after_quiz(df)
    evaluated_df = evaluate_answers_final(df_new_header, answers)

    df_valid_enhanced, df_invalid_enhanced = split_df_based_on_username_enhanced(evaluated_df)


    df_valid_rearranged = rearrange_usernames(df_valid_enhanced.copy())
    df_with_final_split_usernames = split_usernames_into_columns_final(df_valid_rearranged.copy())

    # Define the path where to save the Excel file
    file_path = './'+ first_date_only + '_QUIZ'+'.xlsx'

    # Apply the function to save both DataFrames to an Excel file
    save_dataframes_to_excel(df_with_final_split_usernames, df_invalid_enhanced, file_path)

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zoom Q&A (Quiz) Answer Processor")
    
    parser.add_argument('-p', '--path', type=str, help='Path to the csv file', default=None, required=True, metavar='path of csv file')
    
    # 정답 인자 추가 (nargs='+'를 사용하여 하나 이상의 정답을 받을 수 있도록 설정)
    parser.add_argument('-a', '--answer', type=str, nargs='+', help='answer list', required=True)
    
    # 파싱한 인자를 args에 저장
    args = parser.parse_args()
    # main 함수 호출
    main(args.path, args.answer)