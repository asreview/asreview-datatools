import requests


def request_by_id(id_list, id_type='doi', mailto=None):
    """Get metadata from OpenAlex for a list of identifiers.

    Parameters
    ----------
    id_list : list[str]
        List of identifiers
    id_type: str
        Type of the identifier (see 
        https://docs.openalex.org/about-the-data/work#ids), by default 'doi'
    mailto : str, optional
        Email address to add to the request, to end up in the polite pool
        (see https://docs.openalex.org/api#the-polite-pool), by default None

    Returns
    -------
    list[dict]
        List of OpenAlex data corresponding to the identifiers, 
        not necessarily in the same order as the input.

    Raises
    ------
    requests.HTTPError
        If a request got a HTTP error response.
    """
    data = []
    page_length = 50
    url = "http://api.openalex.org/works"
    for page_start in range(0, len(id_list), page_length):
        page = id_list[page_start: page_start+page_length]
        params = {
            "filter": f"{id_type}:{'|'.join(page)}",
            "per-page": page_length,
            "mailto": mailto
        }
        res = requests.get(url, params=params)
        res.raise_for_status()
        data += res.json()['results']

    return data
