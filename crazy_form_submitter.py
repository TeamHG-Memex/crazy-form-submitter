from lxml import html
from lxml.html import InputElement, tostring
import string
from scrapy.http import FormRequest, TextResponse
from urlparse import urlparse
from urlparse import urljoin

class CrazyFormSubmitter():

    def __init__(self, search_terms = None):

        if not search_terms:
            self.search_terms = list(string.ascii_lowercase) + [" ", "*" , "%", ".", "?"]

    def normalize_link(self, url_to_normalize, current_page_url):

        #not quite, doesn't include path in normalization, gets paths wrong

        cp_scheme, cp_netloc, cp_path, cp_params, cp_query, cp_fragment = urlparse(current_page_url)

        parsed_url_to_normalize = urlparse(url_to_normalize)
        scheme, netloc, path, params, query, fragment = urlparse(url_to_normalize)

        if not parsed_url_to_normalize.scheme or not parsed_url_to_normalize.netloc:
            full_url = urljoin(current_page_url, url_to_normalize)
        else:
            full_url = url_to_normalize

        return full_url

    def __fill_form(self, url, form, text_input_value):
        for _input in form.inputs:
            if isinstance(_input, InputElement) and _input.type.lower() == "text":
                _input.value = text_input_value

        full_action_url = self.normalize_link(form.action, url)

        formdata = {}
        for key_val in form.form_values():
            name, value = key_val
            formdata[name] = value

        return form.method, formdata
    
    def generate_form_requests(self, url, content, **kwargs):

        doc = html.fromstring(content)
        for form in doc.forms:

            for search_term in self.search_terms:

                form_method, formdata = self.__fill_form(url, form, search_term)
                yield FormRequest(url = url, formdata = formdata, method = form_method, **kwargs)

    def generate_form_requests_from_response(self, response, **kwargs):

        url = response.url
        content = response.body

        doc = html.fromstring(content)
        for form in doc.forms:
            for search_term in self.search_terms:
                #find input boxes and fill them out
                form_method, formdata = self.__fill_form(url, form, search_term)
    
                yield FormRequest.from_response(response, formdata = formdata, method = form_method, **kwargs)

if __name__ == "__main__":

    import requests
    r = requests.get("http://stackoverflow.com/questions/11208239/scrapy-xpath-query-to-select-input-tag-elementsbounty")
    cfs = CrazyFormSubmitter()
    #for fr in cfs.generate_form_requests(r.url, r.text):
    #   print fr.__dict__
        
    response = TextResponse(url = u"http://stackoverflow.com/questions/11208239/scrapy-xpath-query-to-select-input-tag-elementsbounty", encoding = "utf-8", body = r.text)
    for fr in cfs.generate_form_requests_from_response(response):
        print fr.__dict__
