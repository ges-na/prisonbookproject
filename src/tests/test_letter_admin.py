import unittest


class TestLetterAdmin(unittest.TestCase):
    def test_create_letter_minimal_good(self):
        pass

    def test_create_letter_all_fields_good(self):
        pass

    def test_create_letter_without_person(self):
        pass

    def test_get_letter_name(self):
        pass

    def test_get_person_current_prison(self):
        # has prison
        # no prison
        pass

    def test_get_restrictions(self):
        pass

    def test_move_to_stage1_complete(self):
        pass

    def test_mark_letters_fulfilled_good(self):
        pass

    def test_mark_letters_fulfilled_failure_no_person(self):
        pass

    def test_mark_letters_discarded_good(self):
        pass

    def test_mark_letters_discarded_failure_fulfilled(self):
        pass

    def get_prison_mailing_address(self):
        # without additional_mailing_headers
        # with additional_mailing_headers
        pass

    def test_save(self):
        # no pk
        # has pk
        pass
