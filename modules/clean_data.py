import pandas as pd
from fuzzywuzzy import fuzz

def clean_data(input_filename, output_filename, similarity_threshold=70, verbose=False):
    """
    Clean data by removing strict and non-strict duplicates.

    Args:
        input_filename (str): Path to the input CSV file.
        output_filename (str): Path to the output CSV file.
        similarity_threshold (int): Similarity threshold for fuzzy matching (default is 70).
        verbose (bool): Flag to enable/disable verbose output.

    Returns:
        None
    """
    if verbose:
        print(f"Loading data from file {input_filename}...")
    df = pd.read_csv(input_filename)

    # Stage 1: "Strict" comparison and removal of exact duplicates
    if verbose:
        print("Removing strict duplicates...")
    df_no_strict_duplicates = df.drop_duplicates(subset=['title', 'description']).reset_index(drop=True)
    if verbose:
        print(f"Strict duplicates removed: {len(df) - len(df_no_strict_duplicates)}")

    # Stage 2: Preparation for "non-strict" comparison
    if verbose:
        print("Preparing data for 'non-strict' comparison...")
    df_no_strict_duplicates_sorted = df_no_strict_duplicates.sort_values('title').reset_index()

    # List of row indices to remove
    indexes_to_remove = set()

    if verbose:
        print("Searching for duplicates with 'non-strict' comparison...")
    # Use fuzzy matching algorithm to find duplicates
    for i in range(len(df_no_strict_duplicates_sorted) - 1):
        for j in range(i + 1, len(df_no_strict_duplicates_sorted)):
            # Use fuzz.token_sort_ratio to compare strings
            similarity_title = fuzz.token_sort_ratio(df_no_strict_duplicates_sorted.loc[i, 'title'], df_no_strict_duplicates_sorted.loc[j, 'title'])
            similarity_text = fuzz.token_sort_ratio(df_no_strict_duplicates_sorted.loc[i, 'description'], df_no_strict_duplicates_sorted.loc[j, 'description'])

            if similarity_title > similarity_threshold or similarity_text > similarity_threshold:
                indexes_to_remove.add(df_no_strict_duplicates_sorted.loc[j, 'index'])  # Add index to set for removal
                if verbose:
                    print(f"Duplicate found: row {i + 1} and row {j + 1}")
                    print(f"Title similarity: {similarity_title}, Text similarity: {similarity_text}")

    # Remove duplicates found in the 'non-strict' comparison stage
    df_final = df_no_strict_duplicates_sorted.drop(df_no_strict_duplicates_sorted[df_no_strict_duplicates_sorted['index'].isin(indexes_to_remove)].index).reset_index(drop=True)

    if verbose:
        print("Saving data...")
    # Save cleaned data back to CSV
    df_final.to_csv(output_filename, index=False)

    # Output information about the number of removed and remaining rows
    if verbose:
        print(f"Rows removed in 'non-strict' comparison stage: {len(indexes_to_remove)}")
        print(f"Remaining rows after cleaning: {len(df_final)}")
        print(f"Data cleaned and saved to '{output_filename}'.")

if __name__ == "__main__":
    # Example usage
    input_filename = 'results/example_client/2024-06-13/search_results.csv'
    output_filename = 'results/example_client/2024-06-13/search_results_cleaned.csv'
    clean_data(input_filename, output_filename, verbose=True)