import requests


class StatusCodeError(Exception):
    pass


def request_by_id(id_list, id_type='doi', mailto=None):
    """Get the data available in OpenAlex corresonpding to a list of 
    identifiers.

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
    StatusCodeError
        If a request got a response with status code different from 200.
    """
    data = []
    base_url = "http://api.openalex.org/works"
    for page_start in range(0, len(id_list), 50):
        page = id_list[page_start: page_start+50]

        # Set number of results to 50 instead of default 25.
        url = base_url + f"?filter={id_type}:{'|'.join(page)}&per-page=50"
        if mailto is not None:
            url += f"&mailto={mailto}"
        res = requests.get(url)

        if res.status_code == 200:
            data += res.json()['results']
        else:
            raise StatusCodeError(f"Error in request to Openalex."
                f"Status code: {res.status_code}. Message: {res.json()}"
            )
    return data
