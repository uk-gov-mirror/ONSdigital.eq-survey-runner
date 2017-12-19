import unittest

from app.helpers.form_helper import get_mapped_answers, get_form_for_location, post_form_for_location
from app.helpers.schema_helper import SchemaHelper
from app.questionnaire.location import Location
from app.utilities.schema import load_schema_file
from app.data_model.answer_store import AnswerStore, Answer
from app.validation.validators import DateRequired, OptionalForm

from werkzeug.datastructures import MultiDict

from tests.app.app_context_test_case import AppContextTestCase


class TestFormHelper(AppContextTestCase):

    def test_get_form_for_block_location(self):
        with self.test_request_context():
            survey = load_schema_file('test_0102.json')

            block_json = SchemaHelper.get_block(survey, 'reporting-period')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location, AnswerStore(), error_messages)

            self.assertTrue(hasattr(form, 'period-to'))
            self.assertTrue(hasattr(form, 'period-from'))

            period_from_field = getattr(form, 'period-from')
            period_to_field = getattr(form, 'period-to')

            self.assertIsInstance(period_from_field.month.validators[0], DateRequired)
            self.assertIsInstance(period_to_field.month.validators[0], DateRequired)

    def test_get_form_and_disable_mandatory_answers(self):
        with self.test_request_context():
            survey = load_schema_file('test_0102.json')

            block_json = SchemaHelper.get_block(survey, 'reporting-period')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location,
                                            AnswerStore(), error_messages, disable_mandatory=True)

            self.assertTrue(hasattr(form, 'period-from'))
            self.assertTrue(hasattr(form, 'period-to'))

            period_from_field = getattr(form, 'period-from')
            period_to_field = getattr(form, 'period-to')

            self.assertIsInstance(period_from_field.month.validators[0], OptionalForm)
            self.assertIsInstance(period_to_field.month.validators[0], OptionalForm)

    def test_get_form_deserialises_dates(self):
        with self.test_request_context():
            survey = load_schema_file('test_0102.json')

            block_json = SchemaHelper.get_block(survey, 'reporting-period')
            location = Location('rsi', 0, 'reporting-period')
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location, AnswerStore([
                {
                    'answer_id': 'period-from',
                    'group_id': 'rsi',
                    'group_instance': 0,
                    'block_id': 'reporting-period',
                    'value': '2015-05-01',
                    'answer_instance': 0,
                }, {
                    'answer_id': 'period-to',
                    'group_id': 'rsi',
                    'group_instance': 0,
                    'block_id': 'reporting-period',
                    'value': '2017-09-01',
                    'answer_instance': 0,
                }
            ]), error_messages)

            self.assertTrue(hasattr(form, 'period-to'))
            self.assertTrue(hasattr(form, 'period-from'))

            period_to_field = getattr(form, 'period-to')
            period_from_field = getattr(form, 'period-from')

            self.assertEqual(period_from_field.data, {
                'day': '01',
                'month': '5',
                'year': '2015',
            })
            self.assertEqual(period_to_field.data, {
                'day': '01',
                'month': '9',
                'year': '2017',
            })

    def test_get_form_deserialises_month_year_dates(self):
        with self.test_request_context():
            survey = load_schema_file('test_dates.json')

            block_json = SchemaHelper.get_block(survey, 'date-block')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location, AnswerStore([
                {
                    'answer_id': 'month-year-answer',
                    'group_id': 'dates',
                    'group_instance': 0,
                    'block_id': 'date-block',
                    'value': '2015-05-01',
                    'answer_instance': 0,
                }
            ]), error_messages)

            self.assertTrue(hasattr(form, 'month-year-answer'))

            month_year_field = getattr(form, 'month-year-answer')

            self.assertEqual(month_year_field.data, {
                'month': '5',
                'year': '2015',
            })

    def test_get_form_deserialises_lists(self):
        with self.test_request_context():
            survey = load_schema_file('test_checkbox.json')

            block_json = SchemaHelper.get_block(survey, 'mandatory-checkbox')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location, AnswerStore([
                {
                    'answer_id': 'mandatory-checkbox-answer',
                    'group_id': 'checkboxes',
                    'group_instance': 0,
                    'block_id': 'mandatory-checkbox',
                    'value': ['Cheese', 'Ham'],
                    'answer_instance': 0,
                }
            ]), error_messages)

            self.assertTrue(hasattr(form, 'mandatory-checkbox-answer'))

            checkbox_field = getattr(form, 'mandatory-checkbox-answer')

            self.assertEqual(checkbox_field.data, ['Cheese', 'Ham'])

    def test_post_form_for_block_location(self):
        with self.test_request_context():
            survey = load_schema_file('test_0102.json')

            block_json = SchemaHelper.get_block(survey, 'reporting-period')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = post_form_for_location(block_json, location, AnswerStore(survey), {
                'period-from-day': '1',
                'period-from-month': '05',
                'period-from-year': '2015',
                'period-to-day': '1',
                'period-to-month': '09',
                'period-to-year': '2017',
            }, error_messages)

            self.assertTrue(hasattr(form, 'period-to'))
            self.assertTrue(hasattr(form, 'period-from'))

            period_to_field = getattr(form, 'period-to')
            period_from_field = getattr(form, 'period-from')

            self.assertIsInstance(period_from_field.month.validators[0], DateRequired)
            self.assertIsInstance(period_to_field.month.validators[0], DateRequired)

            self.assertEqual(period_from_field.data, {
                'day': '1',
                'month': '05',
                'year': '2015',
            })
            self.assertEqual(period_to_field.data, {
                'day': '1',
                'month': '09',
                'year': '2017',
            })

    def test_post_form_and_disable_mandatory(self):
        with self.test_request_context():
            survey = load_schema_file('test_0102.json')

            block_json = SchemaHelper.get_block(survey, 'reporting-period')
            location = SchemaHelper.get_first_location(survey)
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = post_form_for_location(block_json, location, AnswerStore(survey), {
            }, error_messages, disable_mandatory=True)

            self.assertTrue(hasattr(form, 'period-from'))
            self.assertTrue(hasattr(form, 'period-to'))

            period_from_field = getattr(form, 'period-from')
            period_to_field = getattr(form, 'period-to')

            self.assertIsInstance(period_from_field.month.validators[0], OptionalForm)
            self.assertIsInstance(period_to_field.month.validators[0], OptionalForm)

    def test_get_form_for_household_composition(self):
        with self.test_request_context():
            survey = load_schema_file('census_household.json')

            block_json = SchemaHelper.get_block(survey, 'household-composition')
            location = Location('who-lives-here', 0, 'household-composition')
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = get_form_for_location(block_json, location, AnswerStore(), error_messages)

            self.assertTrue(hasattr(form, 'household'))
            self.assertEqual(len(form.household.entries), 1)

            first_field_entry = form.household[0]

            self.assertTrue(hasattr(first_field_entry, 'first-name'))
            self.assertTrue(hasattr(first_field_entry, 'middle-names'))
            self.assertTrue(hasattr(first_field_entry, 'last-name'))

    def test_post_form_for_household_composition(self):
        with self.test_request_context():
            survey = load_schema_file('census_household.json')

            block_json = SchemaHelper.get_block(survey, 'household-composition')
            location = Location('who-lives-here', 0, 'household-composition')
            error_messages = SchemaHelper.get_messages(survey)

            form, _ = post_form_for_location(block_json, location, AnswerStore(survey), {
                'household-0-first-name': 'Joe',
                'household-0-last-name': '',
                'household-1-first-name': 'Bob',
                'household-1-last-name': 'Seymour',
            }, error_messages)

            self.assertEqual(len(form.household.entries), 2)
            self.assertEqual(form.household.entries[0].data, {
                'first-name': 'Joe',
                'middle-names': '',
                'last-name': ''
            })
            self.assertEqual(form.household.entries[1].data, {
                'first-name': 'Bob',
                'middle-names': '',
                'last-name': 'Seymour'
            })

    def test_get_form_for_household_relationship(self):
        with self.test_request_context():
            survey = load_schema_file('census_household.json')

            block_json = SchemaHelper.get_block(survey, 'household-relationships')
            location = Location('who-lives-here-relationship', 0, 'household-relationships')
            error_messages = SchemaHelper.get_messages(survey)

            answer_store = AnswerStore([
                {
                    'group_id': 'who-lives-here-relationship',
                    'group_instance': 0,
                    'answer_id': 'first-name',
                    'block_id': 'household-composition',
                    'value': 'Joe',
                    'answer_instance': 0,
                }, {
                    'group_id': 'who-lives-here-relationship',
                    'group_instance': 0,
                    'answer_id': 'last-name',
                    'block_id': 'household-composition',
                    'value': 'Bloggs',
                    'answer_instance': 0,
                }, {
                    'group_id': 'who-lives-here-relationship',
                    'group_instance': 1,
                    'answer_id': 'first-name',
                    'block_id': 'household-composition',
                    'value': 'Jane',
                    'answer_instance': 1,
                }, {
                    'group_id': 'who-lives-here-relationship',
                    'group_instance': 1,
                    'answer_id': 'last-name',
                    'block_id': 'household-composition',
                    'value': 'Bloggs',
                    'answer_instance': 1,
                }
            ])
            form, _ = get_form_for_location(block_json, location, answer_store, error_messages)

            answer = SchemaHelper.get_first_answer_for_block(block_json)

            self.assertTrue(hasattr(form, answer['id']))

            field_list = getattr(form, answer['id'])

            # With two people, we need to define 1 relationship
            self.assertEqual(len(field_list.entries), 1)

    def test_post_form_for_household_relationship(self):
        with self.test_request_context():
            survey = load_schema_file('census_household.json')

            block_json = SchemaHelper.get_block(survey, 'household-relationships')
            location = Location('who-lives-here-relationship', 0, 'household-relationships')
            error_messages = SchemaHelper.get_messages(survey)

            answer_store = AnswerStore([
                {
                    'answer_id': 'first-name',
                    'block_id': 'household-composition',
                    'value': 'Joe',
                    'answer_instance': 0,
                }, {
                    'answer_id': 'last-name',
                    'block_id': 'household-composition',
                    'value': 'Bloggs',
                    'answer_instance': 0,
                }, {
                    'answer_id': 'first-name',
                    'block_id': 'household-composition',
                    'value': 'Jane',
                    'answer_instance': 1,
                }, {
                    'answer_id': 'last-name',
                    'block_id': 'household-composition',
                    'value': 'Bloggs',
                    'answer_instance': 1,
                }
            ])

            answer = SchemaHelper.get_first_answer_for_block(block_json)

            form, _ = post_form_for_location(block_json, location, answer_store, MultiDict({
                '{answer_id}-0'.format(answer_id=answer['id']): '3'
            }), error_messages)

            self.assertTrue(hasattr(form, answer['id']))

            field_list = getattr(form, answer['id'])

            # With two people, we need to define 1 relationship
            self.assertEqual(len(field_list.entries), 1)

            # Check the data matches what was passed from request
            self.assertEqual(field_list.entries[0].data, '3')

    def test_post_form_for_radio_other_not_selected(self):
        with self.test_request_context():
            survey = load_schema_file('test_radio_mandatory_with_mandatory_other.json')

            block_json = SchemaHelper.get_block(survey, 'radio-mandatory')
            location = Location('radio', 0, 'radio-mandatory')
            error_messages = SchemaHelper.get_messages(survey)

            answer_store = AnswerStore([
                {
                    'answer_id': 'radio-mandatory-answer',
                    'block_id': 'radio-mandatory',
                    'value': 'Other',
                    'answer_instance': 0,
                },
                {
                    'answer_id': 'other-answer-mandatory',
                    'block_id': 'radio-mandatory',
                    'value': 'Other text field value',
                    'answer_instance': 0,
                }
            ])

            answer = SchemaHelper.get_first_answer_for_block(block_json)

            form, _ = post_form_for_location(block_json, location, answer_store, MultiDict({
                '{answer_id}'.format(answer_id=answer['id']): 'Bacon',
                'other-answer-mandatory': 'Old other text'
            }), error_messages)

            self.assertTrue(hasattr(form, answer['id']))

            other_text_field = getattr(form, 'other-answer-mandatory')
            self.assertEqual(other_text_field.data, '')

    def test_post_form_for_radio_other_selected(self):
        with self.test_request_context():
            survey = load_schema_file('test_radio_mandatory_with_mandatory_other.json')

            block_json = SchemaHelper.get_block(survey, 'radio-mandatory')
            location = Location('radio', 0, 'radio-mandatory')
            error_messages = SchemaHelper.get_messages(survey)

            answer_store = AnswerStore([
                {
                    'answer_id': 'radio-mandatory-answer',
                    'block_id': 'radio-mandatory',
                    'value': 'Other',
                    'answer_instance': 0,
                },
                {
                    'answer_id': 'other-answer-mandatory',
                    'block_id': 'block-1',
                    'value': 'Other text field value',
                    'answer_instance': 0,
                }
            ])

            radio_answer = SchemaHelper.get_first_answer_for_block(block_json)
            text_answer = 'other-answer-mandatory'

            form, _ = post_form_for_location(block_json, location, answer_store, MultiDict({
                '{answer_id}'.format(answer_id=radio_answer['id']): 'Other',
                '{answer_id}'.format(answer_id=text_answer): 'Other text field value',
            }), error_messages)

            other_text_field = getattr(form, 'other-answer-mandatory')
            self.assertEqual(other_text_field.data, 'Other text field value')


class TestGetMappedAnswers(unittest.TestCase):

    def setUp(self):
        self.store = AnswerStore(None)

    def tearDown(self):
        self.store.clear()

    def test_maps_answers(self):
        answer_1 = Answer(
            block_id='1',
            answer_id='2',
            answer_instance=1,
            group_id='5',
            group_instance=1,
            value=25,
        )
        answer_2 = Answer(
            block_id='1',
            answer_id='5',
            answer_instance=1,
            group_id='6',
            group_instance=1,
            value=65,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)

        expected_answers = {
            '2_1': 25,
            '5_1': 65
        }

        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_maps_and_filters_answers(self):
        answer_1 = Answer(
            block_id='1',
            answer_id='2',
            answer_instance=1,
            group_id='5',
            group_instance=1,
            value=25,
        )
        answer_2 = Answer(
            block_id='1',
            answer_id='5',
            answer_instance=1,
            group_id='6',
            group_instance=1,
            value=65,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)

        expected_answers = {
            '5_1': 65
        }

        self.assertEqual(get_mapped_answers(self.store, answer_id='5'), expected_answers)

    def test_returns_ordered_map(self):
        answer = Answer(
            block_id='1',
            answer_id='2',
            group_id='5',
            group_instance=1,
            value=25,
        )

        for i in range(0, 100):
            answer.answer_instance = i

            self.store.add(answer)

        last_instance = -1

        self.assertEqual(len(self.store.answers), 100)

        mapped = get_mapped_answers(self.store)

        for key, _ in mapped.items():
            pos = key.find('_')

            instance = 0 if pos == -1 else int(key[pos + 1:])

            self.assertGreater(instance, last_instance)

            last_instance = instance

    def test_remove_single_answer_by_group_id(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group2',
            block_id='block1',
            answer_id='answer2',
            value=20,
        )
        answer_3 = Answer(
            group_id='group3',
            block_id='block1',
            answer_id='answer3',
            value=30,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)
        self.store.add(answer_3)

        self.store.remove(group_id='group1')
        expected_answers = {
            'answer2': 20,
            'answer3': 30
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_multiple_answers_by_group_id(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group2',
            block_id='block1',
            answer_id='answer2',
            value=20,
        )
        answer_3 = Answer(
            group_id='group2',
            block_id='block1',
            answer_id='answer3',
            value=30,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)
        self.store.add(answer_3)

        self.store.remove(group_id='group2')
        expected_answers = {
            'answer1': 10,
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_single_answer_by_block_id(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            block_id='block2',
            answer_id='answer2',
            value=20,
        )
        answer_3 = Answer(
            group_id='group1',
            block_id='block3',
            answer_id='answer3',
            value=30,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)
        self.store.add(answer_3)

        self.store.remove(block_id='block1')
        expected_answers = {
            'answer2': 20,
            'answer3': 30
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_multiple_answers_by_block_id(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            block_id='block2',
            answer_id='answer2',
            value=20,
        )
        answer_3 = Answer(
            group_id='group1',
            block_id='block2',
            answer_id='answer3',
            value=30,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)
        self.store.add(answer_3)

        self.store.remove(block_id='block2')
        expected_answers = {
            'answer1': 10,
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_multiple_answers_by_location(self):
        answer_1 = Answer(
            group_id='group1',
            group_instance=0,
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            group_instance=0,
            block_id='block1',
            answer_id='answer2',
            value=20,
        )
        answer_3 = Answer(
            group_id='group1',
            group_instance=0,
            block_id='block2',
            answer_id='answer3',
            value=30,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)
        self.store.add(answer_3)

        location = Location('group1', 0, 'block1')

        self.store.remove_by_location(location=location)

        expected_answers = {
            'answer3': 30,
        }

        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_answers_by_group_id_that_does_not_exist(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            block_id='block2',
            answer_id='answer2',
            value=20,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)

        self.store.remove(group_id='group2')
        expected_answers = {
            'answer1': 10,
            'answer2': 20
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_answers_by_block_id_that_does_not_exist(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer2',
            value=20,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)

        self.store.remove(block_id='block2')
        expected_answers = {
            'answer1': 10,
            'answer2': 20
        }
        self.assertEqual(get_mapped_answers(self.store), expected_answers)

    def test_remove_all_answers(self):
        answer_1 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer1',
            value=10,
        )
        answer_2 = Answer(
            group_id='group1',
            block_id='block1',
            answer_id='answer2',
            value=20,
        )

        self.store.add(answer_1)
        self.store.add(answer_2)

        self.store.remove()
        self.assertEqual(get_mapped_answers(self.store), {})
