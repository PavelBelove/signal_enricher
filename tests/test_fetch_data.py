# tests/test_fetch_data.py

import pytest
import requests
from modules.fetch_data import fetch_xmlstock_search_results, fetch_and_parse, save_results_to_csv

@pytest.fixture
def mock_xml_response():
    return """
    <response>
        <result>
            <group>
                <doc>
                    <title>Test Title</title>
                    <url>http://example.com/article</url>
                    <pubDate>2024-06-13</pubDate>
                </doc>
            </group>
        </result>
    </response>
    """

def test_fetch_xmlstock_search_results(requests_mock, mock_xml_response):
    url = "https://xmlstock.com/google/xml/"
    requests_mock.get(url, text=mock_xml_response)
    
    results = fetch_xmlstock_search_results("test query", days=30, num_results=1, num_pages=1, verbose=True)
    
    assert len(results) == 1
    assert results[0]['title'] == "Test Title"
    assert results[0]['link'] == "http://example.com/article"
    assert results[0]['pubDate'] == "2024-06-13"

def test_fetch_and_parse():
    url = "https://ru.wikipedia.org/wiki/42_(%D1%87%D0%B8%D1%81%D0%BB%D0%BE)"
    
    article_data = fetch_and_parse(url, verbose=True)
    
    assert article_data['title'] == "42 (число) — Википедия"
    assert "42" in article_data['text']
    assert article_data['article_url'] == url

def test_save_results_to_csv(tmp_path):
    results = [
        {'title': 'Test Title', 'link': 'http://example.com/article', 'pubDate': '2024-06-13', 'description': 'Test content', 'query': 'test query'}
    ]
    output_filename = tmp_path / "test_results.csv"
    
    save_results_to_csv(results, output_filename, verbose=True)
    
    with open(output_filename, 'r') as f:
        content = f.read()
    
    assert "Test Title" in content
    assert "http://example.com/article" in content
    assert "2024-06-13" in content
    assert "Test content" in content
    assert "test query" in content