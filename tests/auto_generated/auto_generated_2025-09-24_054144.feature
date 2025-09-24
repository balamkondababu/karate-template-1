### karate-config.js Updates

To support the provided OpenAPI specification, we need to add the following test data variables to the existing `karate-config.js`:

```javascript
// Add these to your existing config object
testData: {
  validUserName: 'John Doe',
  validUserId: 1,
  validApplicationId: 1,
  invalidUserId: 99999,
  invalidApplicationId: 99999,
  emptyString: '',
  nullValue: null,
  boundaryNumber: 1000000
}
```

### Feature Files

Based on the provided OpenAPI specification, we will create the following feature files:

#### health-check.feature

This feature file is not explicitly mentioned in the specification, but it's a good practice to include a health check endpoint to verify the API is up and running.

```gherkin
Feature: Health Check

Background:
  * url baseUrl
  * configure headers = commonHeaders

Scenario: Health check
  Given path '/health'
  When method get
  Then status 200
  And match response == { status: 'OK' }
```

#### user-management.feature

This feature file will cover the user management endpoints.

```gherkin
Feature: User Management

Background:
  * url baseUrl
  * configure headers = commonHeaders
  * def testData = { 
    validUserName: '#(testData.validUserName)',
    validUserId: '#(testData.validUserId)',
    invalidUserId: '#(testData.invalidUserId)',
    emptyString: '#(testData.emptyString)',
    nullValue: '#(testData.nullValue)',
    boundaryNumber: '#(testData.boundaryNumber)'
  }

Scenario: Get list of users
  Given path '/users'
  When method get
  Then status 200
  And match response == '#[]'

Scenario: Create a new user
  Given path '/users'
  And request { name: '#(testData.validUserName)' }
  When method post
  Then status 201
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID
  Given path '/users/' + testData.validUserId
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by ID with invalid ID
  Given path '/users/' + testData.invalidUserId
  When method get
  Then status 404

Scenario: Get user by application ID
  Given path '/users/' + testData.validUserId + '/' + testData.validApplicationId
  When method get
  Then status 200
  And match response == { id: '#number', name: '#string' }

Scenario: Get user by application ID with invalid application ID
  Given path '/users/' + testData.validUserId + '/' + testData.invalidApplicationId
  When method get
  Then status 404

Scenario Outline: Create user with different parameters
  Given path '/users'
  And request { name: '<name>' }
  When method post
  Then status <status>
  And match response == <response>

  Examples:
    | name           | status | response                    |
    | validUserName  | 201    | { id: '#number', name: '#string' } |
    | emptyString    | 400    | { error: '#string' }          |
    | nullValue      | 400    | { error: '#string' }          |
    | boundaryNumber | 400    | { error: '#string' }          |
```

### Execution Commands

To execute the feature files, use the following commands:

* Single feature: `mvn test -Dkarate.options="classpath:user-management.feature"`
* Full suite: `mvn test -Dkarate.options="--tags ~@ignore"`
* With environment: `mvn test -Dkarate.env=test`

Note: The above commands assume that you have the Karate framework set up in your project and the `karate-config.js` file is properly configured.