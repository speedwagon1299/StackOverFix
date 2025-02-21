# Configuration for each library's documentation site

SITE_CONFIG = {
    1: {
        "name": "NumPy",
        "base_url": "https://numpy.org/doc/2.2/reference/",
        "content_selector": {"name": "article", "attrs": {}},
        "valid_link_prefix": "https://numpy.org/doc/2.2/reference/",
        "content_tags": ['h1', 'h2', 'h3', 'p', 'pre', 'code', 'li', 'dt', 'dd'],
        "exclude_selectors": [{'name': 'div', 'attrs': {'class': 'sphinxsidebar'}}]
    },
    2: {
        "name": "Pandas",
        "base_url": "https://pandas.pydata.org/docs/reference/index.html",
        "content_selector": {"name": "article", "attrs": {}},
        "valid_link_prefix": "https://pandas.pydata.org/docs/reference/",
        "content_tags": ['h1', 'h2', 'h3', 'p', 'pre', 'code', 'li', 'dt', 'dd'],
        "exclude_selectors": [{'name': 'div', 'attrs': {'class': 'sphinxsidebar'}}]
    },
    3: {
        "name": "Scikit-learn",
        "base_url": "https://scikit-learn.org/stable/api/",
        "content_selector": {"name": "article", "attrs": {}},
        "valid_link_prefix": "https://scikit-learn.org/stable/api/",
        "content_tags": ['h1', 'h2', 'h3', 'p', 'pre', 'code', 'li', 'dt', 'dd'],
        "exclude_selectors": [{'name': 'div', 'attrs': {'class': 'sphinxsidebar'}}]
    },
    4: {
        "name": "TensorFlow",
        "base_url": "https://www.tensorflow.org/api_docs/python/",
        "content_selector": {"name": "div", "attrs": {"class": "devsite-article-body"}},
        "valid_link_prefix": "https://www.tensorflow.org/api_docs/python/"
    },
    5: {
        "name": "PyTorch",
        "base_url": "https://pytorch.org/docs/stable/index.html",
        "content_selector": {"name": "div", "attrs": {"role": "main"}},
        "valid_link_prefix": "https://pytorch.org/docs/stable/"
    }
}
