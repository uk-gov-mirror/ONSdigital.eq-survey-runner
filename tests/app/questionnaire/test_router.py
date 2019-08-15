from flask import url_for

from app.data_model.list_store import ListStore
from app.data_model.progress_store import ProgressStore, CompletionStatus
from app.questionnaire.location import Location
from app.questionnaire.router import Router
from app.utilities.schema import load_schema_from_name
from tests.app.app_context_test_case import AppContextTestCase


class TestRouter(AppContextTestCase):
    def test_can_access_location(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        current_location = Location(section_id='default-section', block_id='name-block')
        routing_path = [
            Location(section_id='default-section', block_id='name-block'),
            Location(section_id='default-section', block_id='summary'),
        ]
        can_access_location = router.can_access_location(current_location, routing_path)

        self.assertTrue(can_access_location)

    def test_cant_access_location(self):
        schema = load_schema_from_name('test_repeating_sections_with_hub_and_spoke')

        list_store = ListStore(
            [
                {
                    'items': ['abc123', '123abc'],
                    'name': 'people',
                    'primary_person': 'abc123',
                }
            ]
        )

        router = Router(
            schema=schema, progress_store=ProgressStore, list_store=list_store
        )

        current_location = Location(
            section_id='personal-details-section',
            block_id='proxy',
            list_item_id='invalid-list-item-id',
        )
        routing_path = []
        can_access_location = router.can_access_location(current_location, routing_path)

        self.assertFalse(can_access_location)

    def test_cant_access_location_invalid_list_item_id(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        current_location = Location(section_id='default-section', block_id='name-block')
        routing_path = []
        can_access_location = router.can_access_location(current_location, routing_path)

        self.assertFalse(can_access_location)

    def test_cant_access_location_not_on_allowable_path(self):
        schema = load_schema_from_name('test_unit_patterns')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        current_location = Location(
            section_id='default-section', block_id='set-duration-units-block'
        )
        routing_path = [
            Location(section_id='default-section', block_id='set-length-units-block'),
            Location(section_id='default-section', block_id='set-duration-units-block'),
            Location(section_id='default-section', block_id='set-area-units-block'),
            Location(section_id='default-section', block_id='set-volume-units-block'),
            Location(section_id='default-section', block_id='summary'),
        ]
        can_access_location = router.can_access_location(current_location, routing_path)

        self.assertFalse(can_access_location)

    def test_next_location_url(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore(
            [
                {
                    'section_id': 'default-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {'section_id': 'default-section', 'block_id': 'name-block'}
                    ],
                }
            ]
        )

        router = Router(schema, progress_store)

        current_location = Location(section_id='default-section', block_id='name-block')
        routing_path = [
            Location(section_id='default-section', block_id='name-block'),
            Location(section_id='default-section', block_id='summary'),
        ]
        next_location = router.get_next_location_url(current_location, routing_path)
        expected_location = Location(
            section_id='default-section', block_id='summary'
        ).url()

        self.assertEqual(next_location, expected_location)

    def test_previous_location_url(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        current_location = Location(section_id='default-section', block_id='summary')
        routing_path = [
            Location(section_id='default-section', block_id='name-block'),
            Location(section_id='default-section', block_id='summary'),
        ]
        previous_location_url = router.get_previous_location_url(
            current_location, routing_path
        )
        expected_location_url = Location(
            section_id='default-section', block_id='name-block'
        ).url()

        self.assertEqual(previous_location_url, expected_location_url)

    def test_previous_location_with_hub_enabled(self):
        schema = load_schema_from_name('test_hub_and_spoke')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        current_location = Location(
            section_id='employment-section', block_id='employment-status'
        )
        routing_path = [
            Location(section_id='employment-section', block_id='employment-status'),
            Location(section_id='employment-section', block_id='employment-type'),
        ]
        previous_location_url = router.get_previous_location_url(
            current_location, routing_path
        )
        expected_location_url = url_for('questionnaire.get_questionnaire')

        self.assertEqual(previous_location_url, expected_location_url)

    def test_is_survey_not_complete(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore()
        router = Router(schema, progress_store)

        is_survey_complete = router.is_survey_complete()

        self.assertFalse(is_survey_complete)

    def test_is_survey_complete(self):
        schema = load_schema_from_name('test_textfield')
        progress_store = ProgressStore(
            [
                {
                    'section_id': 'default-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {'section_id': 'default-section', 'block_id': 'name-block'}
                    ],
                }
            ]
        )
        router = Router(schema, progress_store)

        is_survey_complete = router.is_survey_complete()

        self.assertTrue(is_survey_complete)

    def test_is_survey_not_complete_with_repeating_sections(self):
        schema = load_schema_from_name('test_repeating_sections_with_hub_and_spoke')

        progress_store = ProgressStore(
            [
                {
                    'section_id': 'default-section',
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'default-section',
                            'block_id': 'mandatory-checkbox',
                        },
                        {
                            'section_id': 'default-section',
                            'block_id': 'non-mandatory-checkbox',
                        },
                    ],
                }
            ]
        )

        list_store = ListStore(
            [
                {
                    'items': ['abc123', '123abc'],
                    'name': 'people',
                    'primary_person': 'abc123',
                }
            ]
        )

        router = Router(schema, progress_store, list_store)

        is_survey_complete = router.is_survey_complete()

        self.assertFalse(is_survey_complete)

    def test_is_survey_complete_with_repeating_sections(self):
        schema = load_schema_from_name('test_repeating_sections_with_hub_and_spoke')

        progress_store = ProgressStore(
            [
                {
                    'section_id': 'section',
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'section',
                            'block_id': 'primary-person-list-collector',
                        },
                        {'section_id': 'section', 'block_id': 'list-collector'},
                        {'section_id': 'section', 'block_id': 'next-interstitial'},
                        {
                            'section_id': 'section',
                            'block_id': 'another-list-collector-block',
                        },
                    ],
                },
                {
                    'section_id': 'personal-details-section',
                    'status': CompletionStatus.COMPLETED,
                    'list_item_id': 'abc123',
                    'locations': [
                        {
                            'section_id': 'personal-details-section',
                            'block_id': 'proxy',
                            'list_name': 'people',
                            'list_item_id': 'ZywslG',
                        },
                        {
                            'section_id': 'personal-details-section',
                            'block_id': 'date-of-birth',
                            'list_name': 'people',
                            'list_item_id': 'ZywslG',
                        },
                        {
                            'section_id': 'personal-details-section',
                            'block_id': 'confirm-dob',
                            'list_name': 'people',
                            'list_item_id': 'ZywslG',
                        },
                        {
                            'section_id': 'personal-details-section',
                            'block_id': 'sex',
                            'list_name': 'people',
                            'list_item_id': 'ZywslG',
                        },
                    ],
                },
            ]
        )

        list_store = ListStore(
            [{'items': ['abc123'], 'name': 'people', 'primary_person': 'abc123'}]
        )

        router = Router(schema, progress_store, list_store)

        is_survey_complete = router.is_survey_complete()

        self.assertTrue(is_survey_complete)

    def test_is_survey_complete_summary_in_own_section(self):
        schema = load_schema_from_name('test_placeholder_full')

        progress_store = ProgressStore(
            [
                {
                    'section_id': 'name-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {'section_id': 'name-section', 'block_id': 'name-question'}
                    ],
                },
                {
                    'section_id': 'age-input-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'age-input-section',
                            'block_id': 'dob-question-block',
                        }
                    ],
                },
                {
                    'section_id': 'age-confirmation-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'age-confirmation-section',
                            'block_id': 'confirm-dob-proxy',
                        }
                    ],
                },
            ]
        )
        router = Router(schema, progress_store)

        is_survey_complete = router.is_survey_complete()

        self.assertTrue(is_survey_complete)

    def test_get_first_incomplete_location_in_section(self):
        schema = load_schema_from_name('test_section_summary')

        progress_store = ProgressStore(
            [
                {
                    'section_id': 'property-details-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'property-details-section',
                            'block_id': 'insurance-type',
                        }
                    ],
                }
            ]
        )
        router = Router(schema, progress_store)

        section_routing_path = [
            Location(section_id='property-details-section', block_id='insurance-type'),
            Location(
                section_id='property-details-section', block_id='insurance-address'
            ),
        ]

        incomplete = router.get_first_incomplete_location_for_section(
            routing_path=section_routing_path, section_id='property-details-section'
        )

        self.assertEqual(
            incomplete,
            Location(
                section_id='property-details-section', block_id='insurance-address'
            ),
        )

    def test_get_last_complete_location_in_section(self):
        schema = load_schema_from_name('test_section_summary')

        progress_store = ProgressStore(
            [
                {
                    'section_id': 'property-details-section',
                    'list_item_id': None,
                    'status': CompletionStatus.COMPLETED,
                    'locations': [
                        {
                            'section_id': 'property-details-section',
                            'block_id': 'insurance-type',
                        }
                    ],
                }
            ]
        )
        router = Router(schema, progress_store)

        section_routing_path = [
            Location(section_id='property-details-section', block_id='insurance-type'),
            Location(
                section_id='property-details-section', block_id='insurance-address'
            ),
        ]

        last_complete_location = router.get_last_complete_location_for_section(
            routing_path=section_routing_path, section_id='property-details-section'
        )

        self.assertEqual(
            last_complete_location,
            Location(section_id='property-details-section', block_id='insurance-type'),
        )
