# coding=utf-8
from trnltk.morphology.model import formatter

class LearnerView(object):
    def __init__(self):
        self._context = {}

    def get_template_context(self):
        return self._context

    def set_corpus_id(self, str_corpus_id):
        self._context['corpus_id'] = str_corpus_id

    def set_current_word(self, word):
        self._context['current_word_id'] = word['_id']
        self._context['current_surface'] = word['surface']
        self._context['current_index'] = word['index']

    def set_previous_nonparsed_word(self, previous_nonparsed_word):
        self._context['previous_nonparsed_word_id'] = previous_nonparsed_word['_id']

    def set_next_nonparsed_word(self, next_nonparsed_word):
        self._context['next_nonparsed_word_id'] = next_nonparsed_word['_id']

    def set_leading_words(self, leading_words):
        self._context['leading_words'] = [self._create_context_word_dict(word) for word in leading_words]

    def set_following_words(self, following_words):
        self._context['following_words'] = [self._create_context_word_dict(word) for word in following_words]

    def set_all_nonparsed_count(self, all_nonparsed_count):
        self._context['all_nonparsed_count'] = all_nonparsed_count

    def set_prior_nonparsed_count(self, prior_nonparsed_count):
        self._context['prior_nonparsed_count'] = prior_nonparsed_count

    def set_all_count(self, all_count):
        self._context['all_count'] = all_count

    def add_parse_result(self, uuid_for_parse_result, parse_result, likelihood_value, likelihood_percentage, likelihood_value_level):
        parse_result_containers = self._context.get('parse_results') or []

        parse_result_container = {
            'uuid' : uuid_for_parse_result,
            'formatted_parse_result' : formatter.format_morpheme_container_for_parseset(parse_result, add_space=True),
            'likelihood_value' : likelihood_value,
            'likelihood_percentage' : likelihood_percentage,
            'likelihood_value_color' : self._get_likelihood_value_color(likelihood_value_level),
            'likelihood_percentage_color' : self._get_likelihood_percentage_color(likelihood_percentage)
        }

        parse_result_containers.append(parse_result_container)

        self._context['parse_results'] = parse_result_containers

    def _create_context_word_dict(self, word):
        return {
            'id': word['_id'],
            'surface': word['surface'],
            'parsed': bool(word['parsed']),
            'parse_result': word.get('parse_result')}

    def _get_likelihood_value_color(self, likelihood_value):
        return "warning"
        #return self._likelihood_value_style_map(likelihood_level)     # TODO

    def _get_likelihood_percentage_color(self, likelihood_percentage):
        return "warning"
        #return self._likelihood_percentage_style_map(likelihood_percentage) # TODO
