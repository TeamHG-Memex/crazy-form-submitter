from lxml import html
from lxml.html import InputElement, HTMLParser
import string
from scrapy.http import FormRequest
from scrapy.http.request.form import _get_inputs as get_form_data
from scrapy.selector.lxmldocument import LxmlDocument

class CrazyFormSubmitter:

    def __init__(self, search_terms=None):

        if not search_terms:
            self.search_terms = list(string.ascii_lowercase) + [" ", "*", "%", ".", "?"]

    def _fill_form(self, form, text_input_value):

        additional_formdata = {}
        for _input in form.inputs:
            if isinstance(_input, InputElement) and _input.type.lower() == "text":
                additional_formdata[_input.name] = text_input_value

        return form.method, get_form_data(form, additional_formdata, None, None, None)

    def generate_form_requests(self, url, content, **kwargs):

        doc = html.fromstring(content)
        for form in doc.forms:

            for search_term in self.search_terms:
                form_method, formdata = self._fill_form(form, search_term)
                yield FormRequest(url=url, formdata=formdata, method=form_method, **kwargs)

    def generate_form_requests_from_response(self, response, **kwargs):

        doc = LxmlDocument(response, HTMLParser)

        for form in doc.forms:
            for search_term in self.search_terms:
                #find input boxes and fill them out
                form_method, formdata = self._fill_form(form, search_term)

                yield FormRequest.from_response(response, formdata=formdata, method=form_method, **kwargs)

if __name__ == "__main__":

    import requests
    url = "http://stackoverflow.com/questions/11208239/scrapy-xpath-query-to-select-input-tag-elementsbounty"
    r = requests.get(url)
    cfs = CrazyFormSubmitter()
        
    from scrapy.http import TextResponse        
    response = TextResponse(url=url, encoding="utf-8", body=r.text)
    for fr in cfs.generate_form_requests_from_response(response):
        print(fr.__dict__)
