Feature: Application Management

Background:
  * url 'https://example.com'
  * configure headers = { Content-Type: 'application/json' }
  * def testData = { aname: 'Test Application' }

Scenario: Get list of applications - returns 200
  Given path 'applications'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Get list of applications with invalid header - returns 400
  Given path 'applications'
  And header Content-Type = 'text/plain'
  When method get
  Then status 400

Scenario Outline: Get application by ID - returns 200
  Given path 'applications/<aid>'
  When method get
  Then status 200
  And match response contains { aid: '#number', aname: '#string' }

  Examples:
    | aid |
    | 1   |
    | 2   |

Scenario: Get application by ID with invalid ID - returns 404
  Given path 'applications/abc'
  When method get
  Then status 404

Scenario: Get application by ID with missing ID - returns 400
  Given path 'applications/'
  When method get
  Then status 400

Scenario: Create a new application - returns 201
  Given path 'applications'
  And request { aname: '#(testData.aname)' }
  When method post
  Then status 201
  And match response contains { aid: '#number', aname: '#string' }

Scenario: Create a new application with missing name - returns 400
  Given path 'applications'
  And request { }
  When method post
  Then status 400

Scenario: Create a new application with invalid name - returns 400
  Given path 'applications'
  And request { aname: 123 }
  When method post
  Then status 400

Feature: Error Handling

Scenario: Get list of applications with invalid authentication - returns 401
  Given path 'applications'
  And header Authorization = 'Invalid Token'
  When method get
  Then status 401

Scenario: Get application by ID with invalid authentication - returns 401
  Given path 'applications/1'
  And header Authorization = 'Invalid Token'
  When method get
  Then status 401

Scenario: Create a new application with invalid authentication - returns 401
  Given path 'applications'
  And header Authorization = 'Invalid Token'
  And request { aname: '#(testData.aname)' }
  When method post
  Then status 401