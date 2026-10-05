from apps.location.models import Location
from core.abstract.tests import AbstractTest, generate_name


class TestLocation(AbstractTest):
    """Location related tests"""

    path = 'location'

    parameters = {
        'description': f'Test Location description fake {generate_name()}'
    }
