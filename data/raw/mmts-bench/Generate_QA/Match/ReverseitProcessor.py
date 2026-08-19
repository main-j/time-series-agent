import pandas as pd
import ast

def process_csv_reverse(csv_file_path, output_path):
    df = pd.read_csv(csv_file_path)
    
    for index, row in df.iterrows():
        if pd.notna(row['value']):
            value = ast.literal_eval(row['value'])
            
            for i in range(1, min(5, len(value))):
                if value[i]:
                    value[i] = value[i][::-1]
            
            df.at[index, 'value'] = str(value)
    
    df.to_csv(output_path, index=False)
    print(f"Processing completed, results saved to: {output_path}")
    return df

if __name__ == "__main__":
    CSV_FILE_PATH = "your_input_file.csv"
    OUTPUT_PATH = "processed_output.csv"
    
    processed_df = process_csv_reverse(CSV_FILE_PATH, OUTPUT_PATH)