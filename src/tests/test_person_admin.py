import unittest


class TestPersonAdminForm(unittest.TestCase):
    def test_clean_inmate_number(self):
        # empty, required/not required
        pass

    def test_clean_name(self):
        pass


class TestPersonCreateForm(unittest.TestCase):
    def test_clean_on_create(self):
        pass


class TestPersonPrisonInline(unittest.TestCase):
    def test_inline(self):
        # ???
        pass


class TestPersonFilters(unittest.TestCase):
    def test_prison_list_filter(self):
        # ???
        pass

    def test_eligibility_list_filter(self):
        # ???
        pass


class TestPersonAdmin(unittest.TestCase):
    def test_last_served_date(self):
        pass

    def test_get_correct_form_and_fields(self):
        pass

    def test_get_current_prison(self):
        pass

    def test_get_pending_letter_count(self):
        pass

    def test_get_letter_count(self):
        pass

    def test_get_package_count(self):
        pass

    def test_save(self):
        pass
