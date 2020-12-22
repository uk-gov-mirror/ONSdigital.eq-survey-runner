import unittest
import json
import snappy

from jwcrypto import jwe
from jwcrypto.common import base64url_encode

from app.data_model.app_models import QuestionnaireState
from app.data_model.questionnaire_store import QuestionnaireStore
from app.storage import data_access
from app.storage.encrypted_questionnaire_storage import EncryptedQuestionnaireStorage
from app.storage.storage_encryption import StorageEncryption
from tests.app.app_context_test_case import AppContextTestCase


def _save_state_data(user_id, data, state_version=QuestionnaireStore.LATEST_VERSION):
    json_data = json.loads(data)

    json_metadata = json_data['METADATA']
    collection_exercise_id = json_metadata['collection_exercise_sid']
    form_type = json_metadata['form_type']
    eq_id = json_metadata['eq_id']
    ru_ref = json_metadata['ru_ref']

    encryption = StorageEncryption(user_id, 'mock', 'mock')

    state_data = encryption.encrypt_data(data)

    questionnaire_state = QuestionnaireState(
        user_id,
        state_data,
        state_version,
        collection_exercise_id,
        form_type,
        eq_id,
        ru_ref
    )
    data_access.put(questionnaire_state)


class TestEncryptedQuestionnaireStorage(AppContextTestCase):

    def setUp(self):
        super().setUp()
        self.storage = EncryptedQuestionnaireStorage('user_id', 'user_ik', 'pepper')

    def test_encrypted_storage_requires_user_id(self):
        with self.assertRaises(ValueError):
            EncryptedQuestionnaireStorage(None, 'key', 'pepper')

    def test_encrypted_storage_requires_user_ik(self):
        with self.assertRaises(ValueError):
            EncryptedQuestionnaireStorage('1', None, 'pepper')

    def test_store_and_get(self):
        user_id = '1'
        user_ik = '2'
        encrypted = EncryptedQuestionnaireStorage(user_id, user_ik, 'pepper')
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        encrypted.add_or_update(json_data, QuestionnaireStore.LATEST_VERSION)
        # check we can decrypt the data
        self.assertEqual((json_data, QuestionnaireStore.LATEST_VERSION), encrypted.get_user_data())

    def test_store(self):
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        self.assertIsNone(self.storage.add_or_update(json_data, QuestionnaireStore.LATEST_VERSION))
        self.assertIsNotNone(self.storage.get_user_data())  # pylint: disable=protected-access

    def test_get(self):
        mock_data = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_mock_data = json.dumps(mock_data)

        self.storage.add_or_update(json_mock_data, QuestionnaireStore.LATEST_VERSION)

        user_data_from_storage = self.storage.get_user_data()
        data_version_from_user = user_data_from_storage[1]
        data_from_user = json.loads(user_data_from_storage[0])

        self.assertEqual(mock_data, data_from_user)
        self.assertEqual(QuestionnaireStore.LATEST_VERSION, data_version_from_user)

    def test_delete(self):
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        self.storage.add_or_update(json_data, QuestionnaireStore.LATEST_VERSION)
        self.assertEqual((json_data, QuestionnaireStore.LATEST_VERSION), self.storage.get_user_data())
        self.storage.delete()
        self.assertEqual((None, None), self.storage.get_user_data())  # pylint: disable=protected-access


class TestEncryptedQuestionnaireStorageEncoding(AppContextTestCase):
    """Compression didn't used to be applied to the questionnaire store data. It also
    used to be base64-encoded. For performance reasons the base64 encoding is being
    removed and compression applied using the snappy lib
    """
    LEGACY_DATA_STORE_VERSION = 2

    def setUp(self):
        super().setUp()
        self.user_id = 'user_id'
        self.storage = EncryptedQuestionnaireStorage(self.user_id, 'user_ik', 'pepper')

    def test_legacy_get(self):
        """Tests that the legacy data is correctly decrypted
        """
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        self._save_legacy_state_data(self.user_id, json_data)
        self.assertEqual((json_data, self.LEGACY_DATA_STORE_VERSION), self.storage.get_user_data())

    def test_legacy_migrated_to_latest(self):
        """Tests that the legacy data is correctly saved as latest
        """
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        self._save_legacy_state_data(self.user_id, json_data)
        self.storage.add_or_update(json_data, QuestionnaireStore.LATEST_VERSION)
        self.assertEqual((json_data, QuestionnaireStore.LATEST_VERSION), self.storage.get_user_data())

    def test_newer_data_saved_as_current_latest_version(self):
        """
        If we encounter data newer than we can write, it should be written with the latest version
        that this application version can write.
        e.g. we can read version 3, but can only write version 2. Data should be saved as version 2.
        """
        mockData = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mockData)
        current_version = QuestionnaireStore.LATEST_VERSION
        newer_version = current_version + 1
        _save_state_data(self.user_id, json_data, state_version=newer_version)
        self.storage.add_or_update(json_data, current_version)
        self.assertEqual((json_data, current_version), self.storage.get_user_data())

    def test_get(self):
        """Tests compressed state
        """
        mock_data = {'METADATA': {
            'collection_exercise_sid': '123',
            'form_type': '456',
            'ru_ref': '789',
            'eq_id': 'survey_456',
        }}
        json_data = json.dumps(mock_data)

        self._save_compressed_state_data(self.user_id, json_data)

        user_data_from_storage = self.storage.get_user_data()
        data_version_from_user = user_data_from_storage[1]
        data_from_user = json.loads(user_data_from_storage[0])

        self.assertEqual(mock_data, data_from_user)
        self.assertEqual(QuestionnaireStore.LATEST_VERSION + 1, data_version_from_user)

    def _save_legacy_state_data(self, user_id, data):
        json_data = json.loads(data)

        json_metadata = json_data['METADATA']
        collection_exercise_id = json_metadata['collection_exercise_sid']
        form_type = json_metadata['form_type']
        eq_id = json_metadata['eq_id']
        ru_ref = json_metadata['ru_ref']

        protected_header = {
            'alg': 'dir',
            'enc': 'A256GCM',
            'kid': '1,1',
        }

        jwe_token = jwe.JWE(
            plaintext=base64url_encode(data),
            protected=protected_header,
            recipient=self.storage.encrypter.key
        )

        legacy_state_data = json.dumps({'data': jwe_token.serialize(compact=True)})

        questionnaire_state = QuestionnaireState(
            user_id,
            legacy_state_data,
            self.LEGACY_DATA_STORE_VERSION,
            collection_exercise_id,
            form_type,
            ru_ref,
            eq_id,
        )
        data_access.put(questionnaire_state)

    def _save_compressed_state_data(self, user_id, data):
        json_data = json.loads(data)

        json_metadata = json_data['METADATA']
        collection_exercise_id = json_metadata['collection_exercise_sid']
        form_type = json_metadata['form_type']
        eq_id = json_metadata['eq_id']
        ru_ref = json_metadata['ru_ref']

        protected_header = {
            'alg': 'dir',
            'enc': 'A256GCM',
            'kid': '1,1',
        }

        jwe_token = jwe.JWE(
            plaintext=snappy.compress(data),
            protected=protected_header,
            recipient=self.storage.encrypter.key
        )

        state_data = jwe_token.serialize(compact=True)

        questionnaire_state = QuestionnaireState(
            user_id,
            state_data,
            QuestionnaireStore.LATEST_VERSION + 1,
            collection_exercise_id,
            form_type,
            ru_ref,
            eq_id,
        )
        data_access.put(questionnaire_state)


if __name__ == '__main__':
    unittest.main()
