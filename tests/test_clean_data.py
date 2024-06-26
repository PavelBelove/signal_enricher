# tests/test_clean_data.py

import pytest
import pandas as pd
from modules.clean_data import clean_data

def test_clean_data(tmp_path):
    # Create a test DataFrame with more rows and diverse text data
    data = {
        'title': [
            'Test Title 1', 'Test Title 2', 'Test Title 1', 'Test Title 3', 'Test Title 4',
            'Unique Title 5', 'Unique Title 6', 'Unique Title 7', 'Unique Title 8', 'Unique Title 9',
            'Another Title 10', 'Another Title 11', 'Another Title 12', 'Another Title 13', 'Another Title 14'
        ],
        'description': [
            'Test content 1', 'Test content 2', 'Test content 3', 'Test content 4', 'Test content 5',
            'Unique content 6', 'Unique content 7', 'Unique content 8', 'Unique content 9', 'Unique content 10',
            'Another content 11', 'Another content 12', 'Another content 13', 'Another content 14', 'Another content 15'
        ]
    }
    df = pd.DataFrame(data)
    
    # Create input file in the temporary directory
    input_filename = tmp_path / "test_input.csv"
    df.to_csv(input_filename, index=False)
    
    # Define output file in the temporary directory
    output_filename = tmp_path / "test_output.csv"
    
    # Perform data cleaning with debug directory
    clean_data(input_filename, output_filename, similarity_threshold=70, debug_dir=tmp_path)
    
    # Check results
    df_cleaned = pd.read_csv(output_filename)
    
    assert len(df_cleaned) == 11
    assert 'Test Title 1' in df_cleaned['title'].values
    assert 'Test Title 2' in df_cleaned['title'].values
    assert 'Test Title 3' in df_cleaned['title'].values
    assert 'Test Title 4' in df_cleaned['title'].values
    assert 'Unique Title 5' in df_cleaned['title'].values
    assert 'Unique Title 6' in df_cleaned['title'].values
    assert 'Unique Title 7' in df_cleaned['title'].values
    assert 'Unique Title 8' in df_cleaned['title'].values
    assert 'Unique Title 9' in df_cleaned['title'].values
    assert 'Another Title 10' in df_cleaned['title'].values
    assert 'Another Title 11' in df_cleaned['title'].values
    assert 'Test content 1' in df_cleaned['description'].values
    assert 'Test content 2' in df_cleaned['description'].values
    assert 'Test content 3' in df_cleaned['description'].values
    assert 'Test content 4' in df_cleaned['description'].values
    assert 'Test content 5' in df_cleaned['description'].values
    assert 'Unique content 6' in df_cleaned['description'].values
    assert 'Unique content 7' in df_cleaned['description'].values
    assert 'Unique content 8' in df_cleaned['description'].values
    assert 'Unique content 9' in df_cleaned['description'].values
    assert 'Unique content 10' in df_cleaned['description'].values
    assert 'Another content 11' in df_cleaned['description'].values
    assert 'Another content 12' in df_cleaned['description'].values
    assert 'Another content 13' in df_cleaned['description'].values
    assert 'Another content 14' in df_cleaned['description'].values
    assert 'Another content 15' in df_cleaned['description'].values