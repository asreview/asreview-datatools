from asreviewcontrib.datatools.openalex import request_by_id


def test_request_by_id():
    doi_list = [
        "https://doi.org/10.1177/0340035205054883", 
        "https://doi.org/10.1007/978-3-642-02774-1_74"
    ]

    pmid_list = [
        "https://pubmed.ncbi.nlm.nih.gov/12092264",
        "https://pubmed.ncbi.nlm.nih.gov/19038157"
    ]

    mailto = "asreview@uu.nl"

    response = request_by_id(doi_list, id_type='doi', mailto=mailto)
    response_ids = set(data_dict['ids']['doi'] for data_dict in response)
    assert response_ids == set(doi_list)

    response = request_by_id(pmid_list, id_type='pmid', mailto=mailto)
    response_ids = set(data_dict['ids']['pmid'] for data_dict in response)
    assert response_ids == set(pmid_list)
