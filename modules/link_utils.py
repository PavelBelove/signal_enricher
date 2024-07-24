from urllib.parse import urlparse, parse_qs

def is_linkedin_post_link(url):
    """Проверяет, является ли ссылка прямой ссылкой на пост в LinkedIn."""
    parsed_url = urlparse(url)
    if "linkedin" not in parsed_url.netloc:
        return False
    
    path_parts = parsed_url.path.split('/')
    
    # Проверяем, что URL содержит '/posts/' или '/pulse/'
    if '/posts/' in parsed_url.path or '/pulse/' in parsed_url.path:
        return True
    
    # Проверяем наличие идентификатора активности
    query_params = parse_qs(parsed_url.query)
    if 'activityId' in query_params:
        return True
    
    return False

def find_best_link(links):
    """Выбирает лучшую ссылку из списка найденных."""
    linkedin_links = [link for link in links if is_linkedin_post_link(link)]
    
    if linkedin_links:
        return linkedin_links[0]
    elif links:
        return links[0]
    else:
        return "N/A"