import os
from . import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp

class ResumeParser(object):
    def __init__(self, resume):
        nlp = spacy.load('en_core_web_trf')
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name'              : None,
            'email'             : None,
            'mobile_number'     : None,
            'skills'            : None,
            'education'         : None,
            'experience'        : None,
            'competencies'      : None,
            'measurable_results': None
        }
        self.__resume      = resume
        self.__text_raw    = utils.extract_text(self.__resume, os.path.splitext(self.__resume)[1])
        self.__text        = ' '.join(self.__text_raw.split())
        self.__nlp         = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        name       = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email      = utils.extract_email(self.__text)
        mobile     = utils.extract_mobile_number(self.__text)
        skills     = utils.extract_skills(self.__nlp, self.__noun_chunks)
        # edu        = utils.extract_education([sent.text_with_ws for sent in self.__nlp.sents])
        edu        = utils.extract_education(self.__text)
        experience = utils.extract_experience(self.__text)
        entities   = utils.extract_entity_sections(self.__text_raw)
        org_dict    =utils.extract_organisations_name(self.__nlp)
        self.__details['name'] = name
        self.__details['email'] = email
        self.__details['mobile_number'] = mobile
        self.__details['skills'] = skills
        # self.__details['education'] = entities['education']
        self.__details['education'] = edu
        self.__details['experience'] = experience
        self.__details['company_names']=org_dict['company']
        self.__details['college_name']=';\n'.join(org_dict['college'])
        try:
            self.__details['competencies'] = utils.extract_competencies(self.__text_raw, entities['experience'])
            self.__details['measurable_results'] = utils.extract_measurable_results(self.__text_raw, entities['experience'])
        except KeyError:
            self.__details['competencies'] = []
            self.__details['measurable_results'] = []
        return

def resume_result_wrapper(resume):
        parser = ResumeParser(resume)
        return parser.get_extracted_data()

if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [pool.apply_async(resume_result_wrapper, args=(x,)) for x in resumes]

    results = [p.get() for p in results]

    pprint.pprint(results)