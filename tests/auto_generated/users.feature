Feature: User Management

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { name: 'John Doe' }

Scenario: Get list of users - returns 200
  Given path 'users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Get list of users - empty list
  Given path 'users'
  When method get
  Then status 200
  And match response == '[]'

Scenario: Get user by ID - returns 200
  Given path 'users/1'
  When method get
  Then status 200
  And match response contains { id: '#number', name: '#string' }

Scenario: Get user by ID - invalid ID
  Given path 'users/abc'
  When method get
  Then status 404

Scenario: Get user by ID - missing ID
  Given path 'users/'
  When method get
  Then status 404

Scenario Outline: Get user by ID - boundary values
  Given path 'users/<id>'
  When method get
  Then status <status>

  Examples:
    | id | status |
    | 0  | 200    |
    | -1 | 404    |

Scenario: Create a new user - returns 201
  Given path 'users'
  And request { name: '#(testData.name)' }
  When method post
  Then status 201
  And match response contains { id: '#number', name: '#string' }

Scenario: Create a new user - missing name
  Given path 'users'
  And request {}
  When method post
  Then status 400

Scenario: Create a new user - invalid name
  Given path 'users'
  And request { name: 123 }
  When method post
  Then status 400

Scenario Outline: Create a new user - boundary values
  Given path 'users'
  And request { name: '<name>' }
  When method post
  Then status <status>

  Examples:
    | name      | status |
    |           | 400    |
    | a         | 201    |
    | a         | 201    |

Feature: Application Management

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { aname: 'Test App' }

Scenario: Get list of applications - returns 200
  Given path 'applications'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Get list of applications - empty list
  Given path 'applications'
  When method get
  Then status 200
  And match response == '[]'

Scenario: Get application by ID - returns 200
  Given path 'applications/1'
  When method get
  Then status 200
  And match response contains { aid: '#number', aname: '#string' }

Scenario: Get application by ID - invalid ID
  Given path 'applications/abc'
  When method get
  Then status 404

Scenario: Get application by ID - missing ID
  Given path 'applications/'
  When method get
  Then status 404

Scenario Outline: Get application by ID - boundary values
  Given path 'applications/<id>'
  When method get
  Then status <status>

  Examples:
    | id | status |
    | 0  | 200    |
    | -1 | 404    |

Scenario: Create a new application - returns 201
  Given path 'applications'
  And request { aname: '#(testData.aname)' }
  When method post
  Then status 201
  And match response contains { aid: '#number', aname: '#string' }

Scenario: Create a new application - missing aname
  Given path 'applications'
  And request {}
  When method post
  Then status 400

Scenario: Create a new application - invalid aname
  Given path 'applications'
  And request { aname: 123 }
  When method post
  Then status 400

Scenario Outline: Create a new application - boundary values
  Given path 'applications'
  And request { aname: '<aname>' }
  When method post
  Then status <status>

  Examples:
    | aname      | status |
    |           | 400    |
    | a         | 201    |
    | a         | 201    |