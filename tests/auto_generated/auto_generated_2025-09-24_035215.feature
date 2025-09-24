Feature: Test new endpoints

Scenario: Get user by ID
* def auth = 'auth placeholder'
* url 'https://example.com/users/1'
* header Authorization = auth
* get
* match responseStatus == '#[200,299]'
* match response ==
"""
{
  "id": '#number',
  "name": '#string'
}
"""

Scenario: Get user by application ID
* def auth = 'auth placeholder'
* url 'https://example.com/users/1/1'
* header Authorization = auth
* get
* match responseStatus == '#[200,299]'
* match response ==
"""
{
  "id": '#number',
  "name": '#string'
}
"""